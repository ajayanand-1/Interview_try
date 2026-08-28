"""Pydantic schema for Agent Memos and Evidence (PRD §7 & §12)."""

from typing import List, Optional, Literal
from datetime import datetime, timezone
from pydantic import BaseModel, Field, model_validator


PersonaType = Literal["technical_agent", "hr_culture_agent", "hiring_manager_agent", "skeptic_agent"]
ConfidenceLevel = Literal["low", "medium", "high", "insufficient_evidence"]


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EvidenceItem(BaseModel):
    claim: str = Field(..., description="Fact or assertion made by the persona")
    citation_id: str = Field(..., description="Stable citation ID from Rosetta document")


class AgentMemo(BaseModel):
    persona: PersonaType
    candidate_id: str
    score: Optional[int] = Field(
        None,
        description="Integer score 1-10. Must be None if confidence is 'insufficient_evidence' (PRD §12)"
    )
    confidence: ConfidenceLevel
    verdict_summary: str
    strengths: List[EvidenceItem] = Field(default_factory=list)
    gaps: List[EvidenceItem] = Field(default_factory=list)
    insufficient_evidence_items: List[str] = Field(default_factory=list)
    contrarian_argument: Optional[str] = Field(
        None,
        description="Contrarian perspective / devil's advocate point (required for HR/Culture, optional for others)"
    )
    created_at: datetime = Field(default_factory=get_utc_now)

    @model_validator(mode="after")
    def validate_score_against_confidence(self):
        """Enforce PRD §12: When confidence is 'insufficient_evidence', score must be None."""
        if self.confidence == "insufficient_evidence":
            if self.score is not None:
                raise ValueError("Score must be null/None when confidence is 'insufficient_evidence' (PRD §12)")
        else:
            if self.score is None:
                raise ValueError("Score must be provided (1-10) when confidence is not 'insufficient_evidence'")
            if not (1 <= self.score <= 10):
                raise ValueError(f"Score must be between 1 and 10, got {self.score}")
        return self
