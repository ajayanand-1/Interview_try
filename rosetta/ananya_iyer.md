# Rosetta Document — Candidate Profile: Ananya Iyer
**Candidate ID**: `ananya_iyer` | **Target Role**: `AI Engineer — Agentic Systems`

> **Note for Evaluating Agents**: Every evaluation claim, strength, gap, and vote in your memos and debate MUST cite one of the stable citation IDs (`[R-EXP-xx]`, `[T-Axx]`, etc.) indexed in this document.

---
## 1. Resume Facts
### 1.1 Education
- **`[R-EDU-01]`** B.E. Information Technology, University of Mumbai (2019)

### 1.2 Professional Experience
#### Software Engineer II — Bridgepoint Systems (2021-06 – present, 4.0 yrs)
- **`[R-EXP-01]`** Maintains Python/FastAPI microservices for an internal ops platform used by a few internal teams.
- **`[R-EXP-02]`** Helped migrate part of the document ingestion pipeline to use OCR-based extraction for scanned forms.
- **`[R-EXP-03]`** Over the last 1.5 years, started building an internal RAG-based support-ticket assistant: set up a retrieval pipeline (LangChain + Chroma); team estimated answer accuracy improved by around 40% based on informal review.
- **`[R-EXP-04]`** After a production incident (see interview), introduced a pre-deploy checklist for prompt changes that the team adopted.

#### Junior Backend Developer — Bridgepoint Systems (2019-07 – 2021-06, 2.0 yrs)
- **`[R-EXP-05]`** Built basic REST APIs for internal tooling.
- **`[R-EXP-06]`** Worked with QA and product to define API contracts.

### 1.3 Technical Skills & Certifications
- **Core Skills**: Python, FastAPI, MongoDB, PostgreSQL, LangChain, Chroma, basic React, OCR pipelines (Tesseract), Docker

## 2. Interview Transcript Facts
### 2.1 Technical Q&A
**`[T-Q1]` Question (RAG support-ticket assistant architecture)**:
> Tell me about the RAG pipeline you built for the support-ticket assistant.

**`[T-A1]` Candidate Response**:
> Sure — happy to walk through it step by step. We retrieve from a Chroma vector store built from past resolved tickets and internal docs. The top few matches get passed to the LLM, which drafts a response for a human agent to review before it goes out. We chunked documents by section rather than fixed length, since that kept related context together.

**`[T-Q2]` Question (40% accuracy improvement metric measurement) *(Follow-up)***:
> Your resume mentions a ~40% accuracy improvement. How was that measured?

**`[T-A2]` Candidate Response *(Self-Disclosed Gap)***:
> I want to be upfront about this — it was based on internal review, not a formal benchmark. A few of us spot-checked a sample of responses before and after the change and it felt clearly better, but I wouldn't want to present that number as something rigorous if it comes up again.

**`[T-Q3]` Question (Multi-agent orchestration frameworks (LangGraph, CrewAI))**:
> Have you worked with multi-agent orchestration frameworks — LangGraph, CrewAI?

**`[T-A3]` Candidate Response *(Self-Disclosed Gap)***:
> Not in production. I've read through the docs for both and built a small planner/executor toy project on my own time, but everything I've actually shipped has been single-agent RAG. That's a real gap relative to what this role needs, and I'd rather say that clearly than talk around it.

**`[T-Q4]` Question (Approach to ramping up on multi-agent systems) *(Follow-up)***:
> How would you approach ramping up on multi-agent systems specifically?

**`[T-A4]` Candidate Response**:
> I'd start by reading through your existing planner/executor/reviewer code directly, rather than a general course, since the real failure patterns usually aren't in the docs. Then I'd want to pair with someone on a small bug fix first, before touching the architecture itself.

### 2.2 Behavioral & Friction Events
- **Friction / Mistake Event `[T-A5]`**:
  > "I pushed a prompt change to the support assistant straight to production — we didn't have a review process at the time, so nothing stopped me. It caused a spike in bad responses for about two hours before we caught it and rolled back."
- **Skeptic Follow-up Response `[T-A7]`** (Word count: 41, Defensiveness: `low`):
  > "No, I named it as mine in the retro doc. One teammate pointed out we should've had the checklist before this happened, which is fair — but I didn't try to shift blame for the specific incident onto the process gap."
- **Behavioral Analysis Note**: Directly owned production outage and instituted pre-deploy checklist without shifting blame.

### 2.3 Ownership & Career Trajectory Q&A
- **`[T-A8]` Gap Probed**: *production multi-agent experience* (Response Style: `direct_acknowledgment`)
  - **Summary**: Directly acknowledges missing production multi-agent experience; highlights fast ramp track record and willingness to ask for help.
  - **Verbatim Quote**: > "It's real, and I'd rather you go in with clear eyes about it than find out later. What I'd point to instead is a pattern: I've picked up new technical areas quickly before — OCR pipelines, then RAG — and I tend to ask for help early instead of quietly struggling, which I think matters more for ramp time than having already touched this exact framework."
- **`[T-A9]` Gap Probed**: *ramp-up ROI vs experienced candidate* (Response Style: `direct_acknowledgment`)
  - **Summary**: Positions self as safer bet on long-term production reliability and incident ownership over demo-focused engineers.
  - **Verbatim Quote**: > "Honestly, I can't out-argue someone who's already done the exact work. What I'd say is I'm a safer bet on the production-ownership side — I've been through a real incident and changed how the team works because of it, not just shipped something that looked good in a demo."
