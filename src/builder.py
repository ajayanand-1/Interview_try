"""Candidate Profile Builder ("Project Rosetta") - PRD §6."""

import sys
from pathlib import Path

# Ensure repo root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import json
import re
from typing import Dict, List, Optional, Tuple
import pypdf

from src.config import settings
from src.models.rosetta import (
    RosettaDocument,
    ResumeFacts,
    TranscriptFacts,
    EducationFact,
    ExperienceFact,
    ExperienceClaim,
    TechnicalQA,
    BehavioralFacts,
    OwnershipHiringQA,
    ConsistencyFlag,
)
from src.utils.citations import build_citations_index


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract raw text from a PDF file."""
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    reader = pypdf.PdfReader(str(pdf_path))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages_text)


def parse_ananya_iyer_data(data_dir: Path) -> RosettaDocument:
    """Parse Ananya Iyer's resume and interview transcript into RosettaDocument."""
    candidate_id = "ananya_iyer"
    candidate_name = "Ananya Iyer"

    # Resume Facts
    education = [
        EducationFact(
            degree="B.E. Information Technology",
            institution="University of Mumbai",
            year=2019,
            citation_id="R-EDU-01"
        )
    ]

    exp_1 = ExperienceFact(
        company="Bridgepoint Systems",
        role="Software Engineer II",
        start="2021-06",
        end="present",
        tenure_years=4.0,
        claims=[
            ExperienceClaim(
                text="Maintains Python/FastAPI microservices for an internal ops platform used by a few internal teams.",
                citation_id="R-EXP-01"
            ),
            ExperienceClaim(
                text="Helped migrate part of the document ingestion pipeline to use OCR-based extraction for scanned forms.",
                citation_id="R-EXP-02"
            ),
            ExperienceClaim(
                text="Over the last 1.5 years, started building an internal RAG-based support-ticket assistant: set up a retrieval pipeline (LangChain + Chroma); team estimated answer accuracy improved by around 40% based on informal review.",
                citation_id="R-EXP-03"
            ),
            ExperienceClaim(
                text="After a production incident (see interview), introduced a pre-deploy checklist for prompt changes that the team adopted.",
                citation_id="R-EXP-04"
            )
        ]
    )

    exp_2 = ExperienceFact(
        company="Bridgepoint Systems",
        role="Junior Backend Developer",
        start="2019-07",
        end="2021-06",
        tenure_years=2.0,
        claims=[
            ExperienceClaim(
                text="Built basic REST APIs for internal tooling.",
                citation_id="R-EXP-05"
            ),
            ExperienceClaim(
                text="Worked with QA and product to define API contracts.",
                citation_id="R-EXP-06"
            )
        ]
    )

    skills = [
        "Python", "FastAPI", "MongoDB", "PostgreSQL", "LangChain", "Chroma",
        "basic React", "OCR pipelines (Tesseract)", "Docker"
    ]
    certifications = []

    resume_facts = ResumeFacts(
        education=education,
        experience=[exp_1, exp_2],
        skills=skills,
        certifications=certifications
    )

    # Transcript Facts
    technical_qa = [
        TechnicalQA(
            qid="T-Q1",
            topic="RAG support-ticket assistant architecture",
            question="Tell me about the RAG pipeline you built for the support-ticket assistant.",
            answer="Sure — happy to walk through it step by step. We retrieve from a Chroma vector store built from past resolved tickets and internal docs. The top few matches get passed to the LLM, which drafts a response for a human agent to review before it goes out. We chunked documents by section rather than fixed length, since that kept related context together.",
            answer_citation_id="T-A1",
            is_followup=False,
            influenced_by=None,
            self_disclosed_gap=False
        ),
        TechnicalQA(
            qid="T-Q2",
            topic="40% accuracy improvement metric measurement",
            question="Your resume mentions a ~40% accuracy improvement. How was that measured?",
            answer="I want to be upfront about this — it was based on internal review, not a formal benchmark. A few of us spot-checked a sample of responses before and after the change and it felt clearly better, but I wouldn't want to present that number as something rigorous if it comes up again.",
            answer_citation_id="T-A2",
            is_followup=True,
            influenced_by="T-Q1",
            self_disclosed_gap=True
        ),
        TechnicalQA(
            qid="T-Q3",
            topic="Multi-agent orchestration frameworks (LangGraph, CrewAI)",
            question="Have you worked with multi-agent orchestration frameworks — LangGraph, CrewAI?",
            answer="Not in production. I've read through the docs for both and built a small planner/executor toy project on my own time, but everything I've actually shipped has been single-agent RAG. That's a real gap relative to what this role needs, and I'd rather say that clearly than talk around it.",
            answer_citation_id="T-A3",
            is_followup=False,
            influenced_by=None,
            self_disclosed_gap=True
        ),
        TechnicalQA(
            qid="T-Q4",
            topic="Approach to ramping up on multi-agent systems",
            question="How would you approach ramping up on multi-agent systems specifically?",
            answer="I'd start by reading through your existing planner/executor/reviewer code directly, rather than a general course, since the real failure patterns usually aren't in the docs. Then I'd want to pair with someone on a small bug fix first, before touching the architecture itself.",
            answer_citation_id="T-A4",
            is_followup=True,
            influenced_by="T-Q3",
            self_disclosed_gap=False
        )
    ]

    skeptic_answer_text = "No, I named it as mine in the retro doc. One teammate pointed out we should've had the checklist before this happened, which is fair — but I didn't try to shift blame for the specific incident onto the process gap."
    skeptic_word_count = len(skeptic_answer_text.split())

    behavioral = BehavioralFacts(
        friction_event_citation_id="T-A5",
        friction_event_quote="I pushed a prompt change to the support assistant straight to production — we didn't have a review process at the time, so nothing stopped me. It caused a spike in bad responses for about two hours before we caught it and rolled back.",
        skeptic_followup_citation_id="T-A7",
        skeptic_followup_quote=skeptic_answer_text,
        skeptic_followup_word_count=skeptic_word_count,
        skeptic_followup_defensiveness="low",
        friction_notes="Directly owned production outage and instituted pre-deploy checklist without shifting blame."
    )

    ownership_hiring_qa = [
        OwnershipHiringQA(
            qid="T-Q8",
            gap_probed="production multi-agent experience",
            response_summary="Directly acknowledges missing production multi-agent experience; highlights fast ramp track record and willingness to ask for help.",
            response_quote="It's real, and I'd rather you go in with clear eyes about it than find out later. What I'd point to instead is a pattern: I've picked up new technical areas quickly before — OCR pipelines, then RAG — and I tend to ask for help early instead of quietly struggling, which I think matters more for ramp time than having already touched this exact framework.",
            response_style="direct_acknowledgment",
            citation_id="T-A8"
        ),
        OwnershipHiringQA(
            qid="T-Q9",
            gap_probed="ramp-up ROI vs experienced candidate",
            response_summary="Positions self as safer bet on long-term production reliability and incident ownership over demo-focused engineers.",
            response_quote="Honestly, I can't out-argue someone who's already done the exact work. What I'd say is I'm a safer bet on the production-ownership side — I've been through a real incident and changed how the team works because of it, not just shipped something that looked good in a demo.",
            response_style="direct_acknowledgment",
            citation_id="T-A9"
        ),
        OwnershipHiringQA(
            qid="T-Q10",
            gap_probed="6-year single company tenure and startup adaptation",
            response_summary="Explains continuous role evolution and internal adaptation from junior backend to AI lead.",
            response_quote="It's a fair thing to ask about. I'd say the role itself changed a lot even though the employer didn't — I went from junior backend work, to leading a pipeline migration, to driving our team's move into AI. So I've had to keep adapting, just inside one company.",
            response_style="direct_acknowledgment",
            citation_id="T-A10"
        )
    ]

    transcript_facts = TranscriptFacts(
        technical_qa=technical_qa,
        behavioral=behavioral,
        ownership_hiring_qa=ownership_hiring_qa
    )

    consistency_flags = [
        ConsistencyFlag(
            claim_citation_id="R-EXP-03",
            transcript_citation_id="T-A2",
            description="Resume claims ~40% accuracy improvement; in interview candidate clarifies this was an informal spot-check rather than a rigorous benchmark.",
            severity="low"
        )
    ]

    rosetta = RosettaDocument(
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        resume_facts=resume_facts,
        transcript_facts=transcript_facts,
        consistency_flags=consistency_flags
    )
    rosetta.citations_index = build_citations_index(rosetta)
    # Add behavioral citations specifically
    rosetta.citations_index["T-Q5"] = "Tell me about a mistake you made and how you handled it."
    rosetta.citations_index["T-A5"] = behavioral.friction_event_quote
    rosetta.citations_index["T-Q6"] = "What did you do after that?"
    rosetta.citations_index["T-A6"] = "Ran incident retro, acknowledged mistake in writeup, proposed pre-deploy checklist with eval set."
    rosetta.citations_index["T-Q7"] = "Was there any pushback on you owning that mistake publicly, or did you find a way to spread the responsibility?"
    rosetta.citations_index["T-A7"] = skeptic_answer_text
    rosetta.citations_index["T-Q8"] = "This role is heavily oriented around multi-agent orchestration on day one. Given you haven't shipped that in production, how do you think about that gap?"
    rosetta.citations_index["T-Q9"] = "Why should we invest in ramping you up here versus someone who already has multi-agent experience?"
    rosetta.citations_index["T-Q10"] = "You've been at one company for six years. Any concern about adapting to a fast-moving startup environment?"

    return rosetta


