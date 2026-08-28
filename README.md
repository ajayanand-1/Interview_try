# PROMPT WARS: Project Rosetta
### Evidence-Grounded Multi-Agent Hiring Intelligence

> A production-grade multi-agent recruitment deliberation system where four isolated AI personas evaluate candidate profiles, cross-examine evidence in structured debate, and synthesize binding hiring decisions with 100% citation traceability.

---

## 🚀 Key Innovations & Architecture

- **Project Rosetta ("Candidate Profile Bible")**: Ingests arbitrary resumes and transcripts, detects sections, and indexes every claim with stable citation IDs (`[R-EXP-01]`, `[T-A1]`, etc.).
- **Strict Persona Isolation**: 4 domain agents evaluate candidates in zero-leakage isolation before deliberation:
  1. `Technical Agent` (Architecture, fundamentals, technical depth)
  2. `HR / Culture Agent` (Friction, accountability, cultural alignment with mandatory contrarian check)
  3. `Hiring Manager Agent` (Velocity, ramp-up ROI, retention economics)
  4. `Skeptic Agent` (Cross-examination, resume inflation detection, attribution auditing)
- **General Secretary Deliberation & Adjudication**: Chairs multi-round debate with integer voting, direct rebuttals, and deliberative score shifting ("Opinion Changed"). Synthesizes a non-averaging qualitative hiring verdict.
- **Constitutional Override Protocol**: Agents can file formal override motions against the General Secretary verdict, requiring a 75% supermajority vote (3/4) to pass.
- **100% Evidence Traceability**: Every strength, concern, and debate claim resolves back to verbatim source text.
- **Run-Scoped Workspaces (`RunWorkspace`)**: Complete isolation between evaluation runs preventing global file collisions and enabling parallel multi-candidate evaluations.

---

## 🛠️ Tech Stack

- **Intelligence Core & Backend**: Python 3.11+, FastAPI, Pydantic v2, ReportLab, PyPDF, Uvicorn, Pytest
- **Frontend Presentation Layer**: React 19, Vite, TypeScript, Tailwind CSS, Lucide React, React Router v7

---

## ⚡ Quick Start (Local Development)

### 1. One-Command Dev Launcher
```bash
./scripts/dev.sh
```
*Starts both the FastAPI backend on `http://127.0.0.1:8000` and the React frontend on `http://localhost:3000`.*

---

### 2. Manual Startup

#### Terminal 1: FastAPI Backend
```bash
# Activate virtual environment
source .venv/bin/activate

# Start API server
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Backend API**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`

#### Terminal 2: React Frontend
```bash
cd frontend
npm install
npm run dev
```
- **Frontend UI**: `http://localhost:3000`

---

## 🧪 Testing

Run the full automated test suite (40 unit, integration, API, debate, decision, isolation, and workspace tests):

```bash
./.venv/bin/pytest -v
```

Build the frontend production bundle:
```bash
cd frontend && npm run build
```

---

## ☁️ Cloud Deployment (Render)

This repository includes a `render.yaml` specification for instant free-tier deployment on Render:

1. **Backend Web Service (`promptwars-api`)**:
   - Environment: Python 3.11
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
2. **Frontend Static Site (`promptwars-ui`)**:
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/dist`
   - Environment Variable: `VITE_API_BASE_URL=https://promptwars-api.onrender.com`

---

## 📜 License
Apache-2.0
