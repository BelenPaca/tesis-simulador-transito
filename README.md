# Trabajo Grupal: Sistema RAG para Consultas de Normativa UCE

Este proyecto es un asistente virtual diseñado para la Carrera de Computación (FICA - UCE), con el objetivo de resolver dudas sobre la normativa de titulación y los proyectos integradores de los estudiantes.

## 🚀 Arquitectura y Tecnologías Utilizadas

El sistema emplea la técnica **RAG (Retrieval-Augmented Generation)** para enriquecer las respuestas del Modelo de Lenguaje con documentos de contexto almacenados localmente.

### Backend (Spring Boot)
- **Framework:** Spring Boot 3 + Java
- **IA Integration:** Spring AI para la conexión fluida con Modelos de Lenguaje Grandes (LLM).
- **Controladores REST:** Endpoints para enviar consultas de chat y administrar el historial de conversaciones.
- **Base de Datos Relacional:** PostgreSQL para almacenar el historial de conversaciones y estado de la aplicación.
- **Base de Datos Vectorial:** Qdrant para almacenar y recuperar de forma semántica los *embeddings* de los documentos de normativa.

### Frontend (Vue 3)
- **Framework:** Vue.js 3 (Composition API) construido con Vite.
- **Estilos:** Vanilla CSS con paleta de colores personalizada (modo claro y oscuro) con un diseño Premium y minimalista.
- **Funcionalidades:** 
  - Chat interactivo con streaming de respuestas (Markdown parseado).
  - Historial de conversaciones guardado en base de datos.
  - Sidebar con opciones de temas y acceso rápido al perfil de la aplicación (SabIA Asistente).

### Infraestructura (Docker)
- Se utiliza `docker-compose.yml` para levantar fácilmente la base de datos PostgreSQL y Qdrant localmente.

## 🛠️ Cómo Ejecutar el Proyecto

1. **Levantar los servicios de base de datos:**
   Asegúrate de tener Docker instalado y ejecuta en la carpeta `11.spring-rag`:
   ```bash
   docker-compose up -d
   ```

2. **Backend (Spring Boot):**
   Abre el proyecto en tu IDE y ejecuta la clase principal `SpringRagMain.java`. El backend se levantará (normalmente en el puerto 8080) y servirá la interfaz automáticamente en la raíz.

3. **Frontend (Desarrollo):**
   Si deseas hacer modificaciones a la interfaz gráfica:
   ```bash
   cd 12.vue-chat-ui
   npm install
   npm run dev
   ```
   Para construir y pasar a producción (Spring), ejecuta:
   ```bash
   npm run build
   ```
   (Los archivos compilados en `dist/` se deben copiar a `11.spring-rag/src/main/resources/static/`).

## 👥 Equipo de Desarrollo
Proyecto grupal desarrollado para la materia correspondiente en la Carrera de Computación (FICA - UCE).
