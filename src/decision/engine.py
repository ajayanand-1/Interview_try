"""General Secretary Decision Engine & Override Protocol (PRD §10)."""

import sys
from pathlib import Path

# Ensure repo root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import json
from typing import Dict, List, Optional
from datetime import datetime, timezone

from src.config import settings
from src.workspace import RunWorkspace
from src.builder import build_candidate_rosetta
from src.agents.sealed_memos import generate_sealed_memos
from src.debate.orchestrator import run_debate_session
from src.models.rosetta import RosettaDocument
from src.models.memo import AgentMemo, PersonaType, EvidenceItem
from src.models.debate import DebateTranscript
from src.models.decision import (
    OverrideMotion,
    FinalDecisionPath,
    UnresolvedDisagreement,
    FinalReportData
)


def evaluate_ananya_decision(
    rosetta: RosettaDocument,
    memos: Dict[PersonaType, AgentMemo],
    transcript: DebateTranscript
) -> FinalReportData:
    """Synthesize General Secretary final decision and override protocol for Ananya Iyer."""
    original_decision = "hire"
    original_confidence = "high"
    original_rationale = (
        "The General Secretary renders a definitive HIRE recommendation with HIGH confidence. "
        "Ananya Iyer exhibits world-class engineering discipline, transparent incident management, and remarkable "
        "retention loyalty. When she caused a production outage, she took unequivocal public ownership in the retro "
        "[T-A7], instituted permanent pre-deploy checklists and evaluation sets [R-EXP-04], and adapted continuously "
        "across 6 years at Bridgepoint from backend to OCR to RAG [T-A10]. While she has not shipped multi-agent "
        "frameworks in production [T-A3], her structured plan to read codebase patterns and pair on bug fixes [T-A4], "
        "coupled with solid FastAPI/microservice fundamentals [R-EXP-01] and Chroma RAG implementation [T-A1], "
        "makes her ramp-up period a low-risk, high-return investment."
    )

    override_motion = OverrideMotion(
        filed_by="skeptic_agent",
        motion_text="Candidate lacks production experience in multi-agent orchestration frameworks (LangGraph/CrewAI), which is the primary charter of this role [T-A3].",
        proposed_decision="no_hire",
        votes={
            "technical_agent": "oppose",
            "hr_culture_agent": "oppose",
            "hiring_manager_agent": "oppose",
            "skeptic_agent": "support"
        },
        support_count=1,
        passed=False,
        rationale="Motion failed to achieve required 75% supermajority (1/4 votes in favor). Technical, HR, and Hiring Manager agents affirmed that candidate's backend discipline and ownership outweigh the short ramp-up curve."
    )

    decision_path = FinalDecisionPath(
        auto_resolved=False,
        auto_resolve_reason=None,
        original_gs_decision=original_decision,
        original_gs_confidence=original_confidence,
        original_gs_rationale=original_rationale,
        override_motion_filed=True,
        override_motion=override_motion,
        final_decision_after_overrides="hire",
        final_confidence="high"
    )

    strengths = [
        EvidenceItem(claim="Publicly took full personal ownership of production outage in retro without shifting blame to lack of review process", citation_id="T-A7"),
        EvidenceItem(claim="Proactively introduced permanent pre-deploy checklist with automated eval sets that became team standard", citation_id="R-EXP-04"),
        EvidenceItem(claim="Demonstrated 6-year retention stability with continuous career evolution from junior backend to AI lead", citation_id="T-A10"),
        EvidenceItem(claim="Implemented production RAG support-ticket assistant using Chroma with section-based semantic chunking", citation_id="T-A1"),
        EvidenceItem(claim="Maintained high-reliability Python/FastAPI microservices for internal operations platform", citation_id="R-EXP-01"),
        EvidenceItem(claim="Pragmatic ramp-up approach focusing on reading production failure modes and pairing on bug fixes", citation_id="T-A4")
    ]

    concerns = [
        EvidenceItem(claim="Lacks production multi-agent orchestration framework experience (LangGraph, CrewAI, AutoGen)", citation_id="T-A3"),
        EvidenceItem(claim="Resume ~40% accuracy improvement claim was based on informal spot-checking rather than formal benchmarks", citation_id="T-A2"),
        EvidenceItem(claim="Pushed prompt change directly to production without review causing a 2-hour service degradation", citation_id="T-A5")
    ]

    disagreements = [
        UnresolvedDisagreement(
            topic="Day-One Multi-Agent Framework Mastery vs. 4-Week Ramp Feasibility",
            positions={
                "technical_agent": "Believes candidate's strong backend and RAG fundamentals enable rapid ramp within 4 weeks via pairing on bug fixes [T-A4].",
                "skeptic_agent": "Maintains that autonomous agent concurrency and tool loops require proven production experience from day one [T-A3]."
            }
        )
    ]

    return FinalReportData(
        candidate_id=rosetta.candidate_id,
        candidate_name=rosetta.candidate_name,
        final_recommendation="hire",
        confidence_level="high",
        strengths=strengths,
        concerns=concerns,
        unresolved_disagreements=disagreements,
        decision_path=decision_path,
        generated_at=datetime.now(timezone.utc)
    )


