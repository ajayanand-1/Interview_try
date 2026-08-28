"""End-to-End Unattended Multi-Agent System Test (PRD §15)."""

import json
from pathlib import Path
from src.config import settings
from src.builder import build_candidate_rosetta
from src.agents.sealed_memos import generate_sealed_memos, PERSONAS
from src.debate.orchestrator import run_debate_session
from src.decision.engine import synthesize_candidate_decision
from src.decision.reporter import generate_candidate_report_artifacts
from src.utils.citations import validate_report_traceability, validate_memo_traceability


def test_full_pipeline_ananya_iyer():
    """Run full unattended pipeline for Ananya Iyer and verify all phase deliverables."""
    cid = "ananya_iyer"
    
    # Phase 1
    rosetta = build_candidate_rosetta(cid)
    assert (settings.rosetta_dir / f"{cid}.json").exists()
    assert (settings.rosetta_dir / f"{cid}.md").exists()
    
    # Phase 2
    memos = generate_sealed_memos(cid, rosetta)
    assert len(memos) == 4
    for p in PERSONAS:
        assert (settings.memos_dir / f"{cid}_{p}.json").exists()
        assert (settings.memos_dir / f"{cid}_{p}.pdf").exists()
        valid, _ = validate_memo_traceability(memos[p], set(rosetta.citations_index.keys()))
        assert valid
        
    # Phase 3
    transcript = run_debate_session(cid, rosetta, memos)
    assert (settings.debate_dir / f"{cid}_transcript.json").exists()
    assert (settings.debate_dir / f"{cid}_transcript.md").exists()
    assert transcript.total_rounds >= 3
    
    # Phase 4
    report_data, json_p, pdf_p, md_p = generate_candidate_report_artifacts(
        cid, rosetta, memos, transcript
    )
    assert json_p.exists()
    assert pdf_p.exists()
    assert md_p.exists()
    assert report_data.final_recommendation == "hire"
    assert report_data.confidence_level == "high"

    # PRD §15 Traceability verification
    valid_cits = set(rosetta.citations_index.keys())
    is_traceable, invalid = validate_report_traceability(report_data, valid_cits)
    assert is_traceable, f"Untraceable citations found: {invalid}"


def test_full_pipeline_rohan_malhotra():
    """Run full unattended pipeline for Rohan Malhotra and verify all phase deliverables."""
    cid = "rohan_malhotra"
    
    # Phase 1
    rosetta = build_candidate_rosetta(cid)
    assert (settings.rosetta_dir / f"{cid}.json").exists()
    assert (settings.rosetta_dir / f"{cid}.md").exists()
    
    # Phase 2
    memos = generate_sealed_memos(cid, rosetta)
    assert len(memos) == 4
    for p in PERSONAS:
        assert (settings.memos_dir / f"{cid}_{p}.json").exists()
        assert (settings.memos_dir / f"{cid}_{p}.pdf").exists()
        valid, _ = validate_memo_traceability(memos[p], set(rosetta.citations_index.keys()))
        assert valid
        
    # Phase 3
    transcript = run_debate_session(cid, rosetta, memos)
    assert (settings.debate_dir / f"{cid}_transcript.json").exists()
    assert (settings.debate_dir / f"{cid}_transcript.md").exists()
    assert transcript.total_rounds >= 3
    
    # Phase 4
    report_data, json_p, pdf_p, md_p = generate_candidate_report_artifacts(
        cid, rosetta, memos, transcript
    )
    assert json_p.exists()
    assert pdf_p.exists()
    assert md_p.exists()
    assert report_data.final_recommendation == "no_hire"
    assert report_data.confidence_level == "high"

    # PRD §15 Traceability verification
    valid_cits = set(rosetta.citations_index.keys())
    is_traceable, invalid = validate_report_traceability(report_data, valid_cits)
    assert is_traceable, f"Untraceable citations found: {invalid}"
