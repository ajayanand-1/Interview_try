"""Tests for Debate Orchestrator and General Secretary (PRD §9)."""

import json
from pathlib import Path
from src.config import settings
from src.builder import build_candidate_rosetta
from src.agents.sealed_memos import generate_sealed_memos
from src.debate.orchestrator import (
    run_debate_session,
    check_auto_resolve,
    generate_debate_agenda
)
from src.models.debate import DebateTranscript


def test_auto_resolve_logic():
    """PRD §9: Unanimous >= 8 auto-hires, unanimous <= 4 auto-rejects."""
    hire_votes = {"p1": 8, "p2": 9, "p3": 8, "p4": 10}
    assert check_auto_resolve(hire_votes) == "auto_hire"

    reject_votes = {"p1": 4, "p2": 3, "p3": 2, "p4": 4}
    assert check_auto_resolve(reject_votes) == "auto_reject"

    split_votes = {"p1": 7, "p2": 4, "p3": 6, "p4": 3}
    assert check_auto_resolve(split_votes) is None


def test_ananya_debate_orchestration():
    """Test full debate execution for Ananya Iyer."""
    rosetta = build_candidate_rosetta("ananya_iyer")
    memos = generate_sealed_memos("ananya_iyer", rosetta)
    transcript = run_debate_session("ananya_iyer", rosetta, memos)

    assert isinstance(transcript, DebateTranscript)
    assert transcript.candidate_id == "ananya_iyer"
    assert len(transcript.agenda) == 3
    assert transcript.total_rounds >= 3
    assert transcript.maturity_reached is True

    # Verify at least one rebuttal turn occurred (PRD §9 requirement)
    rebuttal_turns = [
        t for r in transcript.rounds for t in r.turns if t.responds_to is not None
    ]
    assert len(rebuttal_turns) >= 1

    # Verify counter-question response occurred
    cq_turns = [
        t for r in transcript.rounds for t in r.turns if t.is_counter_question_response
    ]
    assert len(cq_turns) >= 1

    # Verify disk files
    json_path = settings.debate_dir / "ananya_iyer_transcript.json"
    md_path = settings.debate_dir / "ananya_iyer_transcript.md"
    assert json_path.exists()
    assert md_path.exists()
    assert md_path.stat().st_size > 1000


def test_rohan_debate_orchestration():
    """Test full debate execution for Rohan Malhotra."""
    rosetta = build_candidate_rosetta("rohan_malhotra")
    memos = generate_sealed_memos("rohan_malhotra", rosetta)
    transcript = run_debate_session("rohan_malhotra", rosetta, memos)

    assert isinstance(transcript, DebateTranscript)
    assert transcript.candidate_id == "rohan_malhotra"
    assert len(transcript.agenda) == 3
    assert transcript.total_rounds >= 3

    # Check that deltas explain score shifts
    all_deltas = [
        delta for r in transcript.rounds for delta in r.score_deltas_from_previous_round.values()
    ]
    assert len(all_deltas) >= 1

    # Verify disk files
    json_path = settings.debate_dir / "rohan_malhotra_transcript.json"
    md_path = settings.debate_dir / "rohan_malhotra_transcript.md"
    assert json_path.exists()
    assert md_path.exists()
