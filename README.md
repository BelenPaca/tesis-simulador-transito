# TransiAI: Sistema de Asistencia y Simulación de Tránsito (Monorepo)

## Descripción General
TransiAI es una plataforma integral basada en arquitectura RAG (Retrieval-Augmented Generation) diseñada para brindar orientación y análisis interactivo sobre la normativa legal de transporte, tránsito y seguridad vial en el Ecuador (COIP, LOTTTSV, Reglamento General y normativa conexa).

Este repositorio monolítico consolida el código fuente completo del sistema, permitiendo la ejecución local integral tanto del backend como del frontend, además de servir como base para los repositorios desacoplados de despliegue en la nube.

---

## Estructura del Proyecto

- **spring-rag/:** Servicio backend desarrollado en Java y Spring Boot (Spring AI, controladores REST, servicios de ingesta documental y conectores de bases de datos).
- **vue-chat-ui/:** Cliente web interactivo desarrollado en Vue.js 3 y Vite, con soporte para Server-Sent Events (SSE) y renderizado de componentes analíticos.

---

## Modalidades de Despliegue del Sistema

El ecosistema de TransiAI opera bajo dos esquemas:

### 1. Entorno de Producción en la Nube (Arquitectura Desacoplada)
- **Frontend:** Desplegado en **Cloudflare Pages** sobre una red de distribución perimetral (Edge CDN). Repositorio dedicado: `tesis-simulador-transito-front`.
- **Backend:** Desplegado en **Render (PaaS)** como contenedor Docker (OpenJDK 25). Repositorio dedicado: `tesis-simulador-transito-backend`.
- **Bases de Datos:** Clúster gestionado en **Qdrant Cloud** (almacenamiento vectorial) y base de datos serverless en **Neon.tech** (PostgreSQL).

### 2. Entorno de Ejecución Local (Línea Base y Privacidad)
Permite levantar el entorno completo de forma autónoma mediante contenedores con Podman o Docker Compose, utilizando instancias locales de PostgreSQL y Qdrant.

---

## Requisitos del Sistema

- Java Development Kit (JDK) 21 o superior
- Node.js 18 o superior y npm
- Podman o Docker con Docker Compose
- Gradle (incluido en el repositorio mediante gradlew)

---

## Guía de Ejecución en Entorno Local

### 1. Inicialización de Bases de Datos Locales
```bash
cd spring-rag
podman compose up -d
```

### 2. Ejecución del Backend
```bash
cd spring-rag
./gradlew bootRun
```
El servicio estará disponible en `http://localhost:8080`.

### 3. Ejecución del Frontend
```bash
cd vue-chat-ui
npm install
npm run dev
```
La interfaz de usuario estará disponible en `http://localhost:5173`.

---

## Licencia y Uso Académico
Proyecto desarrollado como trabajo de titulación e investigación académica. Todos los derechos reservados.
