"""Tests for Voice Debate Playback (PRD §16)."""

import json
from pathlib import Path
from src.config import settings
from src.builder import build_candidate_rosetta
from src.agents.sealed_memos import generate_sealed_memos
from src.debate.orchestrator import run_debate_session
from src.debate.voice import (
    VOICE_MAP,
    NEURAL_VOICE_MAP,
    playback_debate_audio,
    play_voice_turn,
    clean_text_for_speech,
    synthesize_neural_speech,
    get_persona_voice_meta,
)


def test_voice_mapping_coverage():
    """Verify distinct voice mappings and 2-female / 2-male assignments for all personas."""
    assert "general_secretary" in VOICE_MAP
    assert "technical_agent" in VOICE_MAP
    assert "hr_culture_agent" in VOICE_MAP
    assert "hiring_manager_agent" in VOICE_MAP
    assert "skeptic_agent" in VOICE_MAP

    # Verify neural voice mapping
    assert len(NEURAL_VOICE_MAP) == 5
    assert NEURAL_VOICE_MAP["technical_agent"]["voice"] == "en-US-AriaNeural"
    assert NEURAL_VOICE_MAP["hr_culture_agent"]["voice"] == "en-US-GuyNeural"
    assert NEURAL_VOICE_MAP["hiring_manager_agent"]["voice"] == "en-US-ChristopherNeural"
    assert NEURAL_VOICE_MAP["skeptic_agent"]["voice"] == "en-US-JennyNeural"
    assert NEURAL_VOICE_MAP["general_secretary"]["voice"] == "en-GB-RyanNeural"


def test_clean_text_for_natural_speech():
    """Verify citations and formatting are cleaned for natural speech prosody."""
    raw = "Candidate has solid single-agent RAG [T-A1] but lacking LangGraph [T-A3, T-A4]. *Emphasis* here."
    cleaned = clean_text_for_speech(raw)
    assert "[T-A1]" not in cleaned
    assert "[T-A3, T-A4]" not in cleaned
    assert "*" not in cleaned
    assert "Candidate has solid single-agent RAG but lacking LangGraph. Emphasis here." == cleaned


def test_persona_voice_metadata_gender_balance():
    """Verify exactly 2 female and 2 male evaluators plus chair."""
    tech_meta = get_persona_voice_meta("technical_agent")
    hr_meta = get_persona_voice_meta("hr_culture_agent")
    hm_meta = get_persona_voice_meta("hiring_manager_agent")
    skep_meta = get_persona_voice_meta("skeptic_agent")

    assert tech_meta["gender"] == "female"
    assert skep_meta["gender"] == "female"
    assert hr_meta["gender"] == "male"
    assert hm_meta["gender"] == "male"


def test_voice_playback_dry_run():
    """Verify voice playback functions without error in dry run mode."""
    rosetta = build_candidate_rosetta("ananya_iyer")
    memos = generate_sealed_memos("ananya_iyer", rosetta)
    transcript = run_debate_session("ananya_iyer", rosetta, memos)
    
    # Should execute without throwing exception
    playback_debate_audio(transcript, dry_run=True)

