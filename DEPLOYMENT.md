# Google Cloud Run Deployment Guide: Project Rosetta (Prompt Wars)

This document provides the complete, production-ready guide for packaging and deploying **PROMPT WARS (Project Rosetta)** to **Google Cloud Run** as a single, unified container.

---

## 🏗️ Architecture on Google Cloud Run

The entire application runs inside a single container instance on Google Cloud Run:

```
                            Google Cloud Run Service
                     (https://promptwars-<hash>-uc.a.run.app)
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

- **Unified Single-Origin**: Eliminates CORS complications by serving both the API and the React frontend on the same port (`$PORT`, default `8080`).
- **SPA Routing**: Non-API routes (e.g. `/evaluations`, `/evaluations/new`, `/evaluations/:run_id`, `/candidates`, `/jobs`, `/reports`) return `index.html` with status `200 OK` so direct links and browser refreshes work natively.
- **Dynamic Port Binding**: Automatically binds to `0.0.0.0:$PORT` provided by Google Cloud Run.

---

## 🚀 Google Cloud Run Deployment Instructions

### Method 1: One-Command Source Deployment (Recommended)

Google Cloud Run can build the container image automatically using Cloud Build and deploy it:

```bash
# 1. Authenticate with Google Cloud
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT_ID

# 2. Deploy directly from repository root
gcloud run deploy promptwars \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars GEMINI_API_KEY="your-gemini-api-key"
```

---

### Method 2: Build with Cloud Build & Artifact Registry

```bash
# 1. Create an Artifact Registry repository (if not already created)
gcloud artifacts repositories create promptwars-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Prompt Wars Docker Repository"

# 2. Build and push image via Google Cloud Build
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_GCP_PROJECT_ID/promptwars-repo/promptwars:latest .

# 3. Deploy image to Cloud Run
gcloud run deploy promptwars \
  --image us-central1-docker.pkg.dev/YOUR_GCP_PROJECT_ID/promptwars-repo/promptwars:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars GEMINI_API_KEY="your-gemini-api-key"
```

---

## 🐳 Local Docker Verification

To test the container image locally before deploying to Cloud Run:

```bash
# 1. Build Docker image locally
docker build -t promptwars:local .

# 2. Run container locally mapping port 8080
docker run -p 8080:8080 -e PORT=8080 -e GEMINI_API_KEY="your-key" promptwars:local

# 3. Test endpoints
curl http://localhost:8080/api/health
curl http://localhost:8080/
curl http://localhost:8080/evaluations
curl http://localhost:8080/docs
```

---

## 💻 Local Development Workflow (Without Docker)

### 1. Dual-Server Development Mode (with Vite HMR)
```bash
./scripts/dev.sh
```
- **Frontend UI**: `http://localhost:3000`
- **Backend API**: `http://127.0.0.1:8000`

### 2. Single-Port Production Mode
```bash
# 1. Build frontend
cd frontend && npm run build && cd ..

# 2. Run unified FastAPI server
PORT=8080 ./.venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8080
```
- **Unified App**: `http://localhost:8080/`
- **Swagger Docs**: `http://localhost:8080/docs`
- **Health Check**: `http://localhost:8080/api/health`

---

## ⚙️ Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `PORT` | Auto-provided | `8080` | Port on which the container listens (Cloud Run sets this automatically). |
| `GEMINI_API_KEY` | Optional | `None` | Google Gemini API key for external LLM evaluation personas. |
| `ALLOWED_ORIGINS` | Optional | `*` | Comma-separated list of CORS origins if accessing API externally. |

---

## 🩺 Cloud Run Health Check & Probe Configuration

- **Health Check Path**: `/api/health`
- **Port**: `8080` (or dynamic `$PORT`)
- **Protocol**: HTTP
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "project-rosetta-api",
    "version": "1.0.0"
  }
  ```
