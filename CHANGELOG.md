# Project Rosetta / Prompt Wars — Enhancement Changelog

This document tracks all new features, architecture extensions, data models, UI components, and improvements added to the **Prompt Wars (Project Rosetta)** codebase relative to the upstream repository [`neednotbenamed/promptwars`](https://github.com/neednotbenamed/promptwars).

---

## 🌟 Summary of Key Enhancements

| Category | Upstream State (`neednotbenamed/promptwars`) | Enhanced State (`ajayanand-1/Interview_try`) |
|---|---|---|
| **Candidate Feedback Engine** | Not present | **Multi-Persona Candidate Feedback & Growth Playbook** synthesizing actionable guidance from HR, Skeptic, Hiring Manager, Technical, and General Secretary. |
| **Resume Rewriting Guide** | Not present | **Evidence-grounded Resume Improvements** with Identified Issues, Actionable Recommendations, and side-by-side **Before vs. After rewrite examples**. |
| **Target Job Skills Roadmap** | Basic memo gaps | **Structured Capabilities Roadmap** mapping Company Expectations, Verified Candidate Levels, and Concrete Growth Paths. |
| **Company Expectations Guide** | Implicit in memos | **Explicit Organizational Standards** analyzing Accountability, Retention, Scientific Rigor, and Future Interview Advice. |
| **API Endpoints** | `/api/evaluations/*` (metadata, rosetta, memos, debate, decision, report) | Added dedicated **`GET /api/evaluations/{run_id}/feedback`** with full Pydantic schema validation. |
| **Frontend UI (React SPA)** | 5 Tabs (Overview, Rosetta, Memos, Debate, Decision Path) | Added 6th Tab **"💡 Candidate Feedback & Growth"** with interactive cards, before/after diffs, and 5-persona feedback grid. |
| **Streamlit UI** | 6 Tabs | Added 7th Tab **"💡 Candidate Feedback"** with collapsible before/after rewrite blocks and skills breakdown. |
| **PDF & Markdown Deliverables** | Executive Decision & Citations | Expanded to include **Candidate Feedback & Growth Playbook** directly in generated Markdown and ReportLab PDFs. |
| **Automated Testing** | 47 tests | **55 Comprehensive Unit, Integration, and Traceability Tests** passing. |

---

## 🛠️ Detailed Component Changes

### 1. Data Models (`src/models/decision.py`)
- **`PersonaFeedbackItem`**: Captures persona name, punchy headline, constructive evaluation feedback, and key recommendation.
- **`ResumeImprovementItem`**: Captures resume section/topic, identified issue from evaluation, actionable recommendation, and concrete `example_before` / `example_after` diffs.
- **`RequiredSkillItem`**: Maps skill categories to company expectations, candidate verified status, and mastery roadmaps.
- **`CompanyExpectationItem`**: Defines organizational standards, candidate performance findings, and future interview preparation tips.
- **`CandidateFeedback`**: Aggregates all 4 dimensions into a unified feedback deliverable.
- **`FinalReportData`**: Integrated optional `feedback: CandidateFeedback` field into core decision schema.

### 2. Decision Engine (`src/decision/engine.py`)
- Added specialized feedback synthesizers for:
  - **Ananya Iyer**: Focuses on benchmark quantification (converting ~40% spot-checks to gold standard numbers), multi-agent graph framework ramp-up (LangGraph/CrewAI), and CI/CD pre-deploy evaluation harnesses.
  - **Rohan Malhotra**: Focuses on attribution honesty (correcting solo architect claims), tenure stability narrative (avoiding 7-month departures), and quantitative observability.
  - **Generic / Custom Candidates**: Dynamically derives evidence-grounded feedback, resume rewriting tips, and domain skill gap analyses from Rosetta index citations.
  - **Auto-Resolved Cases**: Generates consensus feedback based on unanimous panel deliberation.

### 3. Deliverables & Report Generators (`src/decision/reporter.py`)
- **Markdown Report Generator (`generate_markdown_report`)**:
  - Added Section `## 6. Comprehensive Candidate Feedback & Growth Playbook`.
  - Structured subsections for Resume Improvements, Target Skills Roadmap, Company Expectations, and 5-Persona Breakdown.
- **PDF Report Generator (`generate_pdf_report`)**:
  - Implemented ReportLab flowables rendering Candidate Feedback & Growth Playbook on generated PDF exports.

### 4. API Endpoints (`src/api/routes/evaluations.py`)
- Added **`GET /api/evaluations/{run_id}/feedback`**: Direct endpoint returning candidate feedback and growth playbook.
- Updated **`GET /api/evaluations/{run_id}/decision`**: Returns feedback object alongside decision path.

### 5. React Frontend SPA (`frontend/`)
- **`frontend/src/types/api.ts`**: Defined TypeScript interfaces for `CandidateFeedback`, `PersonaFeedbackItem`, `ResumeImprovementItem`, `RequiredSkillItem`, `CompanyExpectationItem`.
- **`frontend/src/api/client.ts`**: Added `api.getFeedback(runId)` client method.
- **`frontend/src/pages/EvaluationDetail.tsx`**:
  - Added 6th Navigation Tab **"Candidate Feedback & Growth"**.
  - Built interactive UI with top strategic takeaway banner, 2-column Before/After resume rewrite blocks, skills capability matrix, organizational standards breakdown, and 5-persona feedback cards.

### 6. Streamlit Application (`streamlit_app.py`)
- Added 7th Tab **"💡 Candidate Feedback"** with collapsible expanders for Resume Rewriting, Required Skills Roadmap, Company Expectations, and 5-Persona evaluation breakdown.

---

## 👤 Original Author Attribution
- **Original Author**: [`neednotbenamed`](https://github.com/neednotbenamed)
- **Original Upstream Repository**: [https://github.com/neednotbenamed/promptwars](https://github.com/neednotbenamed/promptwars)