- **`[T-A10]` Gap Probed**: *6-year single company tenure and startup adaptation* (Response Style: `direct_acknowledgment`)
  - **Summary**: Explains continuous role evolution and internal adaptation from junior backend to AI lead.
  - **Verbatim Quote**: > "It's a fair thing to ask about. I'd say the role itself changed a lot even though the employer didn't — I went from junior backend work, to leading a pipeline migration, to driving our team's move into AI. So I've had to keep adapting, just inside one company."

## 3. Resume vs. Transcript Consistency Cross-Checks
- **[FLAG - Severity: `LOW`]** Claim `[R-EXP-03]` vs. Interview `[T-A2]`
  - **Discrepancy**: Resume claims ~40% accuracy improvement; in interview candidate clarifies this was an informal spot-check rather than a rigorous benchmark.

## 4. Master Citation Index (Lookup Table)
| Citation ID | Source Content Summary |
|---|---|
| `R-EDU-01` | B.E. Information Technology (University of Mumbai, 2019) |
| `R-EXP-01` | [Bridgepoint Systems - Software Engineer II] Maintains Python/FastAPI microservices for an internal ops platform used by a few internal teams. |
| `R-EXP-02` | [Bridgepoint Systems - Software Engineer II] Helped migrate part of the document ingestion pipeline to use OCR-based extraction for scanned forms. |
| `R-EXP-03` | [Bridgepoint Systems - Software Engineer II] Over the last 1.5 years, started building an internal RAG-based support-ticket assistant: set up a retrieval pipeline (LangChain + Chroma); team estimated answer accuracy improved by around 40% based on informal review. |
| `R-EXP-04` | [Bridgepoint Systems - Software Engineer II] After a production incident (see interview), introduced a pre-deploy checklist for prompt changes that the team adopted. |
| `R-EXP-05` | [Bridgepoint Systems - Junior Backend Developer] Built basic REST APIs for internal tooling. |
| `R-EXP-06` | [Bridgepoint Systems - Junior Backend Developer] Worked with QA and product to define API contracts. |
| `T-A1` | Answer (RAG support-ticket assistant architecture): Sure — happy to walk through it step by step. We retrieve from a Chroma vector store built from past resolved tickets and internal docs. The top few matches get passed to the LLM, which drafts a response for a human agent to review before it goes out. We chunked documents by section rather than fixed length, since that kept related context together. |
| `T-A10` | Gap probed [6-year single company tenure and startup adaptation] (direct_acknowledgment): Explains continuous role evolution and internal adaptation from junior backend to AI lead. |
| `T-A2` | Answer (40% accuracy improvement metric measurement): I want to be upfront about this — it was based on internal review, not a formal benchmark. A few of us spot-checked a sample of responses before and after the change and it felt clearly better, but I wouldn't want to present that number as something rigorous if it comes up again. |
| `T-A3` | Answer (Multi-agent orchestration frameworks (LangGraph, CrewAI)): Not in production. I've read through the docs for both and built a small planner/executor toy project on my own time, but everything I've actually shipped has been single-agent RAG. That's a real gap relative to what this role needs, and I'd rather say that clearly than talk around it. |
| `T-A4` | Answer (Approach to ramping up on multi-agent systems): I'd start by reading through your existing planner/executor/reviewer code directly, rather than a general course, since the real failure patterns usually aren't in the docs. Then I'd want to pair with someone on a small bug fix first, before touching the architecture itself. |
| `T-A5` | I pushed a prompt change to the support assistant straight to production — we didn't have a review process at the time, so nothing stopped me. It caused a spike in bad responses for about two hours before we caught it and rolled back. |
| `T-A6` | Ran incident retro, acknowledged mistake in writeup, proposed pre-deploy checklist with eval set. |
| `T-A7` | No, I named it as mine in the retro doc. One teammate pointed out we should've had the checklist before this happened, which is fair — but I didn't try to shift blame for the specific incident onto the process gap. |
| `T-A8` | Gap probed [production multi-agent experience] (direct_acknowledgment): Directly acknowledges missing production multi-agent experience; highlights fast ramp track record and willingness to ask for help. |
| `T-A9` | Gap probed [ramp-up ROI vs experienced candidate] (direct_acknowledgment): Positions self as safer bet on long-term production reliability and incident ownership over demo-focused engineers. |
| `T-Q1` | Question (RAG support-ticket assistant architecture): Tell me about the RAG pipeline you built for the support-ticket assistant. |
| `T-Q10` | You've been at one company for six years. Any concern about adapting to a fast-moving startup environment? |
| `T-Q2` | Question (40% accuracy improvement metric measurement): Your resume mentions a ~40% accuracy improvement. How was that measured? |
| `T-Q3` | Question (Multi-agent orchestration frameworks (LangGraph, CrewAI)): Have you worked with multi-agent orchestration frameworks — LangGraph, CrewAI? |
| `T-Q4` | Question (Approach to ramping up on multi-agent systems): How would you approach ramping up on multi-agent systems specifically? |
| `T-Q5` | Tell me about a mistake you made and how you handled it. |
| `T-Q6` | What did you do after that? |
| `T-Q7` | Was there any pushback on you owning that mistake publicly, or did you find a way to spread the responsibility? |
| `T-Q8` | This role is heavily oriented around multi-agent orchestration on day one. Given you haven't shipped that in production, how do you think about that gap? |
| `T-Q9` | Why should we invest in ramping you up here versus someone who already has multi-agent experience? |