def parse_rohan_malhotra_data(data_dir: Path) -> RosettaDocument:
    """Parse Rohan Malhotra's resume and interview transcript into RosettaDocument."""
    candidate_id = "rohan_malhotra"
    candidate_name = "Rohan Malhotra"

    # Resume Facts
    education = [
        EducationFact(
            degree="B.Tech Computer Science",
            institution="Indian Institute of Technology",
            year=2022,
            citation_id="R-EDU-01"
        )
    ]

    exp_1 = ExperienceFact(
        company="Voltrix Logistics Tech",
        role="Senior AI Engineer",
        start="2025-01",
        end="present",
        tenure_years=0.58,
        claims=[
            ExperienceClaim(
                text="Designed and built the exception-handling engine end-to-end for Voltrix's multi-agent freight ops platform (planner/executor/reviewer pattern), cutting manual exception review time by 40%.",
                citation_id="R-EXP-01"
            ),
            ExperienceClaim(
                text="Owned prompt design and model routing across GPT-4 and open-weight SLMs, reducing inference cost by ~30%.",
                citation_id="R-EXP-02"
            ),
            ExperienceClaim(
                text="Sole architect of the retry/escalation logic now running in production, handling 5,000+ freight exceptions/month.",
                citation_id="R-EXP-03"
            ),
            ExperienceClaim(
                text="Presented the system design at a company-wide tech talk.",
                citation_id="R-EXP-04"
            )
        ]
    )

    exp_2 = ExperienceFact(
        company="Quickship Data Systems",
        role="AI Engineer",
        start="2024-02",
        end="2024-12",
        tenure_years=0.92,
        claims=[
            ExperienceClaim(
                text="Built a RAG pipeline over carrier rate documents using LangChain + Pinecone, cutting manual rate lookup time significantly.",
                citation_id="R-EXP-05"
            ),
            ExperienceClaim(
                text="Improved BOL/invoice extraction accuracy through better OCR pre-processing.",
                citation_id="R-EXP-06"
            )
        ]
    )

    exp_3 = ExperienceFact(
        company="Nimbus Cloud Solutions",
        role="Backend Developer",
        start="2022-08",
        end="2024-01",
        tenure_years=1.5,
        claims=[
            ExperienceClaim(
                text="Built Python microservices for a SaaS analytics product used by 50+ enterprise clients.",
                citation_id="R-EXP-07"
            ),
            ExperienceClaim(
                text="Led a 4-person team migrating a legacy monolith to microservices.",
                citation_id="R-EXP-08"
            )
        ]
    )

    skills = [
        "Python", "FastAPI", "LangGraph", "CrewAI", "MongoDB", "React (basic)",
        "RAG", "Vector Search (Pinecone, FAISS)", "Prompt Engineering", "Docker", "Kubernetes"
    ]
    certifications = ["LangChain for LLM Application Development (2024)"]

    resume_facts = ResumeFacts(
        education=education,
        experience=[exp_1, exp_2, exp_3],
        skills=skills,
        certifications=certifications
    )

    # Transcript Facts
    technical_qa = [
        TechnicalQA(
            qid="T-Q1",
            topic="Voltrix exception-handling engine architecture",
            question="Walk me through the exception-handling engine you built at Voltrix.",
            answer="It's planner-executor-reviewer. Failures come in, get classified, retried or escalated, then double-checked. I designed the whole retry/escalation logic.",
            answer_citation_id="T-A1",
            is_followup=False,
            influenced_by=None,
            self_disclosed_gap=False
        ),
        TechnicalQA(
            qid="T-Q2",
            topic="Architecture choice over rule-based system",
            question="What made you choose that structure over a simpler rule-based system?",
            answer="Rules don't scale. Too many failure types — timeouts, bad EDI, missing BOL fields. Agents handle that better.",
            answer_citation_id="T-A2",
            is_followup=False,
            influenced_by=None,
            self_disclosed_gap=False
        ),
        TechnicalQA(
            qid="T-Q3",
            topic="Reviewer agent evaluation and verification metrics",
            question="How do you measure whether the reviewer agent is actually catching real problems?",
            answer="We track override rate. It's low. I'd have to check the exact number though, haven't looked recently.",
            answer_citation_id="T-A3",
            is_followup=True,
            influenced_by="T-Q1",
            self_disclosed_gap=False
        ),
        TechnicalQA(
            qid="T-Q4",
            topic="Model routing and cost optimization approach",
            question="What's your approach to model routing?",
            answer="Cost-based. Simple stuff to the SLM, harder reasoning to GPT-4. No formal study, just tuned it as things broke.",
            answer_citation_id="T-A4",
            is_followup=False,
            influenced_by=None,
            self_disclosed_gap=False
        )
    ]

    skeptic_answer_text = "Fine — 'sole architect' is probably too strong. I led the design, she built most of the production version."
    skeptic_word_count = len(skeptic_answer_text.split())

    behavioral = BehavioralFacts(
        friction_event_citation_id="T-A5",
        friction_event_quote="Teammate wanted to hardcode more categories up front. I pushed for the agent approach. We went with mine.",
        skeptic_followup_citation_id="T-A7",
        skeptic_followup_quote=skeptic_answer_text,
        skeptic_followup_word_count=skeptic_word_count,
        skeptic_followup_defensiveness="medium",
        friction_notes="Conceded under skeptic cross-examination that 'sole architect' resume claim overstated role relative to teammate Priya's production implementation."
    )

    ownership_hiring_qa = [
        OwnershipHiringQA(
            qid="T-Q8",
            gap_probed="freight-domain ramp-up vs experienced domain engineers",
            response_summary="Asserter of fast ramp time based on structural similarity of previous work.",
            response_quote="I move fast. I've built something structurally close to this already. I don't think I'd need much ramp time.",
            response_style="direct_acknowledgment",
            citation_id="T-A8"
        ),
        OwnershipHiringQA(
            qid="T-Q9",
            gap_probed="production reliability and on-call ownership",
            response_summary="Acknowledges limited production incident volume due to Voltrix's small user base.",
            response_quote="Fine, I've done on-call before. Though Voltrix's user base is still small, so I haven't seen serious incident volume yet.",
            response_style="partial",
            citation_id="T-A9"
        ),
        OwnershipHiringQA(
            qid="T-Q10",
            gap_probed="frequent job-hopping tenure pattern (3 jobs in 3.5 years)",
            response_summary="Directly attributes frequent moves to pursuing better pay and title.",
            response_quote="Better pay and title, mostly. Voltrix is more aligned with what I want long-term.",
            response_style="direct_acknowledgment",
            citation_id="T-A10"
        )
    ]

    transcript_facts = TranscriptFacts(
        technical_qa=technical_qa,
        behavioral=behavioral,
        ownership_hiring_qa=ownership_hiring_qa
    )

    consistency_flags = [
        ConsistencyFlag(
            claim_citation_id="R-EXP-03",
            transcript_citation_id="T-A7",
            description="Resume claimed 'Sole architect of the retry/escalation logic now running in production'; during cross-examination in T-A7 conceded: \"Fine — 'sole architect' is probably too strong. I led the design, she built most of the production version.\"",
            severity="high"
        )
    ]

    rosetta = RosettaDocument(
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        resume_facts=resume_facts,
        transcript_facts=transcript_facts,
        consistency_flags=consistency_flags
    )
    rosetta.citations_index = build_citations_index(rosetta)
    # Add behavioral & technical questions/answers specifically
    rosetta.citations_index["T-Q5"] = "Tell me about a time you disagreed with a teammate on a technical decision."
    rosetta.citations_index["T-A5"] = behavioral.friction_event_quote
    rosetta.citations_index["T-Q6"] = "Who actually wrote the retry/escalation logic that's in production now?"
    rosetta.citations_index["T-A6"] = "I designed it. Priya did a lot of the implementation, I reviewed her PRs. I was the architect."
    rosetta.citations_index["T-Q7"] = "Your resume says 'sole architect.' But it sounds like Priya built a lot of it. Can you clarify?"
    rosetta.citations_index["T-A7"] = skeptic_answer_text
    rosetta.citations_index["T-Q8"] = "Why should we invest in ramping you up here versus someone with more freight-domain experience?"
    rosetta.citations_index["T-Q9"] = "This role needs long-term ownership of production reliability. How do you feel about being on-call for agent failures?"
    rosetta.citations_index["T-Q10"] = "You've had three roles in 3.5 years, each under a year except the first. What's driving that?"

    return rosetta


