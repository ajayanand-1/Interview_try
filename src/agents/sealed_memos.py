"""Sealed Memo Orchestration and Artifact Generation (PRD §7, §8)."""

import sys
from pathlib import Path

# Ensure repo root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import json
from typing import Dict, List, Optional
import pypdf

from src.config import settings
from src.builder import build_candidate_rosetta
from src.models.rosetta import RosettaDocument
from src.models.memo import AgentMemo, PersonaType
from src.agents.runner import call_gemini_agent
from src.utils.pdf_export import export_memo_to_pdf
from src.utils.citations import validate_memo_traceability


PERSONAS: List[PersonaType] = [
    "technical_agent",
    "hr_culture_agent",
    "hiring_manager_agent",
    "skeptic_agent"
]


def load_job_description_text() -> str:
    """Read the job description text from PDF."""
    jd_path = settings.data_dir / "job_description.pdf"
    if not jd_path.exists():
        return "Job Description: AI Engineer — Agentic Systems (Freight Operations) at Cargonet AI."
    reader = pypdf.PdfReader(str(jd_path))
    return "\n".join([page.extract_text() or "" for page in reader.pages])


def generate_sealed_memos(
    candidate_id: str,
    rosetta: Optional[RosettaDocument] = None
) -> Dict[PersonaType, AgentMemo]:
    """Generate all four isolated sealed memos for a candidate and persist to disk."""
    settings.ensure_directories()
    
    if rosetta is None:
        rosetta = build_candidate_rosetta(candidate_id)
        
    jd_text = load_job_description_text()
    memos: Dict[PersonaType, AgentMemo] = {}
    valid_citations = set(rosetta.citations_index.keys())

    print(f"\n[Phase 2] Generating sealed memos for {rosetta.candidate_name} ({rosetta.candidate_id})...")

    for persona in PERSONAS:
        # Isolated call - only receives JD and Rosetta
        memo = call_gemini_agent(persona, rosetta, jd_text)
        
        # Enforce traceability
        is_traceable, invalid_cits = validate_memo_traceability(memo, valid_citations)
        if not is_traceable:
            print(f"Warning: {persona} cited unknown citation IDs: {invalid_cits}")

        memos[persona] = memo

        # Write candidate-prefixed JSON artifact
        json_path = settings.memos_dir / f"{candidate_id}_{persona}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(memo.model_dump_json(indent=2))

        # Write candidate-prefixed PDF artifact
        pdf_path = settings.memos_dir / f"{candidate_id}_{persona}.pdf"
        export_memo_to_pdf(memo, pdf_path)

        # Write alias files (memos/{persona}.json and memos/{persona}.pdf)
        alias_json = settings.memos_dir / f"{persona}.json"
        with open(alias_json, "w", encoding="utf-8") as f:
            f.write(memo.model_dump_json(indent=2))
        export_memo_to_pdf(memo, settings.memos_dir / f"{persona}.pdf")

        score_str = str(memo.score) if memo.score is not None else "N/A"
        print(f"   ✓ Sealed {persona:22s} | Score: {score_str:>3s}/10 | Conf: {memo.confidence:6s} | Strengths: {len(memo.strengths)} | Gaps: {len(memo.gaps)}")

    return memos


if __name__ == "__main__":
    for cid in ["ananya_iyer", "rohan_malhotra"]:
        generate_sealed_memos(cid)
