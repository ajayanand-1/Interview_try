"""Tests for Candidate Profile Builder ("Project Rosetta") - PRD §6."""

import json
from pathlib import Path
from src.config import settings
from src.builder import build_candidate_rosetta
from src.models.rosetta import RosettaDocument


def test_build_ananya_iyer_rosetta():
    """Test generating Rosetta document for Ananya Iyer."""
    rosetta = build_candidate_rosetta("ananya_iyer")
    assert isinstance(rosetta, RosettaDocument)
    assert rosetta.candidate_id == "ananya_iyer"
    assert rosetta.candidate_name == "Ananya Iyer"
    
    # Check resume facts
    assert len(rosetta.resume_facts.education) >= 1
    assert len(rosetta.resume_facts.experience) == 2
    assert "Python" in rosetta.resume_facts.skills
    assert "Chroma" in rosetta.resume_facts.skills

    # Check transcript facts
    assert len(rosetta.transcript_facts.technical_qa) == 4
    assert rosetta.transcript_facts.behavioral.skeptic_followup_defensiveness == "low"
    assert rosetta.transcript_facts.behavioral.skeptic_followup_word_count == 41
    
    # Check consistency flag
    assert len(rosetta.consistency_flags) == 1
    flag = rosetta.consistency_flags[0]
    assert flag.claim_citation_id == "R-EXP-03"
    assert flag.transcript_citation_id == "T-A2"
    assert flag.severity == "low"

    # Check disk artifacts
    json_file = settings.rosetta_dir / "ananya_iyer.json"
    md_file = settings.rosetta_dir / "ananya_iyer.md"
    assert json_file.exists()
    assert md_file.exists()
    assert md_file.stat().st_size > 1000


def test_build_rohan_malhotra_rosetta():
    """Test generating Rosetta document for Rohan Malhotra."""
    rosetta = build_candidate_rosetta("rohan_malhotra")
    assert isinstance(rosetta, RosettaDocument)
    assert rosetta.candidate_id == "rohan_malhotra"
    assert rosetta.candidate_name == "Rohan Malhotra"

    # Check resume facts
    assert len(rosetta.resume_facts.experience) == 3
    assert "LangGraph" in rosetta.resume_facts.skills
    assert len(rosetta.resume_facts.certifications) == 1

    # Check transcript facts
    assert len(rosetta.transcript_facts.technical_qa) == 4
    assert rosetta.transcript_facts.behavioral.skeptic_followup_defensiveness == "medium"
    
    # Check high severity consistency flag (sole architect walkback)
    assert len(rosetta.consistency_flags) >= 1
    flag = rosetta.consistency_flags[0]
    assert flag.claim_citation_id == "R-EXP-03"
    assert flag.transcript_citation_id == "T-A7"
    assert flag.severity == "high"

    # Check disk artifacts
    json_file = settings.rosetta_dir / "rohan_malhotra.json"
    md_file = settings.rosetta_dir / "rohan_malhotra.md"
    assert json_file.exists()
    assert md_file.exists()
    assert md_file.stat().st_size > 1000


def test_rosetta_citations_index_integrity():
    """Test that all citations in index resolve to non-empty strings."""
    for cid in ["ananya_iyer", "rohan_malhotra"]:
        json_file = settings.rosetta_dir / f"{cid}.json"
        with open(json_file, "r") as f:
            data = json.load(f)
        rosetta = RosettaDocument.model_validate(data)
        
        assert len(rosetta.citations_index) >= 15
        for cit_id, cit_text in rosetta.citations_index.items():
            assert cit_id.strip() != ""
            assert cit_text.strip() != ""
