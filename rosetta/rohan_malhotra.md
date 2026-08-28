# Rosetta Document — Candidate Profile: Rohan Malhotra
**Candidate ID**: `rohan_malhotra` | **Target Role**: `AI Engineer — Agentic Systems`

> **Note for Evaluating Agents**: Every evaluation claim, strength, gap, and vote in your memos and debate MUST cite one of the stable citation IDs (`[R-EXP-xx]`, `[T-Axx]`, etc.) indexed in this document.

---
## 1. Resume Facts
### 1.1 Education
- **`[R-EDU-01]`** B.Tech Computer Science, Indian Institute of Technology (2022)

### 1.2 Professional Experience
#### Senior AI Engineer — Voltrix Logistics Tech (2025-01 – present, 0.58 yrs)
- **`[R-EXP-01]`** Designed and built the exception-handling engine end-to-end for Voltrix's multi-agent freight ops platform (planner/executor/reviewer pattern), cutting manual exception review time by 40%.
- **`[R-EXP-02]`** Owned prompt design and model routing across GPT-4 and open-weight SLMs, reducing inference cost by ~30%.
- **`[R-EXP-03]`** Sole architect of the retry/escalation logic now running in production, handling 5,000+ freight exceptions/month.
- **`[R-EXP-04]`** Presented the system design at a company-wide tech talk.

#### AI Engineer — Quickship Data Systems (2024-02 – 2024-12, 0.92 yrs)
- **`[R-EXP-05]`** Built a RAG pipeline over carrier rate documents using LangChain + Pinecone, cutting manual rate lookup time significantly.
- **`[R-EXP-06]`** Improved BOL/invoice extraction accuracy through better OCR pre-processing.

#### Backend Developer — Nimbus Cloud Solutions (2022-08 – 2024-01, 1.5 yrs)
- **`[R-EXP-07]`** Built Python microservices for a SaaS analytics product used by 50+ enterprise clients.
- **`[R-EXP-08]`** Led a 4-person team migrating a legacy monolith to microservices.

### 1.3 Technical Skills & Certifications
- **Core Skills**: Python, FastAPI, LangGraph, CrewAI, MongoDB, React (basic), RAG, Vector Search (Pinecone, FAISS), Prompt Engineering, Docker, Kubernetes
- **Certifications**: LangChain for LLM Application Development (2024)

## 2. Interview Transcript Facts
### 2.1 Technical Q&A
**`[T-Q1]` Question (Voltrix exception-handling engine architecture)**:
> Walk me through the exception-handling engine you built at Voltrix.

**`[T-A1]` Candidate Response**:
> It's planner-executor-reviewer. Failures come in, get classified, retried or escalated, then double-checked. I designed the whole retry/escalation logic.

**`[T-Q2]` Question (Architecture choice over rule-based system)**:
> What made you choose that structure over a simpler rule-based system?

**`[T-A2]` Candidate Response**:
> Rules don't scale. Too many failure types — timeouts, bad EDI, missing BOL fields. Agents handle that better.

**`[T-Q3]` Question (Reviewer agent evaluation and verification metrics) *(Follow-up)***:
> How do you measure whether the reviewer agent is actually catching real problems?

**`[T-A3]` Candidate Response**:
> We track override rate. It's low. I'd have to check the exact number though, haven't looked recently.

**`[T-Q4]` Question (Model routing and cost optimization approach)**:
> What's your approach to model routing?

**`[T-A4]` Candidate Response**:
> Cost-based. Simple stuff to the SLM, harder reasoning to GPT-4. No formal study, just tuned it as things broke.

### 2.2 Behavioral & Friction Events
- **Friction / Mistake Event `[T-A5]`**:
  > "Teammate wanted to hardcode more categories up front. I pushed for the agent approach. We went with mine."
- **Skeptic Follow-up Response `[T-A7]`** (Word count: 19, Defensiveness: `medium`):
  > "Fine — 'sole architect' is probably too strong. I led the design, she built most of the production version."
- **Behavioral Analysis Note**: Conceded under skeptic cross-examination that 'sole architect' resume claim overstated role relative to teammate Priya's production implementation.

### 2.3 Ownership & Career Trajectory Q&A
- **`[T-A8]` Gap Probed**: *freight-domain ramp-up vs experienced domain engineers* (Response Style: `direct_acknowledgment`)
  - **Summary**: Asserter of fast ramp time based on structural similarity of previous work.
  - **Verbatim Quote**: > "I move fast. I've built something structurally close to this already. I don't think I'd need much ramp time."
- **`[T-A9]` Gap Probed**: *production reliability and on-call ownership* (Response Style: `partial`)
  - **Summary**: Acknowledges limited production incident volume due to Voltrix's small user base.
  - **Verbatim Quote**: > "Fine, I've done on-call before. Though Voltrix's user base is still small, so I haven't seen serious incident volume yet."
