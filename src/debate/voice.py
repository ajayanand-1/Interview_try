"""Voice Debate Stretch Feature (PRD §16) - Native Multi-Persona TTS Playback."""

import sys
import subprocess
import shutil
import json
from pathlib import Path
from typing import Dict, Optional

# Ensure repo root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.config import settings
from src.models.debate import DebateTranscript

# Per-persona voice mapping using macOS native speech synthesis voices
VOICE_MAP: Dict[str, str] = {
    "general_secretary": "Daniel",        # British authoritative chair
    "technical_agent": "Alex",            # Methodical engineer
    "hr_culture_agent": "Samantha",       # Empathetic HR partner
    "hiring_manager_agent": "Fred",       # Executive hiring manager
    "skeptic_agent": "Ralph",             # Sharp skeptical cross-examiner
}


def play_voice_turn(persona: str, statement: str, dry_run: bool = False) -> None:
    """Synthesize and play back a turn using persona's assigned voice."""
    voice = VOICE_MAP.get(persona, "Daniel")
    clean_persona = persona.replace("_", " ").title()
    print(f"🎙 [{clean_persona} (Voice: {voice})]: \"{statement}\"")
    
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
