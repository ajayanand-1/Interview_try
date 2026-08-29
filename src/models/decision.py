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


class PersonaFeedbackItem(BaseModel):
    persona: str = Field(..., description="Persona key, e.g. hr_culture_agent, skeptic_agent, hiring_manager_agent, technical_agent, general_secretary")
    headline: str = Field(..., description="Key takeaway headline from this persona")
    feedback: str = Field(..., description="Constructive evaluation feedback")
    key_recommendation: str = Field(..., description="Actionable recommendation for improvement")


class ResumeImprovementItem(BaseModel):
    section: str = Field(..., description="Resume section or topic, e.g. Experience Metrics, Project Attribution, Architecture Claims")
    current_issue: str = Field(..., description="Issue or gap identified during evaluation")
    recommendation: str = Field(..., description="Specific recommendation for rewriting or restructuring")
    example_before: Optional[str] = Field(None, description="Problematic or vague text from current resume")
    example_after: Optional[str] = Field(None, description="Stronger, bulletproof rewrite example")


class RequiredSkillItem(BaseModel):
    skill_category: str = Field(..., description="Skill category, e.g. Multi-Agent Frameworks, Production Observability")
    target_job_expectation: str = Field(..., description="What the company/job demands for this role")
    current_candidate_level: str = Field(..., description="Candidate's current verified capability")
    growth_path: str = Field(..., description="Concrete steps or projects to achieve mastery")


class CompanyExpectationItem(BaseModel):
    pillar: str = Field(..., description="Evaluation pillar, e.g. Production Resilience, Retention Stability, Attribution Integrity")
    company_standard: str = Field(..., description="What top engineering orgs expect")
    assessment_finding: str = Field(..., description="How candidate performed against this standard")
    advice_for_future_interviews: str = Field(..., description="Guidance for meeting company expectations in future interviews")


class CandidateFeedback(BaseModel):
    overall_summary: str = Field(..., description="High-level feedback overview across all 5 evaluation perspectives")
    resume_improvements: List[ResumeImprovementItem] = Field(default_factory=list)
    required_skills: List[RequiredSkillItem] = Field(default_factory=list)
    company_expectations: List[CompanyExpectationItem] = Field(default_factory=list)
    persona_feedback: List[PersonaFeedbackItem] = Field(default_factory=list)


class FinalReportData(BaseModel):
    candidate_id: str
    candidate_name: str
    final_recommendation: Literal["hire", "no_hire"]
    confidence_level: Literal["low", "medium", "high"]
    strengths: List[EvidenceItem] = Field(default_factory=list)
    concerns: List[EvidenceItem] = Field(default_factory=list)
    unresolved_disagreements: List[UnresolvedDisagreement] = Field(default_factory=list)
    decision_path: FinalDecisionPath
    feedback: Optional[CandidateFeedback] = Field(default=None, description="Comprehensive feedback for candidate improvement")
    generated_at: datetime = Field(default_factory=get_utc_now)