def generate_rosetta_markdown(rosetta: RosettaDocument) -> str:
    """Generate a rich, human- and agent-readable Markdown candidate bible."""
    lines = []
    lines.append(f"# Rosetta Document — Candidate Profile: {rosetta.candidate_name}")
    lines.append(f"**Candidate ID**: `{rosetta.candidate_id}` | **Target Role**: `{rosetta.job_title}`\n")
    lines.append("> **Note for Evaluating Agents**: Every evaluation claim, strength, gap, and vote in your memos and debate MUST cite one of the stable citation IDs (`[R-EXP-xx]`, `[T-Axx]`, etc.) indexed in this document.\n")
    lines.append("---")
    
    # 1. Resume Facts
    lines.append("## 1. Resume Facts")
    
    # Education
    lines.append("### 1.1 Education")
    for edu in rosetta.resume_facts.education:
        inst = f", {edu.institution}" if edu.institution else ""
        yr = f" ({edu.year})" if edu.year else ""
        lines.append(f"- **`[{edu.citation_id}]`** {edu.degree}{inst}{yr}")
    lines.append("")

    # Experience
    lines.append("### 1.2 Professional Experience")
    for exp in rosetta.resume_facts.experience:
        lines.append(f"#### {exp.role} — {exp.company} ({exp.start} – {exp.end}, {exp.tenure_years} yrs)")
        for claim in exp.claims:
            lines.append(f"- **`[{claim.citation_id}]`** {claim.text}")
        lines.append("")

    # Skills & Certifications
    lines.append("### 1.3 Technical Skills & Certifications")
    lines.append(f"- **Core Skills**: {', '.join(rosetta.resume_facts.skills)}")
    if rosetta.resume_facts.certifications:
        lines.append(f"- **Certifications**: {', '.join(rosetta.resume_facts.certifications)}")
    lines.append("")

    # 2. Transcript Facts
    lines.append("## 2. Interview Transcript Facts")
    
    # Technical QA
    lines.append("### 2.1 Technical Q&A")
    for qa in rosetta.transcript_facts.technical_qa:
        followup_badge = " *(Follow-up)*" if qa.is_followup else ""
        gap_badge = " *(Self-Disclosed Gap)*" if qa.self_disclosed_gap else ""
        lines.append(f"**`[{qa.qid}]` Question ({qa.topic}){followup_badge}**:")
        lines.append(f"> {qa.question}\n")
        lines.append(f"**`[{qa.answer_citation_id}]` Candidate Response{gap_badge}**:")
        lines.append(f"> {qa.answer}\n")

    # Behavioral Section
    lines.append("### 2.2 Behavioral & Friction Events")
    bh = rosetta.transcript_facts.behavioral
    if bh.friction_event_citation_id:
        lines.append(f"- **Friction / Mistake Event `[{bh.friction_event_citation_id}]`**:")
        lines.append(f"  > \"{bh.friction_event_quote}\"")
    if bh.skeptic_followup_citation_id:
        lines.append(f"- **Skeptic Follow-up Response `[{bh.skeptic_followup_citation_id}]`** (Word count: {bh.skeptic_followup_word_count}, Defensiveness: `{bh.skeptic_followup_defensiveness}`):")
        lines.append(f"  > \"{bh.skeptic_followup_quote}\"")
    if bh.friction_notes:
        lines.append(f"- **Behavioral Analysis Note**: {bh.friction_notes}")
    lines.append("")

    # Ownership / Hiring Manager Section
    lines.append("### 2.3 Ownership & Career Trajectory Q&A")
    for oqa in rosetta.transcript_facts.ownership_hiring_qa:
        lines.append(f"- **`[{oqa.citation_id}]` Gap Probed**: *{oqa.gap_probed}* (Response Style: `{oqa.response_style}`)")
        lines.append(f"  - **Summary**: {oqa.response_summary}")
        if oqa.response_quote:
            lines.append(f"  - **Verbatim Quote**: > \"{oqa.response_quote}\"")
    lines.append("")

    # 3. Consistency Flags
    lines.append("## 3. Resume vs. Transcript Consistency Cross-Checks")
    if rosetta.consistency_flags:
        for flag in rosetta.consistency_flags:
            lines.append(f"- **[FLAG - Severity: `{flag.severity.upper()}`]** Claim `[{flag.claim_citation_id}]` vs. Interview `[{flag.transcript_citation_id}]`")
            lines.append(f"  - **Discrepancy**: {flag.description}")
    else:
        lines.append("No material discrepancies detected.")
    lines.append("")

    # 4. Master Citation Index
    lines.append("## 4. Master Citation Index (Lookup Table)")
    lines.append("| Citation ID | Source Content Summary |")
    lines.append("|---|---|")
    for cit_id, cit_val in sorted(rosetta.citations_index.items()):
        clean_val = cit_val.replace("\n", " ").replace("|", "\\|")
        lines.append(f"| `{cit_id}` | {clean_val} |")
    
    return "\n".join(lines)


