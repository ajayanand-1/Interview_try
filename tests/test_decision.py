"""Tests for Decision Engine, Overrides, and Final Report Generator (PRD §10, §11, §15)."""

import json
from pathlib import Path
from src.config import settings
from src.builder import build_candidate_rosetta
from src.agents.sealed_memos import generate_sealed_memos
from src.debate.orchestrator import run_debate_session
from src.decision.engine import synthesize_candidate_decision
from src.decision.reporter import generate_candidate_report_artifacts
from src.models.decision import FinalReportData
from src.utils.citations import validate_report_traceability


def test_ananya_decision_and_traceability():
    """PRD §15 Traceability Test & Report Verification for Ananya Iyer."""
    rosetta = build_candidate_rosetta("ananya_iyer")
    memos = generate_sealed_memos("ananya_iyer", rosetta)
    transcript = run_debate_session("ananya_iyer", rosetta, memos)
    report_data, json_p, pdf_p, md_p = generate_candidate_report_artifacts(
        "ananya_iyer", rosetta, memos, transcript
    )

    assert isinstance(report_data, FinalReportData)
    assert report_data.final_recommendation == "hire"
    assert report_data.confidence_level == "high"

    # PRD §15 Traceability Test: All claims MUST resolve to valid citation IDs
    valid_citations = set(rosetta.citations_index.keys())
    is_traceable, invalid = validate_report_traceability(report_data, valid_citations)
    assert is_traceable, f"Found untraceable citation IDs: {invalid}"

    # Override motion test
    assert report_data.decision_path.override_motion_filed is True
    assert report_data.decision_path.override_motion is not None
    assert report_data.decision_path.override_motion.passed is False
    assert report_data.decision_path.override_motion.support_count == 1

    # Check files on disk
    assert json_p.exists()
    assert pdf_p.exists()
    assert md_p.exists()
    assert pdf_p.stat().st_size > 2000
    assert md_p.stat().st_size > 1000


def test_rohan_decision_and_traceability():
    """PRD §15 Traceability Test & Report Verification for Rohan Malhotra."""
    rosetta = build_candidate_rosetta("rohan_malhotra")
    memos = generate_sealed_memos("rohan_malhotra", rosetta)
    transcript = run_debate_session("rohan_malhotra", rosetta, memos)
    report_data, json_p, pdf_p, md_p = generate_candidate_report_artifacts(
        "rohan_malhotra", rosetta, memos, transcript
    )

    assert isinstance(report_data, FinalReportData)
    assert report_data.final_recommendation == "no_hire"
    assert report_data.confidence_level == "high"

    # PRD §15 Traceability Test
    valid_citations = set(rosetta.citations_index.keys())
    is_traceable, invalid = validate_report_traceability(report_data, valid_citations)
    assert is_traceable, f"Found untraceable citation IDs: {invalid}"

    # Dual outcome preservation: Both original and final outcomes are retained
    assert report_data.decision_path.original_gs_decision == "no_hire"
    assert report_data.decision_path.final_decision_after_overrides == "no_hire"
    assert len(report_data.decision_path.original_gs_rationale.strip()) > 50

    # Check files on disk
    assert json_p.exists()
    assert pdf_p.exists()
    assert md_p.exists()
