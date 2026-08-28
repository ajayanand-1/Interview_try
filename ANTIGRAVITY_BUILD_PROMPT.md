# Build Prompt — paste into Antigravity CLI

Read `PRD_interview_panel_simulator.md` in this repo fully before writing any code. It is the source of truth — follow it section by section. Anything tagged `[REQUIRED]` is non-negotiable. Anything tagged `[DESIGN CHOICE]` you may implement more cleanly if you have a good reason, but don't silently change the observable behavior it describes.

Build in this order. Stop and show me your plan for each phase before writing code for it.

**Phase 0 — Scaffold**
Set up a Python project (venv or uv), the directory layout from PRD §13 (`rosetta/`, `memos/`, `debate/`, `reports/`), Gemini API key config, and `pydantic` models for every JSON schema in PRD §6 and §7.

**Phase 1 — Candidate Profile Builder**
Parse `data/job_description.pdf`, `data/{candidate}_resume.pdf`, and `data/{candidate}_transcript.pdf` into the Rosetta JSON schema (PRD §6). Every extracted fact gets a stable citation ID. Also emit a human-readable `rosetta/{candidate}.md`.

**Phase 2 — Independent Agents**
Implement the four personas from PRD §7 as isolated, independent Gemini API calls — a fresh session each time, with only the Rosetta doc + JD as input. Write and run the isolation test from PRD §15: assert no persona's call payload contains another persona's output. Each persona writes a sealed `memos/{persona}.json` + `.pdf`.

**Phase 3 — Debate Orchestrator**
Implement the General Secretary per PRD §9: agenda generation from the four sealed memos, one turn per agent per agenda item, counter-questions, free-for-all with per-round integer voting, the unanimous auto-resolve thresholds, and the maturity heuristic. Log every turn to `debate/{candidate}_transcript.json`.

**Phase 4 — Decision & Report**
Implement PRD §10 (General Secretary's final decision + the override-motion mechanic) and §11 (report generator → PDF + Markdown). Every claim in the report must resolve to a Rosetta citation ID — this is the §15 traceability test.

**Phase 5 — Edge cases & tests**
Implement PRD §12's edge cases and the full §15 test suite. Run both candidates end-to-end, unattended.

**Phase 6 (optional — only if 0–5 are solid and time remains)**
Voice debate stretch feature per PRD §16.

Hard constraints, everywhere:
- No agent may share context, session, or memory with another agent before the debate stage. Enforce this in code, not just in the prompt.
- Never fabricate a score when evidence is insufficient — use the explicit `insufficient_evidence` state from PRD §12.
- Every phase's output must be an inspectable file on disk, not something that only exists in memory — I need to grade and demo each phase independently.

Start with Phase 0 and show me the plan before writing any code.
