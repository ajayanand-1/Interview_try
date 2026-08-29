# PROMPT WARS: Project Rosetta
### Evidence-Grounded Multi-Agent Hiring Intelligence

> A production-grade multi-agent recruitment deliberation system where four isolated AI personas evaluate candidate profiles, cross-examine evidence in structured debate, and synthesize binding hiring decisions with 100% citation traceability.

> **Original Author**: [`neednotbenamed`](https://github.com/neednotbenamed)  
> **Original Repository**: [neednotbenamed/promptwars](https://github.com/neednotbenamed/promptwars)

---

## 🚀 Key Innovations & Architecture

- **Fixed AI Persona & Voice Roster (2 Female / 2 Male)**: Every agent has a distinct, permanent identity and fixed synthesis voice:
  1. `Dr. Maya Lin` (Technical Agent, ♀ Female, Karen voice) — Lead AI Systems Architect
  2. `Marcus Vance` (HR / Culture Agent, ♂ Male, Oliver voice) — Head of People & Culture
  3. `David Sterling` (Hiring Manager, ♂ Male, Fred voice) — VP Engineering & Product ROI
  4. `Dr. Rachel Thorne` (Skeptic Agent, ♀ Female, Samantha voice) — Principal Forensic Auditor
  5. `Arthur Pendelton` (General Secretary, ♂ Male, Daniel voice) — Panel Moderator & Adjudicator
- **Parliamentary Civil Deliberation (No Overlapping)**: Structured turn-taking covering 4 mandatory pillars:
  - 🎯 **Core Problem**: Technical, organizational, or economic challenge.
  - 📋 **Company Expectation**: Role competency and delivery standards.
  - ⚖️ **Pros & Cons**: Grounded evidence analyzing strengths and risk factors.
  - 💡 **Viable Solutions**: Actionable onboarding remedies, pair programming, and CI evaluation harnesses.
- **Interactive Voice Stream Player**: Web Speech API integration in React SPA for sequential, non-overlapping audio deliberation streaming.
- **Universal Responsive Design**: Seamless experience across mobile, tablet, and desktop with collapsible drawer navigation and adaptive layouts.
- **Multi-Persona Candidate Feedback & Growth Playbook**: Generates actionable, persona-grounded improvement plans across Resume Improvements (Before/After diffs), Skills Roadmap, and Company Expectations.
- **Run-Scoped Workspaces (`RunWorkspace`)**: Complete isolation between evaluation runs preventing global file collisions and enabling parallel multi-candidate evaluations.
- **Changelog & Enhancements**: See [CHANGELOG.md](file:///Users/ajayanand/desktop/test/promptwars/CHANGELOG.md) for full list of extensions from the original upstream repository.

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

Run the full automated test suite (47 unit, integration, API, debate, decision, isolation, and workspace tests):

```bash
./.venv/bin/pytest -v
```

Build the frontend production bundle:
```bash
cd frontend && npm run build
```

---

## ☁️ Google Cloud Run Deployment

Deploy directly from source to **Google Cloud Run** using the CLI:

```bash
# 1. Login and select your project
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT_ID

# 2. Deploy to Cloud Run
gcloud run deploy promptwars \
  --source . \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars GEMINI_API_KEY="your-gemini-api-key"
```

---

## 🎬 3–5 Minute Hackathon Presentation Demo Script

1. **Dashboard (`/`)**:
   - Open the web application. Show the live **Core Engine Online** indicator and system metrics.
2. **Launch Multi-Candidate Evaluation (`/evaluations/new`)**:
   - Highlight universal candidate support.
   - Click the preset **"Batch: Both Candidates (1 Job + 2 Candidates)"** button or drag-and-drop custom PDFs.
   - Click **Start Batch (2 Candidates)**.
3. **Inspect Evaluation Run (`/evaluations/:run_id`)**:
   - Show the live phase progression (*Ingestion* $\rightarrow$ *Rosetta* $\rightarrow$ *Agents* $\rightarrow$ *Debate* $\rightarrow$ *Decision* $\rightarrow$ *Report*).
   - **Tab 1: Verdict & Overview**: Point out the General Secretary non-averaging synthesis and the Override Motion deliberation box.
   - **Tab 2: Rosetta Bible**: Show the indexed facts and the master citation lookup table.
   - **Tab 3: Sealed Agent Memos**: Show the 4 independent pre-debate persona memos and the HR / Culture Devil's Advocate contrarian argument.
   - **Tab 4: Debate Replay & Deltas**: Show the turns with rebuttal badges and the **"Deliberation Score Shifts (Opinion Changed)"** box showing dynamic vote movement during cross-examination.
   - **Tab 5: Decision Path Flow**: Walk through the visual flowchart from isolated memos to final verdict.
4. **Interactive Evidence Explorer**:
   - Click any citation badge (e.g. `[T-A7]` or `[R-EXP-01]`).
   - The **Evidence Explorer Modal** displays the exact verbatim quote and the personas citing it, proving **100% citation traceability**.
5. **Multi-Candidate Hiring Room (`/jobs`)**:
   - Open `/jobs` and select `AI ENGINEER FREIGHT`.
   - View the side-by-side comparison matrix comparing Ananya vs. Rohan across persona scores, strengths, and concerns.
6. **Download Report (`/reports`)**:
   - Click **Download PDF** to inspect the final deliverable.

---

## 📜 License
Apache-2.0
