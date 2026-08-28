"""Tests for Streamlit data normalization and defensive rendering helpers."""

import pytest
from streamlit_app import (
    safe_text,
    safe_upper,
    safe_lower,
    safe_title,
    safe_list,
    safe_dict
)


def test_safe_text():
    assert safe_text("hello") == "hello"
    assert safe_text("  trimmed  ") == "trimmed"
    assert safe_text(None) == "Not available"
    assert safe_text("", fallback="Custom Fallback") == "Custom Fallback"
    assert safe_text(123) == "123"


def test_safe_upper():
    assert safe_upper("hire") == "HIRE"
    assert safe_upper(None) == "NOT AVAILABLE"
    assert safe_upper("", fallback="N/A") == "N/A"
    assert safe_upper("mixed_CASE") == "MIXED_CASE"


def test_safe_lower():
    assert safe_lower("HIRE") == "hire"
    assert safe_lower(None) == "not available"
    assert safe_lower("") == "not available"


def test_safe_title():
    assert safe_title("ai_engineer_freight") == "Ai Engineer Freight"
    assert safe_title(None) == "Not Available"
    assert safe_title("technical_agent") == "Technical Agent"


def test_safe_list():
    assert safe_list([1, 2, 3]) == [1, 2, 3]
    assert safe_list(None) == []
    assert safe_list((1, 2)) == [1, 2]
    assert safe_list("single_string") == ["single_string"]


def test_safe_dict():
    assert safe_dict({"a": 1}) == {"a": 1}
    assert safe_dict(None) == {}
    assert safe_dict("not a dict") == {}
    assert safe_dict([1, 2, 3]) == {}


def test_synthetic_malformed_evaluation_data():
    """Verify that a synthetic evaluation object with None/missing fields does not crash."""
    synthetic_eval = {
        "candidate_id": None,
        "candidate_name": None,
        "final_recommendation": None,
        "confidence_level": None,
        "strengths": [
            {"claim": None, "citation_id": None},
            None,
        ],
        "concerns": None,
        "resume_facts": [
            {"category": None, "fact": None, "citation_id": None}
        ],
        "transcript_facts": [
            {"question_summary": None, "answer_claim": None, "citation_id": None}
        ],
        "decision_path": {
            "original_gs_rationale": None,
            "override_motion": {
                "filed_by": None,
                "motion_text": None,
                "passed": None,
                "support_count": None
            }
        }
    }

    # Test processing of resume facts
    for rf in safe_list(synthetic_eval.get("resume_facts")):
        if isinstance(rf, dict):
            cat = safe_upper(rf.get("category"), "FACT")
            fact = safe_text(rf.get("fact"), "No fact recorded")
            cit = safe_text(rf.get("citation_id"), "N/A")
            assert cat == "FACT"
            assert fact == "No fact recorded"
            assert cit == "N/A"

    # Test processing of strengths
    for s in safe_list(synthetic_eval.get("strengths")):
        if isinstance(s, dict):
            claim = safe_text(s.get("claim"), "No claim recorded")
            cit = safe_text(s.get("citation_id"), "N/A")
            assert claim == "No claim recorded"
            assert cit == "N/A"

    # Test processing of decision path
    dp = safe_dict(synthetic_eval.get("decision_path"))
    rationale = safe_text(dp.get("original_gs_rationale"), "No rationale recorded.")
    assert rationale == "No rationale recorded."

    ov = safe_dict(dp.get("override_motion"))
    filed_by = safe_title(ov.get("filed_by"), "Unknown Agent")
    assert filed_by == "Unknown Agent"
