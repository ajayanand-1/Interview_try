"""Unit tests for Phase 0 schema validation and constraint enforcement."""

import pytest
from pydantic import ValidationError

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
from src.models.memo import AgentMemo, EvidenceItem
from src.models.debate import DebateTurn, DebateRound, DebateTranscript
from src.models.decision import OverrideMotion, FinalDecisionPath, FinalReportData, UnresolvedDisagreement
from src.utils.citations import build_citations_index, validate_memo_traceability


def test_rosetta_schema_valid():
    """Test valid construction of a Rosetta document."""
    rosetta = RosettaDocument(
        candidate_id="ananya_iyer",
        candidate_name="Ananya Iyer",
        resume_facts=ResumeFacts(
            education=[EducationFact(degree="B.E. Information Technology", year=2019, citation_id="R-EDU-01")],
            experience=[
                ExperienceFact(
                    company="Bridgepoint Systems",
                    role="Software Engineer II",
                    start="2021-06",
                    end="present",
                    tenure_years=4.2,
                    claims=[
                        ExperienceClaim(text="Built RAG support-ticket assistant", citation_id="R-EXP-01")
                    ]
                )
            ],
            skills=["Python", "FastAPI", "MongoDB"],
            certifications=[]
        ),
        transcript_facts=TranscriptFacts(
            technical_qa=[
                TechnicalQA(
                    qid="T-Q1",
                    topic="RAG architecture",
                    question="How did you implement vector search?",
                    answer="Used ChromaDB with chunking and embeddings.",
                    answer_citation_id="T-A1",
                    is_followup=False,
                    self_disclosed_gap=False
                )
            ],
            behavioral=BehavioralFacts(
                friction_event_citation_id="T-A5",
                friction_event_quote="I disagreed on caching strategy.",
                skeptic_followup_defensiveness="low"
            ),
            ownership_hiring_qa=[
                OwnershipHiringQA(
                    qid="T-Q8",
                    gap_probed="multi-agent experience",
                    response_summary="Directly acknowledged having single-agent RAG only.",
                    response_style="direct_acknowledgment",
                    citation_id="T-A8"
                )
            ]
        ),
        consistency_flags=[]
    )
    
    assert rosetta.candidate_id == "ananya_iyer"
    index = build_citations_index(rosetta)
    assert "R-EDU-01" in index
    assert "R-EXP-01" in index
    assert "T-A1" in index
    assert "T-A8" in index


def test_memo_valid_score():
    """Test valid memo score creation."""
    memo = AgentMemo(
        persona="technical_agent",
        candidate_id="ananya_iyer",
        score=7,
        confidence="high",
        verdict_summary="Solid Python foundation and RAG experience.",
        strengths=[EvidenceItem(claim="Built RAG ticket assistant", citation_id="R-EXP-01")],
        gaps=[EvidenceItem(claim="Lacks multi-agent production experience", citation_id="T-A8")],
    )
    assert memo.score == 7
    assert memo.confidence == "high"


def test_memo_insufficient_evidence_requires_none_score():
    """Test PRD §12: score must be None when confidence is insufficient_evidence."""
    # Valid: score=None with insufficient_evidence
    memo = AgentMemo(
        persona="technical_agent",
        candidate_id="ananya_iyer",
        score=None,
        confidence="insufficient_evidence",
        verdict_summary="Not enough data to score carrier integrations.",
        insufficient_evidence_items=["carrier integrations"]
    )
    assert memo.score is None

    # Invalid: non-null score with insufficient_evidence
    with pytest.raises(ValidationError):
        AgentMemo(
            persona="technical_agent",
            candidate_id="ananya_iyer",
            score=5,
            confidence="insufficient_evidence",
            verdict_summary="Invalid attempt to provide score with insufficient evidence"
        )


def test_memo_score_range_validation():
    """Test that score must be between 1 and 10."""
    with pytest.raises(ValidationError):
        AgentMemo(
            persona="technical_agent",
            candidate_id="ananya_iyer",
            score=11,  # out of range
            confidence="high",
            verdict_summary="Invalid score"
        )

    with pytest.raises(ValidationError):
        AgentMemo(
            persona="technical_agent",
            candidate_id="ananya_iyer",
            score=0,  # out of range
            confidence="high",
            verdict_summary="Invalid score"
        )


def test_traceability_validation():
    """Test traceability verification helper."""
    memo = AgentMemo(
        persona="technical_agent",
        candidate_id="ananya_iyer",
        score=7,
        confidence="high",
        verdict_summary="Valid citations",
        strengths=[EvidenceItem(claim="Good RAG", citation_id="R-EXP-01")],
        gaps=[EvidenceItem(claim="Missing agent experience", citation_id="UNKNOWN-CIT-99")],
    )
    
    valid_citations = {"R-EXP-01", "T-A1", "T-A8"}
    passed, invalid = validate_memo_traceability(memo, valid_citations)
    assert not passed
    assert invalid == ["UNKNOWN-CIT-99"]


def test_override_motion_supermajority():
    """Test override motion logic."""
    motion = OverrideMotion(
        filed_by="skeptic_agent",
        motion_text="Candidate lacks required multi-agent experience for an Agentic Systems role.",
        proposed_decision="no_hire",
        votes={
            "technical_agent": "support",
            "hr_culture_agent": "support",
            "hiring_manager_agent": "oppose",
            "skeptic_agent": "support"
        },
        support_count=3,
        passed=True,
        rationale="3 out of 4 agents voted to overturn the hire recommendation to no-hire."
    )
    assert motion.passed is True
    assert motion.support_count == 3
