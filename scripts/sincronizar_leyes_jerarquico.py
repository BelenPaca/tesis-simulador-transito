import os
import sys
import time
import re
import hashlib
import uuid
import psycopg2
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from google import genai
from google.genai import types

# -------------------------------------------------------------
# 1. Configuración y Claves (leídas desde entorno o .env)
# -------------------------------------------------------------
import dotenv
dotenv.load_dotenv()

raw_keys = os.getenv("GEMINI_API_KEYS", os.getenv("GEMINI_API_KEY", ""))
API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]
if not API_KEYS:
    # Clave de respaldo desde variables de entorno
    API_KEYS = [os.getenv("GEMINI_API_KEY", "")]

QDRANT_URL = os.getenv("QDRANT_URL", "https://45f892c8-83a3-41bd-980c-3239d456cfb1.us-west-2-0.aws.cloud.qdrant.io:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "springrag")
NEON_DB_URL = os.getenv("NEON_DB_URL", "")

print("=" * 70)
print("🚀 INICIANDO INGESTA JERÁRQUICA RAG PURA EN QDRANT CLOUD")
print("=" * 70)

# Inicializar clientes Gemini con rotación
gemini_clients = [genai.Client(api_key=k) for k in API_KEYS]
current_key_idx = 0

def get_next_gemini_client():
    global current_key_idx
    client = gemini_clients[current_key_idx]
    current_key_idx = (current_key_idx + 1) % len(gemini_clients)
    return client

# Conectar Qdrant
print(f"🔌 Conectando a Qdrant Cloud ({QDRANT_COLLECTION})...")
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
expected_dim = 3072

# Conectar Neon
print("🔌 Conectando a Neon PostgreSQL...")
conn = psycopg2.connect(NEON_DB_URL)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS registro_leyes (
        nombre_archivo VARCHAR(255) PRIMARY KEY,
        hash_archivo VARCHAR(64) NOT NULL,
        total_fragmentos INT NOT NULL,
        fecha_procesado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
conn.commit()

# Limpiar registro_leyes solo si se pasa --force-all
if "--force-all" in sys.argv:
    cursor.execute("TRUNCATE TABLE registro_leyes;")
    conn.commit()
    print("✅ Tabla 'registro_leyes' reseteada para ingesta forzada completa.")
else:
    print("✅ Modo incremental activo: archivos ya completados se omitirán.")

def obtener_hash_guardado(nombre_archivo):
    try:
        c = psycopg2.connect(NEON_DB_URL)
        cur = c.cursor()
        cur.execute("SELECT hash_archivo FROM registro_leyes WHERE nombre_archivo = %s;", (nombre_archivo,))
        row = cur.fetchone()
        cur.close()
        c.close()
        return row[0] if row else None
    except Exception as e:
        print(f"  ⚠️ Error al leer hash en Neon: {e}")
        return None

def guardar_en_neon(nombre_archivo, hash_archivo, total_fragmentos):
    try:
        c = psycopg2.connect(NEON_DB_URL)
        cur = c.cursor()
        cur.execute("""
            INSERT INTO registro_leyes (nombre_archivo, hash_archivo, total_fragmentos, fecha_procesado)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (nombre_archivo) 
            DO UPDATE SET hash_archivo = EXCLUDED.hash_archivo, total_fragmentos = EXCLUDED.total_fragmentos;
        """, (nombre_archivo, hash_archivo, total_fragmentos))
        c.commit()
        cur.close()
        c.close()
    except Exception as e:
        print(f"  ⚠️ Error al guardar registro en Neon: {e}")

# -------------------------------------------------------------
# 2. Chunking Jerárquico Padre-Hijo en Origen
# -------------------------------------------------------------
def dividir_en_fragmentos_jerarquicos(seccion, max_len=1500):
    """
    Divide un artículo legal asegurando que TODO fragmento derivado
    conserve el encabezado con el número de artículo, título y sanción,
    y que NINGÚN fragmento supere jamás max_len (evita desbordar la ventana de embedding).
    """
    if len(seccion) <= max_len:
        return [seccion]

    # Extraer encabezado introductorio sancionatorio (hasta antes del primer numeral 1.)
    m = re.search(r'(?m)^\s*1[\.\-]\s+', seccion)
    if m:
        header = seccion[:m.start()].strip()
        body = seccion[m.start():].strip()
    else:
        parts = seccion.split('\n\n', 1)
        header = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else ''

    if not body:
        header = seccion[:200].strip()
        body = seccion

    if len(header) > 300:
        header = header[:300].strip()

    # Dividir el cuerpo respetando numerales o párrafos
    patron_items = re.compile(r'(?m)^(?=\d+[\.\-]\s+)')
    raw_items = [it.strip() for it in patron_items.split(body) if it.strip()]
    if not raw_items:
        raw_items = [p.strip() for p in body.split('\n\n') if p.strip()]

    # Garantizar que ningún item individual exceda max_len
    items = []
    for it in raw_items:
        if len(it) <= max_len:
            items.append(it)
        else:
            for sub_i in range(0, len(it), max_len - 150):
                items.append(it[sub_i:sub_i + max_len])

    chunks = []
    current_chunk = header + "\n\n"
    for item in items:
        if len(current_chunk) + len(item) + 2 <= max_len:
            current_chunk += item + "\n\n"
        else:
            if current_chunk.strip() and current_chunk.strip() != header:
                chunks.append(current_chunk.strip()[:max_len])
            current_chunk = header + "\n[Continuación...]\n" + item + "\n\n"

    if current_chunk.strip() and current_chunk.strip() != header:
        chunks.append(current_chunk.strip()[:max_len])

    return chunks

def procesar_archivo_normativo(contenido):
    texto = contenido.replace('\r\n', '\n').replace('\r', '\n')
    secciones = [s.strip() for s in re.split(r'\n(?=#{1,4}\s*(?:Art(?:ículo|\.)?|Capítulo|Título|SECCIÓN)\b)', texto, flags=re.IGNORECASE) if s.strip()]
    
    chunks_finales = []
    for sec in secciones:
        if len(sec) < 15:
            continue
        sub_chunks = dividir_en_fragmentos_jerarquicos(sec)
        chunks_finales.extend(sub_chunks)
    
    return chunks_finales

# -------------------------------------------------------------
# 3. Vectorización con Rotación de Claves
# -------------------------------------------------------------
def generar_embeddings_lote(textos, dim_esperada=3072, max_retries=10):
    config_dict = {"output_dimensionality": dim_esperada}
    
    for attempt in range(max_retries):
        client = get_next_gemini_client()
        try:
            response = client.models.embed_content(
                model="gemini-embedding-001",
                contents=textos,
                config=types.EmbedContentConfig(**config_dict)
            )
            return [e.values for e in response.embeddings]
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                wait_time = (attempt + 1) * 8
                print(f"\n    ⏳ Rate limit en una clave. Esperando {wait_time}s y rotando a siguiente clave (intento {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                wait_time = 3
                print(f"\n    ⚠️ Error en embeddings ({e}). Esperando {wait_time}s y reintentando...")
                time.sleep(wait_time)
    
    raise RuntimeError("Fallo crítico en generación de embeddings tras agotar reintentos.")

# -------------------------------------------------------------
# 4. Ingesta Principal
# -------------------------------------------------------------
def ejecutar_ingesta():
    carpeta_normativa = os.path.join(os.path.dirname(__file__), "..", "normativa")
    archivos = sorted([f for f in os.listdir(carpeta_normativa) if f.endswith(".md") and f != "README.md"])

    print(f"\n📚 Se encontraron {len(archivos)} documentos para ingestar:")
    for a in archivos:
        print(f"  • {a}")
    print("=" * 70)

    total_puntos_global = 0

    for idx, nombre_archivo in enumerate(archivos, 1):
        ruta = os.path.join(carpeta_normativa, nombre_archivo)
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            contenido = f.read()

        hash_actual = hashlib.sha256(contenido.encode("utf-8")).hexdigest()
        hash_previo = obtener_hash_guardado(nombre_archivo)

        print(f"\n[{idx}/{len(archivos)}] Analizando: {nombre_archivo}")

        if hash_previo == hash_actual:
            print(f"  🟢 YA COMPLETADO en Qdrant y Neon. Omitiendo para no duplicar ni gastar tokens.")
            continue

        chunks = procesar_archivo_normativo(contenido)
        print(f"  📑 Total fragmentos generados: {len(chunks)}")

        BATCH_SIZE = 20
        total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE
        puntos_qdrant = []

        for b_idx in range(total_batches):
            inicio = b_idx * BATCH_SIZE
            fin = min(inicio + BATCH_SIZE, len(chunks))
            lote = chunks[inicio:fin]

            sys.stdout.write(f"\r  ⚡ Vectorizando lote {b_idx + 1}/{total_batches} ({len(lote)} fragmentos)...")
            sys.stdout.flush()

            vectores = generar_embeddings_lote(lote, dim_esperada=expected_dim)

            for i, (texto_chunk, vector) in enumerate(zip(lote, vectores)):
                chunk_index = inicio + i
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{nombre_archivo}_{chunk_index}"))

                punto = qmodels.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "doc_content": texto_chunk,
                        "file_name": nombre_archivo,
                        "original_filename": nombre_archivo,
                        "tipo": "ley_oficial",
                        "source": nombre_archivo,
                        "metadata": {
                            "file_name": nombre_archivo,
                            "original_filename": nombre_archivo,
                            "tipo": "ley_oficial",
                            "source": nombre_archivo,
                            "chunk_index": chunk_index
                        }
                    }
                )
                puntos_qdrant.append(punto)

            # Pausa breve de 1 segundo para rotar tranquilamente
            time.sleep(1.2)

        print(f"\n  💾 Subiendo {len(puntos_qdrant)} vectores a Qdrant Cloud...")
        # Subir a Qdrant en lotes de 100
        for q_i in range(0, len(puntos_qdrant), 100):
            qdrant.upsert(
                collection_name=QDRANT_COLLECTION,
                points=puntos_qdrant[q_i:q_i + 100]
            )

        # Registrar en Neon de forma segura
        guardar_en_neon(nombre_archivo, hash_actual, len(puntos_qdrant))

        total_puntos_global += len(puntos_qdrant)
        print(f"  ✅ '{nombre_archivo}' completado exitosamente ({len(puntos_qdrant)} puntos en Qdrant).")

    print("\n" + "=" * 70)
    print(f"🎉 ¡INGESTA TOTAL FINALIZADA CON ÉXITO! Total puntos en Qdrant: {total_puntos_global}")
    print("=" * 70)

if __name__ == "__main__":
    ejecutar_ingesta()

