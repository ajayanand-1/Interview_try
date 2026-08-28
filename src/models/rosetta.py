"""Pydantic schema for Candidate Rosetta Document (PRD §6)."""

from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field


class EducationFact(BaseModel):
    degree: str
    institution: Optional[str] = None
    year: Optional[int] = None
    citation_id: str = Field(..., description="Stable citation ID, e.g., R-EDU-01")


class ExperienceClaim(BaseModel):
    text: str
    citation_id: str = Field(..., description="Stable citation ID, e.g., R-EXP-01")


class ExperienceFact(BaseModel):
    company: str
    role: str
    start: str
    end: str
    tenure_years: float
    claims: List[ExperienceClaim] = Field(default_factory=list)


class ResumeFacts(BaseModel):
    education: List[EducationFact] = Field(default_factory=list)
    experience: List[ExperienceFact] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)


class TechnicalQA(BaseModel):
    qid: str = Field(..., description="Question ID, e.g. T-Q1")
    topic: str
    question: str
    answer: str
    answer_citation_id: str = Field(..., description="Answer citation ID, e.g. T-A1")
    is_followup: bool = False
    influenced_by: Optional[str] = Field(None, description="Earlier question/answer citation if answer shifted")
    self_disclosed_gap: bool = False


class BehavioralFacts(BaseModel):
    friction_event_citation_id: Optional[str] = None
    friction_event_quote: Optional[str] = None
    skeptic_followup_citation_id: Optional[str] = None
    skeptic_followup_quote: Optional[str] = None
    skeptic_followup_word_count: Optional[int] = None
    skeptic_followup_defensiveness: Optional[Literal["low", "medium", "high", "none"]] = "none"
    friction_notes: Optional[str] = None


class OwnershipHiringQA(BaseModel):
    qid: str
    gap_probed: str
    response_summary: str
    response_quote: Optional[str] = None
    response_style: Literal["direct_acknowledgment", "defensive", "evasive", "partial"]
    citation_id: str = Field(..., description="Citation ID, e.g. T-A8")


class TranscriptFacts(BaseModel):
    technical_qa: List[TechnicalQA] = Field(default_factory=list)
    behavioral: BehavioralFacts = Field(default_factory=BehavioralFacts)
    ownership_hiring_qa: List[OwnershipHiringQA] = Field(default_factory=list)


class ConsistencyFlag(BaseModel):
    claim_citation_id: str
    transcript_citation_id: str
    description: str
    severity: Literal["low", "medium", "high"]


class RosettaDocument(BaseModel):
    candidate_id: str = Field(..., description="Unique slug, e.g. ananya_iyer or rohan_malhotra")
    candidate_name: str
    job_title: str = "AI Engineer — Agentic Systems"
    resume_facts: ResumeFacts
    transcript_facts: TranscriptFacts
    consistency_flags: List[ConsistencyFlag] = Field(default_factory=list)
    citations_index: Dict[str, str] = Field(
        default_factory=dict,
        description="Index mapping citation_id -> exact text quote / fact for traceability"
    )

    def get_citation(self, citation_id: str) -> Optional[str]:
        """Resolve a citation ID to its source text."""
        return self.citations_index.get(citation_id)
