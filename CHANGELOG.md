# Project Rosetta / Prompt Wars — Enhancement Changelog

This document tracks all new features, architecture extensions, data models, UI components, voice integrations, and improvements added to the **Prompt Wars (Project Rosetta)** codebase relative to the upstream repository [`neednotbenamed/promptwars`](https://github.com/neednotbenamed/promptwars).

---

## 🌟 Summary of Key Enhancements

| Category | Upstream State (`neednotbenamed/promptwars`) | Enhanced State (`ajayanand-1/Interview_try`) |
|---|---|---|
| **AI Agent Personas & Fixed Gender Voices** | Generic agent labels, no gender balance | **5 Fixed Persona Profiles (2 Female, 2 Male, 1 Moderator)**: Dr. Maya Lin (♀ Technical), Dr. Rachel Thorne (♀ Skeptic), Marcus Vance (♂ HR), David Sterling (♂ Hiring Manager), Arthur Pendelton (♂ Chair) with immutable distinct voices. |
| **Civil Parliamentary Deliberation** | Standard text dialogue | **Extremely Civil, Non-Overlapping Deliberation** systematically covering: (1) Core Problem, (2) Role Expectations, (3) Grounded Pros & Cons, and (4) Viable Solutions. |
| **Interactive Voice Stream Player** | Basic CLI audio script | **Web Speech API In-Browser Player** providing sequential, non-overlapping audio streaming across female and male timbres with active-speaker waveform highlights. |
| **Responsive Web Design** | Desktop-focused layout | **Universal Multi-Device Responsive UI** with mobile drawer navigation, hamburger menu, touch-friendly tab scrolling, and adaptive responsive card grids (`sm:`, `md:`, `lg:`). |
| **Candidate Feedback Engine** | Not present | **Multi-Persona Candidate Feedback & Growth Playbook** synthesizing actionable guidance from HR, Skeptic, Hiring Manager, Technical, and General Secretary. |
| **Resume Rewriting Guide** | Not present | **Evidence-grounded Resume Improvements** with Identified Issues, Actionable Recommendations, and side-by-side **Before vs. After rewrite examples**. |
| **Target Job Skills Roadmap** | Basic memo gaps | **Structured Capabilities Roadmap** mapping Company Expectations, Verified Candidate Levels, and Concrete Growth Paths. |
| **Company Expectations Guide** | Implicit in memos | **Explicit Organizational Standards** analyzing Accountability, Retention, Scientific Rigor, and Future Interview Advice. |
| **API Endpoints** | Standard phase endpoints | Added dedicated **`GET /api/evaluations/{run_id}/feedback`** with full Pydantic schema validation. |
| **PDF & Markdown Deliverables** | Executive Decision & Citations | Expanded to include **Candidate Feedback & Growth Playbook** directly in generated Markdown and ReportLab PDFs. |
| **Automated Testing** | 47 tests | **55 Comprehensive Unit, Integration, and Traceability Tests** passing cleanly. |

---

## 🎭 Fixed AI Agent Persona & Voice Roster

The deliberation panel enforces a strict 2-Female / 2-Male evaluator structure plus an impartial Chair:

1. **Dr. Maya Lin** — `technical_agent`
   - **Gender**: ♀ Female
   - **Voice**: `Karen` / Synthesis Female
   - **Role**: Lead AI Systems Architect
   - **Persona**: Analytical, methodical, precise software architect focusing on retrieval pipelines, graph concurrency, and execution correctness.

2. **Marcus Vance** — `hr_culture_agent`
   - **Gender**: ♂ Male
   - **Voice**: `Oliver` / Synthesis Male
   - **Role**: Head of People & Organizational Culture
   - **Persona**: Empathetic, psychologically perceptive, assessing ownership during outages, communication clarity, and psychological safety.

3. **David Sterling** — `hiring_manager_agent`
   - **Gender**: ♂ Male
   - **Voice**: `Fred` / Synthesis Male
   - **Role**: VP of Engineering & Product Delivery
   - **Persona**: Pragmatic, ROI-driven business leader assessing ramp-up costs, payroll risk, and multi-year retention horizons.

4. **Dr. Rachel Thorne** — `skeptic_agent`
   - **Gender**: ♀ Female
   - **Voice**: `Samantha` / Synthesis Female
   - **Role**: Principal Forensic Auditor & Critic
   - **Persona**: Disciplined, forensic investigator probing unverified metrics, inflated claims, and attribution discrepancies with polite tenacity.

5. **Arthur Pendelton** — `general_secretary`
   - **Gender**: ♂ Male
   - **Voice**: `Daniel` / Synthesis Male Chair
   - **Role**: Panel Moderator & Chief Adjudicator
   - **Persona**: Impartial, structured chair enforcing civil parliamentary order, managing round transitions, and synthesizing binding verdicts.

---

## 🏛️ Structured 4-Pillar Civil Discussion Framework

Every debate round and turn is structured around four essential pillars without overlapping or contentious shouting:
- 🎯 **1. The Problem**: Precise technical, cultural, or business challenge faced by the engineering platform.
- 📋 **2. Role Expectation**: The standard and competency required by the hiring company.
- ⚖️ **3. Pros and Cons**: Evidence-grounded assessment citing verified candidate strengths vs. identified risk factors.
- 💡 **4. Viable Solutions**: Actionable onboarding remedies, pair programming plans, CI evaluation harnesses, or architectural mitigations.

---

## 📱 Mobile & Multi-Device Responsiveness

- **Collapsible Mobile Drawer Sidebar**: Touch-friendly navigation menu with slide-in drawer and backdrop overlay on mobile/tablet viewports.
- **Responsive Topbar**: Mobile hamburger toggle, adaptive search input width, and condensed action buttons.
- **Adaptive Card & Table Layouts**: Grids automatically adjust (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-3/5`) with horizontal touch scrolling for data tables.
- **Touch Targets**: All interactive buttons, tabs, and citation pills are optimized for mobile touch ergonomics (minimum 44px hit zones).

---

## 👤 Original Author Attribution
- **Original Author**: [`neednotbenamed`](https://github.com/neednotbenamed)
- **Original Upstream Repository**: [https://github.com/neednotbenamed/promptwars](https://github.com/neednotbenamed/promptwars)
