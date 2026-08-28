"""Tests for Voice Debate Playback (PRD §16)."""

import json
from pathlib import Path
from src.config import settings
from src.builder import build_candidate_rosetta
from src.agents.sealed_memos import generate_sealed_memos
from src.debate.orchestrator import run_debate_session
from src.debate.voice import VOICE_MAP, playback_debate_audio, play_voice_turn


def test_voice_mapping_coverage():
    """Verify distinct voice mappings for all personas."""
    assert "general_secretary" in VOICE_MAP
    assert "technical_agent" in VOICE_MAP
    assert "hr_culture_agent" in VOICE_MAP
    assert "hiring_manager_agent" in VOICE_MAP
    assert "skeptic_agent" in VOICE_MAP


def test_voice_playback_dry_run():
    """Verify voice playback functions without error in dry run mode."""
    rosetta = build_candidate_rosetta("ananya_iyer")
    memos = generate_sealed_memos("ananya_iyer", rosetta)
    transcript = run_debate_session("ananya_iyer", rosetta, memos)
    
    # Should execute without throwing exception
    playback_debate_audio(transcript, dry_run=True)
