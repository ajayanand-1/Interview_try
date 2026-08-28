"""Pydantic schema for Decision, Overrides, and Final Report (PRD §10 & §11)."""

from typing import List, Optional, Dict, Literal
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from src.models.memo import EvidenceItem


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class OverrideMotion(BaseModel):
    filed_by: str
    motion_text: str
    proposed_decision: Literal["hire", "no_hire"]
    votes: Dict[str, Literal["support", "oppose"]] = Field(
        default_factory=dict,
        description="Votes from all 4 independent agents"
    )
    support_count: int = 0
    passed: bool = Field(..., description="True if >= 3 of 4 agents support (75% supermajority)")
    rationale: str


class FinalDecisionPath(BaseModel):
    auto_resolved: bool = False
    auto_resolve_reason: Optional[str] = None
    original_gs_decision: Literal["hire", "no_hire"]
    original_gs_confidence: Literal["low", "medium", "high"]
    original_gs_rationale: str
    override_motion_filed: bool = False
    override_motion: Optional[OverrideMotion] = None
    final_decision_after_overrides: Literal["hire", "no_hire"]
    final_confidence: Literal["low", "medium", "high"]


class UnresolvedDisagreement(BaseModel):
    topic: str
    positions: Dict[str, str] = Field(
        default_factory=dict,
        description="Map of persona -> final stance on this disagreement"
    )


class FinalReportData(BaseModel):
    candidate_id: str
    candidate_name: str
    final_recommendation: Literal["hire", "no_hire"]
    confidence_level: Literal["low", "medium", "high"]
    strengths: List[EvidenceItem] = Field(default_factory=list)
    concerns: List[EvidenceItem] = Field(default_factory=list)
    unresolved_disagreements: List[UnresolvedDisagreement] = Field(default_factory=list)
    decision_path: FinalDecisionPath
    generated_at: datetime = Field(default_factory=get_utc_now)