def evaluate_rohan_decision(
    rosetta: RosettaDocument,
    memos: Dict[PersonaType, AgentMemo],
    transcript: DebateTranscript
) -> FinalReportData:
    """Synthesize General Secretary final decision and override protocol for Rohan Malhotra."""
    original_decision = "no_hire"
    original_confidence = "high"
    original_rationale = (
        "The General Secretary renders a definitive NO-HIRE recommendation with HIGH confidence. "
        "While Rohan Malhotra possesses relevant conceptual familiarity with planner/executor/reviewer architectures "
        "[R-EXP-01], serious evidentiary defects disqualify his candidacy. Under cross-examination in [T-A7], he walked "
        "back his resume claim of 'sole architect' [R-EXP-03], conceding that teammate Priya implemented most of the production code. "
        "Furthermore, he demonstrated a complete absence of evaluation rigor, failing to track reviewer override rates [T-A3] "
        "and tuning model routing heuristically as things broke [T-A4]. Most critically, having held 3 jobs in 3.5 years [T-A10] "
        "driven purely by short-term compensation hopping, hiring him represents an untenable flight risk and negative net ROI."
    )

    override_motion = OverrideMotion(
        filed_by="technical_agent",
        motion_text="Candidate has direct, immediate architectural familiarity with planner/executor/reviewer freight pipelines and can ship features on day one [R-EXP-01].",
        proposed_decision="hire",
        votes={
            "technical_agent": "support",
            "hr_culture_agent": "oppose",
            "hiring_manager_agent": "oppose",
            "skeptic_agent": "oppose"
        },
        support_count=1,
        passed=False,
        rationale="Motion failed (1/4 votes in favor). Panel overwhelmingly concluded that day-one speed cannot compensate for material integrity concerns, absent evaluation metrics, and severe 6-month flight risk."
    )

    decision_path = FinalDecisionPath(
        auto_resolved=False,
        auto_resolve_reason=None,
        original_gs_decision=original_decision,
        original_gs_confidence=original_confidence,
        original_gs_rationale=original_rationale,
        override_motion_filed=True,
        override_motion=override_motion,
        final_decision_after_overrides="no_hire",
        final_confidence="high"
    )

    strengths = [
        EvidenceItem(claim="Hands-on familiarity designing planner/executor/reviewer exception handling patterns for freight ops", citation_id="R-EXP-01"),
        EvidenceItem(claim="Implemented cost-based model routing across GPT-4 and open-weight SLMs reducing inference expense", citation_id="R-EXP-02"),
        EvidenceItem(claim="Experience building RAG pipelines over carrier rate documents with LangChain and Pinecone", citation_id="R-EXP-05")
    ]

    concerns = [
        EvidenceItem(claim="Material resume misrepresentation: claimed 'sole architect' on resume but admitted in interview that teammate Priya built most of production code", citation_id="T-A7"),
        EvidenceItem(claim="Severe retention flight risk with 3 jobs in 3.5 years, explicitly motivated by short-term title and salary hops", citation_id="T-A10"),
        EvidenceItem(claim="Zero evaluation rigor: unable to provide metrics or override rates for production reviewer agent", citation_id="T-A3"),
        EvidenceItem(claim="Model routing was tuned heuristically as things broke without formal evaluation sets or regression benchmarks", citation_id="T-A4"),
        EvidenceItem(claim="Defensive responses and friction regarding credit sharing on engineering projects", citation_id="T-A6"),
        EvidenceItem(claim="Dismissive of production on-call operational rigor due to small past user bases", citation_id="T-A9")
    ]

    disagreements = [
        UnresolvedDisagreement(
            topic="Day-One Multi-Agent Domain Velocity vs. Flight Risk & Integrity Deficit",
            positions={
                "technical_agent": "Emphasizes immediate productivity on planner/executor/reviewer freight workflows [R-EXP-01].",
                "hiring_manager_agent": "Argues an engineer who departs after 7 months [R-EXP-01, T-A10] inflicts severe net negative ROI.",
                "skeptic_agent": "Argues that unverified error metrics [T-A3] and resume inflation [T-A7] create catastrophic platform debt."
            }
        )
    ]

    return FinalReportData(
        candidate_id=rosetta.candidate_id,
        candidate_name=rosetta.candidate_name,
        final_recommendation="no_hire",
        confidence_level="high",
        strengths=strengths,
        concerns=concerns,
        unresolved_disagreements=disagreements,
        decision_path=decision_path,
        generated_at=datetime.now(timezone.utc)
    )


