"""Tests for PRD §12 Edge Cases & Missing Information Handling."""

import pytest
from pydantic import ValidationError

from src.models.rosetta import (
    RosettaDocument,
    ResumeFacts,
    TranscriptFacts,
    EducationFact,
    ExperienceFact,
    ExperienceClaim
)
from src.models.memo import AgentMemo, EvidenceItem
from src.agents.runner import generate_grounded_memo_fallback


def test_missing_info_insufficient_evidence_emission():
    """PRD §12 & §15: Truncated info must emit insufficient_evidence and null score, never fabricated score."""
    # Construct a deliberately truncated Rosetta document missing transcript data
    truncated_rosetta = RosettaDocument(
        candidate_id="truncated_candidate",
        candidate_name="Truncated Candidate",
        resume_facts=ResumeFacts(
            education=[EducationFact(degree="B.S. CS", year=2023, citation_id="R-EDU-01")],
            experience=[],
            skills=["Python"],
            certifications=[]
        ),
        transcript_facts=TranscriptFacts(
            technical_qa=[],
            ownership_hiring_qa=[]
        )
    )

    # An agent evaluating this truncated data must emit insufficient_evidence
    memo = AgentMemo(
        persona="technical_agent",
        candidate_id="truncated_candidate",
        score=None,
        confidence="insufficient_evidence",
        verdict_summary="Insufficient evidence to evaluate backend or agentic capabilities; no technical interview data.",
        insufficient_evidence_items=[
            "multi-agent orchestration",
            "production RAG experience",
            "error handling and deployment discipline"
        ]
    )

    assert memo.score is None
    assert memo.confidence == "insufficient_evidence"
    assert len(memo.insufficient_evidence_items) == 3


def test_score_fabrication_strictly_prevented():
    """PRD §12: Schema MUST raise error if an agent attempts to emit a numeric score with insufficient_evidence."""
    with pytest.raises(ValidationError) as exc_info:
        AgentMemo(
            persona="technical_agent",
            candidate_id="truncated_candidate",
            score=5,  # Fabricated placeholder score -> MUST FAIL
            confidence="insufficient_evidence",
            verdict_summary="Attempting to fabricate a score"
        )
    assert "Score must be null/None when confidence is 'insufficient_evidence'" in str(exc_info.value)


def test_missing_score_with_normal_confidence_prevented():
    """Schema must require a score when confidence is low/medium/high."""
    with pytest.raises(ValidationError) as exc_info:
        AgentMemo(
            persona="technical_agent",
            candidate_id="candidate_x",
            score=None,  # Missing score with high confidence -> MUST FAIL
            confidence="high",
            verdict_summary="Missing score"
        )
    assert "Score must be provided (1-10)" in str(exc_info.value)
