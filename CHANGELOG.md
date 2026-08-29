# Project Rosetta / Prompt Wars — Enhancement Changelog

This document tracks all new features, architecture extensions, data models, UI components, neural voice integrations, and improvements added to the **Prompt Wars (Project Rosetta)** codebase relative to the upstream repository [`neednotbenamed/promptwars`](https://github.com/neednotbenamed/promptwars).

---

## 🌟 Summary of Key Enhancements

| Category | Upstream State (`neednotbenamed/promptwars`) | Enhanced State (`ajayanand-1/Interview_try`) |
|---|---|---|
| **Human-Grade Neural Voices** | Basic robotic synthesizer | **Studio-Grade Microsoft Edge Neural Voices** with custom pitch, rate, and breathing prosody for 100% human realism. |
| **Neural Audio Streaming API** | Not present | Added **`GET /api/evaluations/{run_id}/debate/audio/{round_idx}/{turn_idx}`** and **`POST /api/speech/synthesize`** streaming high-bitrate MP3 audio. |
| **Speech Text Normalization** | Not present | **Natural Speech Prosody Cleaner** stripping bracketed citation codes (`[T-A1]`, `[R-EXP-04]`) and formatting so voices sound natural and conversational. |
| **AI Agent Personas & Fixed Gender Voices** | Generic agent labels, no gender balance | **5 Fixed Persona Profiles (2 Female, 2 Male, 1 Moderator)**: Dr. Maya Lin (♀ Technical), Dr. Rachel Thorne (♀ Skeptic), Marcus Vance (♂ HR), David Sterling (♂ Hiring Manager), Arthur Pendelton (♂ Chair) with immutable distinct voices. |
| **Civil Parliamentary Deliberation** | Standard text dialogue | **Extremely Civil, Non-Overlapping Deliberation** systematically covering: (1) Core Problem, (2) Role Expectations, (3) Grounded Pros & Cons, and (4) Viable Solutions. |
| **Turn-by-Turn Voice Player** | Basic CLI script | **In-Browser Audio Player with Turn-by-Turn Listen Buttons** providing sequential neural streaming, active speaker equalizer waves, and pause/resume/stop controls. |
| **Responsive Web Design** | Desktop-focused layout | **Universal Multi-Device Responsive UI** with mobile drawer navigation, hamburger menu, touch-friendly tab scrolling, and adaptive responsive card grids (`sm:`, `md:`, `lg:`). |
| **Candidate Feedback Engine** | Not present | **Multi-Persona Candidate Feedback & Growth Playbook** synthesizing actionable guidance from HR, Skeptic, Hiring Manager, Technical, and General Secretary. |
| **Resume Rewriting Guide** | Not present | **Evidence-grounded Resume Improvements** with Identified Issues, Actionable Recommendations, and side-by-side **Before vs. After rewrite examples**. |
| **Target Job Skills Roadmap** | Basic memo gaps | **Structured Capabilities Roadmap** mapping Company Expectations, Verified Candidate Levels, and Concrete Growth Paths. |
| **Company Expectations Guide** | Implicit in memos | **Explicit Organizational Standards** analyzing Accountability, Retention, Scientific Rigor, and Future Interview Advice. |
| **API Endpoints** | Standard phase endpoints | Added dedicated **`GET /api/evaluations/{run_id}/feedback`** and neural audio endpoints. |
| **PDF & Markdown Deliverables** | Executive Decision & Citations | Expanded to include **Candidate Feedback & Growth Playbook** directly in generated Markdown and ReportLab PDFs. |
| **Automated Testing** | 47 tests | **57 Comprehensive Unit, Integration, Voice, and Traceability Tests** passing cleanly. |

---

## 🎭 Ultra-Realistic Human Neural Voice Mapping

| Evaluator Persona | Assigned Gender | High-Definition Neural Voice Profile | Prosody Tuning | Personality & Natural Timbre |
|---|---|---|---|---|
| **Dr. Maya Lin** (`technical_agent`) | **♀ Female** | `en-US-AriaNeural` | Pitch: `+0Hz`, Rate: `+0%` | Studio clarity, analytical precision, measured and articulate AI systems architect. |
| **Marcus Vance** (`hr_culture_agent`) | **♂ Male** | `en-US-GuyNeural` | Pitch: `-1Hz`, Rate: `-2%` | Warm, conversational, resonant, empathetic tone focusing on team culture. |
| **David Sterling** (`hiring_manager_agent`) | **♂ Male** | `en-US-ChristopherNeural` | Pitch: `-2Hz`, Rate: `+1%` | Executive, confident, pragmatic, decisive VP evaluating delivery velocity & ROI. |
| **Dr. Rachel Thorne** (`skeptic_agent`) | **♀ Female** | `en-US-JennyNeural` | Pitch: `+1Hz`, Rate: `-1%` | Forensic, crisp, disciplined, calm, and tenacious code & evidence auditor. |
| **Arthur Pendelton** (`general_secretary`) | **♂ Male** | `en-GB-RyanNeural` | Pitch: `-2Hz`, Rate: `-3%` | Authoritative, distinguished British parliamentary moderator and chief adjudicator. |

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
- **Responsive Topbar**: Mobile hamburger menu trigger, adaptive search input width, and compact action buttons.
- **Adaptive Card & Table Layouts**: Grids automatically adjust (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-3/5`) with horizontal touch scrolling for data tables.
- **Touch Ergonomics**: All buttons, tabs, and interactive citation tags have touch-friendly hit areas ($\ge 44	ext{px}$).

---

## 👤 Original Author Attribution
- **Original Author**: [`neednotbenamed`](https://github.com/neednotbenamed)
- **Original Upstream Repository**: [https://github.com/neednotbenamed/promptwars](https://github.com/neednotbenamed/promptwars)
