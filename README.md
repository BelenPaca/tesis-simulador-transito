# 🚗 TransiAI: Asistente Virtual RAG para Consultas y Análisis de Tránsito

**TransiAI** es un asistente virtual inteligente basado en la técnica **RAG (Retrieval-Augmented Generation)**, diseñado para resolver consultas sobre la Ley Orgánica de Transporte Terrestre, Tránsito y Seguridad Vial (LOTTTSV). Permite brindar información educativa precisa a conductores, peatones y profesionales del derecho, además de analizar automáticamente casos o infracciones de tránsito.

---

## 🌟 Características Principales

- **⚖️ Asesoría Legal Adaptativa y RAG Puro:** Basado en un motor RAG 100% dinámico y probabilístico (sin palabras quemadas ni listas estáticas en código), contrastando consultas ciudadanas frente al COIP, LOTTTSV, Reglamento General, Código del Trabajo, Constitución y COGEP.
- **🪟 Descomposición por Ventanas Deslizantes Léxicas:** Divide consultas compuestas con múltiples infracciones mediante ventanas solapadas ($W=12$, $S=8$) con garantía de ventana final de cola, recuperando todas las conductas concurrentes (ej. exceso de velocidad, semáforo en rojo, celular y llantas lisas según el Art. 383 del COIP).
- **🧠 Memoria Conversacional Multi-Turno:** Mantiene el hilo y acumulación de hechos a través de múltiples turnos en PostgreSQL (Neon), contextualizando repreguntas breves de seguimiento.
- **📄 Análisis Pericial Multimodal e Informes Técnicos:** Ingesta de documentos PDF escaneados o informes técnicos periciales (SIAT de la Policía Nacional) vía Apache Tika, con **Puente de Hechos (*Fact Bridging*)** para conectar datos técnicos (velocidades, alcoholemia, días de incapacidad) con delitos de tránsito con lesiones (**Art. 379 COIP**).
- **🛡️ Blindaje de Dominio y Filtrado Adaptativo:** Si el usuario sube un archivo ajeno a tránsito (ej. lista de compras), la IA lo resume con fidelidad y aclara amablemente que no contiene infracciones viales sin alucinar normas del COGEP. Asimismo, declina cortésmente preguntas fuera de dominio (ej. recetas de cocina) y suprime reactivamente cualquier pastilla de leyes fantasma.
- **🚨 Analizador Inteligente de Infracciones:** Genera automáticamente el bloque estructurado `[INFRACTION_DATA]` proyectando el velocímetro en tres niveles (**LEVE**, **GRAVE**, **MUY GRAVE**), base legal aplicable, consecuencias, puntos de licencia y recomendaciones.
- **💬 Interfaz Web Interactiva en Vue 3:** Transmisión fluida por Server-Sent Events (SSE) con citas legales interactivas (`[LEGAL_SOURCES]`), tooltips dinámicos con extractos de ley, modo oscuro/claro y diseño adaptativo.

---

## 🚀 Arquitectura y Tecnologías Utilizadas

### Backend (Spring Boot 3)
- **Lenguaje / Framework:** Java + Spring Boot 3
- **IA & RAG:** Spring AI para la integración con Modelos de Lenguaje Grandes (LLM).
- **Procesamiento de Documentos:** Pipeline de *transformers* y procesamiento de texto para división en *chunks* e ingesta de normativa.
- **Base de Datos Vectorial:** **Qdrant** para la búsqueda por similitud semántica.
- **Base de Datos Relacional:** **PostgreSQL** para la gestión y persistencia del historial de chats.

### Frontend (Vue 3 + Vite)
- **Framework:** Vue.js 3 (Composition API) impulsado por Vite.
- **Diseño & Estilos:** Vanilla CSS con paleta de colores personalizada, animaciones fluidas y soporte receptivo (Dark / Light Theme).
- **Renderizado de Contenido:** Parsing de Markdown en tiempo real con renderizado especializado para bloques de datos de infracción.

### Infraestructura (Contenedores con Podman)
- Orquestación local mediante `podman-compose.yml` para desplegar PostgreSQL y Qdrant.

---

## 📁 Estructura del Proyecto

```text
tesis-simulador-transito/
├── spring-rag/                  # Backend Spring Boot (Servicios RAG, REST API, Prompts)
│   ├── src/main/java/           # Código fuente Java (Servicios, Controladores, Entidades)
│   ├── src/main/resources/      # Configuración (application.yml, prompts, modelos ONNX)
│   ├── podman-compose.yml       # Configuración de contenedores (PostgreSQL + Qdrant)
│   └── build.gradle.kts         # Configuración de dependencias Gradle
└── vue-chat-ui/                 # Frontend Vue 3 (Interfaz de usuario)
    ├── src/                     # Componentes, vistas y recursos de Vue
    ├── package.json             # Dependencias del Frontend
    └── vite.config.js           # Configuración de Vite
```

---

## 🛠️ Cómo Ejecutar el Proyecto

### 1. Servicios de Base de Datos (PostgreSQL & Qdrant)
Navega a la carpeta del backend `spring-rag` e inicia los servicios requeridos con Podman:

```bash
cd spring-rag

# Iniciar contenedores de PostgreSQL y Qdrant en segundo plano
podman compose up -d

# Detiene y elimina contenedores
podman compose down
```

### 2. Backend (Spring Boot)
Desde la raíz del proyecto o dentro de `spring-rag`:

```bash
# Compilar y ejecutar la aplicación Spring Boot
./gradlew bootRun
```
*El servicio se iniciará en `http://localhost:8080`.*

### 3. Frontend (Vue 3)
Para desarrollo e iteración en el cliente web:

```bash
cd vue-chat-ui

# Instalar dependencias
npm install

# Iniciar el servidor de desarrollo Vite
npm run dev
```
*La interfaz estará disponible en `http://localhost:5173`.*

Para construir los archivos estáticos de producción:
```bash
npm run build
```

---

## ⚙️ Configuración del Prompt del Sistema

El comportamiento de **TransiAI** se encuentra definido en `spring-rag/src/main/resources/prompts/systemPrompt.st`, garantizando que la IA responda únicamente con base en la normativa cargada y genere etiquetas estructuradas `[INFRACTION_DATA]` cuando detecte la descripción de un incidente de tránsito.
