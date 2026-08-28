# Deployment Guide: Unified Production Server for Koyeb & Cloud

This document describes how **PROMPT WARS (Project Rosetta)** operates as a unified, single-origin production application and how to deploy it to platforms like **Koyeb**, **Render**, or **Docker/K8s**.

---

## 🏗️ Architecture: Unified Single-Origin Server

In production, a single FastAPI process serves both the backend API and the compiled React Single Page Application (SPA):

```
                                Client Browser
                                      │
                   ┌──────────────────┴──────────────────┐
                   │                                     │
           Path: /api/*, /docs, /openapi.json     Path: /, /evaluations, /jobs...
                   │                                     │
                   ▼                                     ▼
          FastAPI Endpoints                     React SPA (index.html)
     (Evaluations, Rosetta, Memos,           (Client-side router rendered
       Debate, Decision, Reports)              from frontend/dist/)
```

### Route Resolution Hierarchy:
1. `/api/*` $\rightarrow$ Processed directly by FastAPI routes.
2. `/api/health` $\rightarrow$ Liveness check returning `{"status": "healthy"}`.
3. `/docs` & `/openapi.json` $\rightarrow$ Interactive Swagger UI & OpenAPI schema.
4. `/assets/*` $\rightarrow$ Static assets (JS/CSS bundles) mounted from `frontend/dist/assets/`.
5. `/*` (e.g. `/`, `/evaluations`, `/evaluations/new`, `/evaluations/:run_id`, `/candidates`, `/jobs`, `/reports`) $\rightarrow$ Returns `frontend/dist/index.html` for client-side routing.
6. Unknown `/api/*` routes $\rightarrow$ Return JSON `404 Not Found` (never HTML).

---

## 💻 Local Development Workflow

### 1. Separate Development Mode (Fast Feedback with Vite HMR)
- **Terminal 1 (FastAPI Backend)**:
  ```bash
  ./.venv/bin/uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
  ```
- **Terminal 2 (React Vite Frontend)**:
  ```bash
  cd frontend && npm run dev
  ```
- **One-Command Dev Launcher**:
  ```bash
  ./scripts/dev.sh
  ```

### 2. Local Production-Serving Verification (Single-Origin Mode)
```bash
# 1. Compile the React frontend
cd frontend && npm run build && cd ..

# 2. Start the unified FastAPI server
./.venv/bin/uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```
*Open `http://localhost:8000` in your browser. Both the React SPA and API endpoints will function seamlessly from port 8000.*

---

## 🚀 Production Deployment to Koyeb

### Option 1: Koyeb Git-Driven Deployment (Buildpack / Python)

1. **Build Step**:
   Ensure both Python dependencies and the frontend bundle are compiled:
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && cd frontend && npm install && npm run build && cd ..
     ```
2. **Start Step**:
   - **Run / Start Command**:
     ```bash
     uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
     ```

### Option 2: Koyeb Docker Deployment

A standard `Dockerfile` can be used:

```dockerfile
# Stage 1: Build React Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend Runtime
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source & built frontend
COPY src/ ./src/
COPY data/ ./data/
COPY --from=frontend-builder /app/frontend/dist/ ./frontend/dist/

# Koyeb default port
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port $PORT"]
```

---

## ⚙️ Required Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `PORT` | Optional | `8000` | Port for Uvicorn HTTP server (automatically supplied by Koyeb/Render/Cloud Run). |
| `ALLOWED_ORIGINS` | Optional | `*` | Comma-separated list of additional CORS origins. |
| `GEMINI_API_KEY` | Optional | `None` | Google Gemini API key if using live LLM personas. |
| `OPENAI_API_KEY` | Optional | `None` | OpenAI API key if using OpenAI models. |

---

## 🩺 Health Check & Monitoring

- **Health Endpoint**: `GET /api/health`
- **Expected Status**: `200 OK`
- **Expected Payload**:
  ```json
  {
    "status": "healthy",
    "service": "project-rosetta-api",
    "version": "1.0.0"
  }
  ```
- **Koyeb Health Check Configuration**:
  - **Protocol**: HTTP
  - **Path**: `/api/health`
  - **Port**: `8000` (or `$PORT`)
