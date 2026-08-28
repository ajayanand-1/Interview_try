"""Utilities for citation validation, index generation, and traceability."""

import re
from typing import Dict, List, Set, Tuple
from src.models.rosetta import RosettaDocument
from src.models.memo import AgentMemo
from src.models.decision import FinalReportData


def extract_citation_ids(text: str) -> List[str]:
    """Extract citation IDs matching patterns like R-EDU-01, R-EXP-03, T-A4, T-Q2 from a string."""
    pattern = r"\b(R-[A-Z]+-\d+|T-[AQ]\d+|T-A\d+|T-Q\d+)\b"
    return list(set(re.findall(pattern, text)))


def build_citations_index(rosetta: RosettaDocument) -> Dict[str, str]:
    """Build a comprehensive lookup dictionary of citation_id -> source text from a RosettaDocument."""
    index: Dict[str, str] = {}
    
    # Resume citations
    for edu in rosetta.resume_facts.education:
        index[edu.citation_id] = f"{edu.degree} ({edu.institution or 'N/A'}, {edu.year or 'N/A'})"
        
    for exp in rosetta.resume_facts.experience:
        for claim in exp.claims:
            index[claim.citation_id] = f"[{exp.company} - {exp.role}] {claim.text}"
            
    # Transcript QA citations
    for qa in rosetta.transcript_facts.technical_qa:
        index[qa.qid] = f"Question ({qa.topic}): {qa.question}"
        index[qa.answer_citation_id] = f"Answer ({qa.topic}): {qa.answer}"
        
    # Behavioral citations
    bh = rosetta.transcript_facts.behavioral
    if bh.friction_event_citation_id and bh.friction_event_quote:
        index[bh.friction_event_citation_id] = f"Friction event: {bh.friction_event_quote}"
    if bh.skeptic_followup_citation_id and bh.skeptic_followup_quote:
        index[bh.skeptic_followup_citation_id] = f"Skeptic follow-up response: {bh.skeptic_followup_quote}"
        
    # Ownership/Hiring QA citations
    for oqa in rosetta.transcript_facts.ownership_hiring_qa:
        index[oqa.citation_id] = f"Gap probed [{oqa.gap_probed}] ({oqa.response_style}): {oqa.response_summary}"
        
    return index


def validate_memo_traceability(memo: AgentMemo, valid_citations: Set[str]) -> Tuple[bool, List[str]]:
    """Verify that all citation IDs in an agent memo exist in the valid citations set."""
    invalid = []
    for item in memo.strengths + memo.gaps:
        if item.citation_id not in valid_citations:
            invalid.append(item.citation_id)
    return len(invalid) == 0, invalid


def validate_report_traceability(report: FinalReportData, valid_citations: Set[str]) -> Tuple[bool, List[str]]:
    """Verify that all citation IDs in the final report exist in the valid citations set (PRD §15)."""
    invalid = []
    for item in report.strengths + report.concerns:
        if item.citation_id not in valid_citations:
            invalid.append(item.citation_id)
    return len(invalid) == 0, invalid