- **`[T-A10]` Gap Probed**: *frequent job-hopping tenure pattern (3 jobs in 3.5 years)* (Response Style: `direct_acknowledgment`)
  - **Summary**: Directly attributes frequent moves to pursuing better pay and title.
  - **Verbatim Quote**: > "Better pay and title, mostly. Voltrix is more aligned with what I want long-term."

## 3. Resume vs. Transcript Consistency Cross-Checks
- **[FLAG - Severity: `HIGH`]** Claim `[R-EXP-03]` vs. Interview `[T-A7]`
  - **Discrepancy**: Resume claimed 'Sole architect of the retry/escalation logic now running in production'; during cross-examination in T-A7 conceded: "Fine — 'sole architect' is probably too strong. I led the design, she built most of the production version."

## 4. Master Citation Index (Lookup Table)
| Citation ID | Source Content Summary |
|---|---|
| `R-EDU-01` | B.Tech Computer Science (Indian Institute of Technology, 2022) |
| `R-EXP-01` | [Voltrix Logistics Tech - Senior AI Engineer] Designed and built the exception-handling engine end-to-end for Voltrix's multi-agent freight ops platform (planner/executor/reviewer pattern), cutting manual exception review time by 40%. |
| `R-EXP-02` | [Voltrix Logistics Tech - Senior AI Engineer] Owned prompt design and model routing across GPT-4 and open-weight SLMs, reducing inference cost by ~30%. |
| `R-EXP-03` | [Voltrix Logistics Tech - Senior AI Engineer] Sole architect of the retry/escalation logic now running in production, handling 5,000+ freight exceptions/month. |
| `R-EXP-04` | [Voltrix Logistics Tech - Senior AI Engineer] Presented the system design at a company-wide tech talk. |
| `R-EXP-05` | [Quickship Data Systems - AI Engineer] Built a RAG pipeline over carrier rate documents using LangChain + Pinecone, cutting manual rate lookup time significantly. |
| `R-EXP-06` | [Quickship Data Systems - AI Engineer] Improved BOL/invoice extraction accuracy through better OCR pre-processing. |
| `R-EXP-07` | [Nimbus Cloud Solutions - Backend Developer] Built Python microservices for a SaaS analytics product used by 50+ enterprise clients. |
| `R-EXP-08` | [Nimbus Cloud Solutions - Backend Developer] Led a 4-person team migrating a legacy monolith to microservices. |
| `T-A1` | Answer (Voltrix exception-handling engine architecture): It's planner-executor-reviewer. Failures come in, get classified, retried or escalated, then double-checked. I designed the whole retry/escalation logic. |
| `T-A10` | Gap probed [frequent job-hopping tenure pattern (3 jobs in 3.5 years)] (direct_acknowledgment): Directly attributes frequent moves to pursuing better pay and title. |
| `T-A2` | Answer (Architecture choice over rule-based system): Rules don't scale. Too many failure types — timeouts, bad EDI, missing BOL fields. Agents handle that better. |
| `T-A3` | Answer (Reviewer agent evaluation and verification metrics): We track override rate. It's low. I'd have to check the exact number though, haven't looked recently. |
| `T-A4` | Answer (Model routing and cost optimization approach): Cost-based. Simple stuff to the SLM, harder reasoning to GPT-4. No formal study, just tuned it as things broke. |
| `T-A5` | Teammate wanted to hardcode more categories up front. I pushed for the agent approach. We went with mine. |
| `T-A6` | I designed it. Priya did a lot of the implementation, I reviewed her PRs. I was the architect. |
| `T-A7` | Fine — 'sole architect' is probably too strong. I led the design, she built most of the production version. |
| `T-A8` | Gap probed [freight-domain ramp-up vs experienced domain engineers] (direct_acknowledgment): Asserter of fast ramp time based on structural similarity of previous work. |
| `T-A9` | Gap probed [production reliability and on-call ownership] (partial): Acknowledges limited production incident volume due to Voltrix's small user base. |
| `T-Q1` | Question (Voltrix exception-handling engine architecture): Walk me through the exception-handling engine you built at Voltrix. |
| `T-Q10` | You've had three roles in 3.5 years, each under a year except the first. What's driving that? |
| `T-Q2` | Question (Architecture choice over rule-based system): What made you choose that structure over a simpler rule-based system? |
| `T-Q3` | Question (Reviewer agent evaluation and verification metrics): How do you measure whether the reviewer agent is actually catching real problems? |
| `T-Q4` | Question (Model routing and cost optimization approach): What's your approach to model routing? |
| `T-Q5` | Tell me about a time you disagreed with a teammate on a technical decision. |
| `T-Q6` | Who actually wrote the retry/escalation logic that's in production now? |
| `T-Q7` | Your resume says 'sole architect.' But it sounds like Priya built a lot of it. Can you clarify? |
| `T-Q8` | Why should we invest in ramping you up here versus someone with more freight-domain experience? |
| `T-Q9` | This role needs long-term ownership of production reliability. How do you feel about being on-call for agent failures? |