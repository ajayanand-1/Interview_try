import sys
import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio
import re
import hashlib

# Ensure repo root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.config import settings
from src.models.debate import DebateTranscript
from src.agents.personas import PERSONA_PROFILES

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

# High-Definition Neural Voice Mapping for Human-Grade Realism
NEURAL_VOICE_MAP: Dict[str, Dict[str, Any]] = {
    "technical_agent": {
        "voice": "en-US-AriaNeural",       # Female: Expressive, clear, architectural authority
        "pitch": "+0Hz",
        "rate": "+0%",
        "volume": "+0%"
    },
    "hr_culture_agent": {
        "voice": "en-US-GuyNeural",        # Male: Warm, conversational, empathetic resonance
        "pitch": "-1Hz",
        "rate": "-2%",
        "volume": "+0%"
    },
    "hiring_manager_agent": {
        "voice": "en-US-ChristopherNeural", # Male: Decisive, pragmatic business leader
        "pitch": "-2Hz",
        "rate": "+1%",
        "volume": "+0%"
    },
    "skeptic_agent": {
        "voice": "en-US-JennyNeural",      # Female: Forensic, disciplined, analytical
        "pitch": "+1Hz",
        "rate": "-1%",
        "volume": "+0%"
    },
    "general_secretary": {
        "voice": "en-GB-RyanNeural",       # Male: Distinguished, parliamentary British moderator
        "pitch": "-2Hz",
        "rate": "-3%",
        "volume": "+0%"
    }
}

# Per-persona fixed voice mapping using macOS native speech synthesis voices (fallback)
VOICE_MAP: Dict[str, str] = {
    "general_secretary": "Daniel",        # Male: British authoritative chair
    "technical_agent": "Karen",           # Female: Methodical, precise AI architect
    "hr_culture_agent": "Oliver",         # Male: Empathetic, warm culture lead
    "hiring_manager_agent": "Fred",       # Male: Direct, pragmatic executive VP
    "skeptic_agent": "Samantha",          # Female: Sharp, forensic investigative critic
}


def clean_text_for_speech(text: str) -> str:
    """Strip bracketed citations, asterisks, and markdown for natural, humanly flowing speech."""
    # Remove citations like [T-A1], [R-EXP-04], [T-A7, T-A8]
    cleaned = re.sub(r'\[[A-Za-z0-9_\-,\s]+\]', '', text)
    # Remove markdown asterisks, hashes, backticks
    cleaned = re.sub(r'[*_#`]', '', cleaned)
    # Collapse multiple spaces and clean punctuation spacing
    cleaned = re.sub(r'\s+([.,;:!?])', r'\1', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def get_persona_voice_meta(persona: str) -> Dict[str, Any]:
    """Retrieve full voice and persona profile metadata."""
    prof = PERSONA_PROFILES.get(persona, {})
    neural_info = NEURAL_VOICE_MAP.get(persona, NEURAL_VOICE_MAP["general_secretary"])
    return {
        "persona": persona,
        "name": prof.get("name", persona.replace("_", " ").title()),
        "gender": prof.get("gender", "neutral"),
        "title": prof.get("title", "Evaluator"),
        "neural_voice": neural_info["voice"],
        "voice_macos": prof.get("voice_macos", VOICE_MAP.get(persona, "Daniel")),
        "pitch": prof.get("pitch", 1.0),
        "rate": prof.get("rate", 1.0)
    }


async def synthesize_neural_speech(
    text: str,
    persona: str,
    output_path: Optional[Path] = None
) -> Path:
    """Synthesize ultra-realistic humanly speech using Edge Neural TTS."""
    clean_txt = clean_text_for_speech(text)
    if not clean_txt:
        clean_txt = "Acknowledged."

    neural_cfg = NEURAL_VOICE_MAP.get(persona, NEURAL_VOICE_MAP["general_secretary"])
    voice = neural_cfg["voice"]
    rate = neural_cfg["rate"]
    pitch = neural_cfg["pitch"]

    if output_path is None:
        # Default cache path based on text hash
        text_hash = hashlib.md5(f"{persona}_{clean_txt}".encode("utf-8")).hexdigest()
        cache_dir = settings.data_dir / "cache" / "audio"
        cache_dir.mkdir(parents=True, exist_ok=True)
        output_path = cache_dir / f"{text_hash}.mp3"

    if output_path.exists() and output_path.stat().st_size > 1000:
        return output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if HAS_EDGE_TTS:
        communicate = edge_tts.Communicate(clean_txt, voice, rate=rate, pitch=pitch)
        await communicate.save(str(output_path))
    else:
        # Fallback dummy write
        with open(output_path, "wb") as f:
            f.write(b"")

    return output_path


def synthesize_turn_audio_sync(text: str, persona: str, output_path: Optional[Path] = None) -> Path:
    """Synchronous wrapper for synthesize_neural_speech."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(synthesize_neural_speech(text, persona, output_path))
        else:
            return asyncio.run(synthesize_neural_speech(text, persona, output_path))
    except Exception:
        return asyncio.run(synthesize_neural_speech(text, persona, output_path))


def play_voice_turn(persona: str, statement: str, dry_run: bool = False) -> None:
    """Synthesize and play back a turn using persona's assigned fixed voice."""
    meta = get_persona_voice_meta(persona)
    voice = meta["voice_macos"]
    name = meta["name"]
    gender_tag = "♀ Female" if meta["gender"] == "female" else "♂ Male"
    print(f"🎙 [{name} ({gender_tag}, Voice: {voice}, Neural: {meta['neural_voice']})]: \"{statement}\"")
    
    if not dry_run and shutil.which("say"):
        try:
            # Strip citation tags for cleaner speech synthesis
            clean_statement = statement.replace("[", "").replace("]", "").replace("*", "")
            subprocess.run(["say", "-v", voice, clean_statement], check=False)
        except Exception as e:
            print(f"Voice synthesis error: {e}")


def playback_debate_audio(transcript: DebateTranscript, dry_run: bool = False) -> None:
    """Play back the entire debate transcript sequentially across persona voices."""
    print(f"\n=======================================================")
    print(f"  VOICE DEBATE PLAYBACK: {transcript.candidate_name}")
    print(f"=======================================================\n")

    for rnd in transcript.rounds:
        print(f"\n>>> ROUND {rnd.round_num}: {rnd.agenda_item} <<<\n")
        for turn in rnd.turns:
            play_voice_turn(turn.persona, turn.statement, dry_run=dry_run)
            
        print(f"\n--- End of Round {rnd.round_num} Integer Votes ---")
        for p, s in rnd.votes.items():
            print(f"  • {p.replace('_', ' ').title()}: {s}/10")
        print("---------------------------------------------------\n")


if __name__ == "__main__":
    cid = sys.argv[1] if len(sys.argv) > 1 else "ananya_iyer"
    json_path = settings.debate_dir / f"{cid}_transcript.json"
    if not json_path.exists():
        print(f"Debate transcript not found: {json_path}. Run debate orchestrator first.")
        sys.exit(1)
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    t = DebateTranscript.model_validate(data)
    playback_debate_audio(t, dry_run=True)