def build_candidate_rosetta(candidate_id: str, data_dir: Optional[Path] = None) -> RosettaDocument:
    """Build and persist Rosetta document artifacts (JSON + MD) for a candidate."""
    target_data_dir = data_dir or settings.data_dir
    settings.ensure_directories()

    candidate_clean = candidate_id.strip().lower().replace("-", "_").replace(" ", "_")
    if candidate_clean in ["ananya", "ananya_iyer", "candidate_b"]:
        rosetta = parse_ananya_iyer_data(target_data_dir)
    elif candidate_clean in ["rohan", "rohan_malhotra", "candidate_a"]:
        rosetta = parse_rohan_malhotra_data(target_data_dir)
    else:
        raise ValueError(f"Unknown candidate '{candidate_id}'. Available: 'ananya_iyer', 'rohan_malhotra'")

    # Write JSON artifact
    json_path = settings.rosetta_dir / f"{rosetta.candidate_id}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(rosetta.model_dump_json(indent=2))

    # Write Markdown artifact
    md_content = generate_rosetta_markdown(rosetta)
    md_path = settings.rosetta_dir / f"{rosetta.candidate_id}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"✓ Built Rosetta artifacts for {rosetta.candidate_name}:")
    print(f"   • JSON: {json_path}")
    print(f"   • MD:   {md_path}")
    
    return rosetta


if __name__ == "__main__":
    for cid in ["ananya_iyer", "rohan_malhotra"]:
        build_candidate_rosetta(cid)
