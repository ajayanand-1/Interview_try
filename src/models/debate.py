"""Pydantic schema for Debate Protocol, Turns, and Transcript (PRD §9)."""

from typing import List, Optional, Dict
from datetime import datetime, timezone
from pydantic import BaseModel, Field


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DebateTurn(BaseModel):
    persona: str = Field(..., description="Persona speaking or 'general_secretary'")
    statement: str
    cites: List[str] = Field(default_factory=list, description="Citation IDs cited in this turn")
    responds_to: Optional[str] = Field(None, description="Persona being responded to if direct rebuttal")
    is_counter_question_response: bool = False


class DebateRound(BaseModel):
    round_num: int
    agenda_item: str
    turns: List[DebateTurn] = Field(default_factory=list)
    votes: Dict[str, Optional[int]] = Field(
        default_factory=dict,
        description="Per-persona integer scores (1-10) for this round"
    )
    score_deltas_from_previous_round: Dict[str, str] = Field(
        default_factory=dict,
        description="Explanation of score change and cited trigger, e.g. '+1 after hearing T-A8 cited'"
    )
    auto_resolve_triggered: Optional[str] = Field(
        None,
        description="'auto_hire' if unanimous >=8, 'auto_reject' if unanimous <=4, else None"
    )


class DebateTranscript(BaseModel):
    candidate_id: str
    candidate_name: str
    agenda: List[str] = Field(default_factory=list, description="3-6 highest tension agenda topics extracted by GS")
    rounds: List[DebateRound] = Field(default_factory=list)
    maturity_reached: bool = False
    total_rounds: int = 0
    finalized_at: datetime = Field(default_factory=get_utc_now)