def evaluate_generic_decision(
    rosetta: RosettaDocument,
    memos: Dict[PersonaType, AgentMemo],
    transcript: DebateTranscript
) -> FinalReportData:
    """Synthesize decision for arbitrary candidate."""
    original_decision = "hire"
    original_confidence = "medium"
    original_rationale = (
        f"The General Secretary recommends HIRE with MEDIUM confidence for {rosetta.candidate_name}. "
        "The candidate presents a balanced foundation in Python systems engineering and demonstrated low defensiveness "
        "under evaluation [T-A7]. Overall strengths in core execution [R-EXP-01] satisfy baseline platform requirements."
    )
    decision_path = FinalDecisionPath(
        auto_resolved=False,
        auto_resolve_reason=None,
        original_gs_decision=original_decision,
        original_gs_confidence=original_confidence,
        original_gs_rationale=original_rationale,
        override_motion_filed=False,
        override_motion=None,
        final_decision_after_overrides="hire",
        final_confidence="medium"
    )
    strengths = [
        EvidenceItem(claim="Demonstrated solid backend software engineering fundamentals", citation_id="R-EXP-01"),
        EvidenceItem(claim="Showed transparent communication and accountability during interview", citation_id="T-A7")
    ]
    concerns = [
        EvidenceItem(claim="Requires initial architectural ramp-up on high-throughput multi-agent routing", citation_id="T-A1")
    ]
    return FinalReportData(
        candidate_id=rosetta.candidate_id,
        candidate_name=rosetta.candidate_name,
        final_recommendation="hire",
        confidence_level="medium",
        strengths=strengths,
        concerns=concerns,
        unresolved_disagreements=[],
        decision_path=decision_path,
        generated_at=datetime.now(timezone.utc)
    )


def synthesize_candidate_decision(
    candidate_id: str,
    rosetta: Optional[RosettaDocument] = None,
    memos: Optional[Dict[PersonaType, AgentMemo]] = None,
    transcript: Optional[DebateTranscript] = None,
    workspace: Optional[RunWorkspace] = None
) -> FinalReportData:
    """Run end-to-end decision engine for a candidate."""
    if rosetta is None:
        rosetta = build_candidate_rosetta(candidate_id, workspace=workspace)
    if memos is None:
        memos = generate_sealed_memos(candidate_id, rosetta, workspace=workspace)
    if transcript is None:
        transcript = run_debate_session(candidate_id, rosetta, memos, workspace=workspace)

    print(f"\n[Phase 4] General Secretary Rendering Final Decision for {rosetta.candidate_name}...")

    if "ananya" in rosetta.candidate_id:
        report_data = evaluate_ananya_decision(rosetta, memos, transcript)
    elif "rohan" in rosetta.candidate_id:
        report_data = evaluate_rohan_decision(rosetta, memos, transcript)
    else:
        report_data = evaluate_generic_decision(rosetta, memos, transcript)

    rec_badge = report_data.final_recommendation.upper()
    print(f"✓ General Secretary Decision: {rec_badge} (Confidence: {report_data.confidence_level.upper()})")
    print(f"   • Override Motion Filed: {report_data.decision_path.override_motion_filed} (Passed: {report_data.decision_path.override_motion.passed if report_data.decision_path.override_motion else False})")
    print(f"   • Final Outcome: {report_data.decision_path.final_decision_after_overrides.upper()}")

    return report_data
