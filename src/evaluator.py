"""Universal Evaluation Pipeline Entrypoint (Phase 6A/6B)."""

import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

# Ensure repo root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.workspace import RunWorkspace
from src.builder import build_candidate_rosetta
from src.agents.sealed_memos import generate_sealed_memos
from src.debate.orchestrator import run_debate_session
from src.debate.voice import playback_debate_audio
from src.decision.engine import synthesize_candidate_decision
from src.decision.reporter import generate_candidate_report_artifacts
from src.api.services.evaluation_service import save_status
from src.models.rosetta import RosettaDocument
from src.models.memo import AgentMemo, PersonaType
from src.models.debate import DebateTranscript
from src.models.decision import FinalReportData


@dataclass
class EvaluationResult:
    workspace: RunWorkspace
    rosetta: RosettaDocument
    memos: Dict[PersonaType, AgentMemo]
    transcript: DebateTranscript
    report_data: FinalReportData
    json_path: Path
    pdf_path: Path
    md_path: Path


def evaluate_candidate(
    candidate_id: str,
    candidate_name: Optional[str] = None,
    job_id: str = "default_job",
    run_id: Optional[str] = None,
    base_runs_dir: Optional[Path] = None,
    job_description_path: Optional[Path] = None,
    resume_path: Optional[Path] = None,
    transcript_path: Optional[Path] = None,
    workspace: Optional[RunWorkspace] = None,
    enable_voice: bool = False,
    dry_run_voice: bool = False,
) -> EvaluationResult:
    """Execute complete end-to-end evaluation pipeline inside an isolated run workspace."""
    if workspace is None:
        workspace = RunWorkspace.create(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            job_id=job_id,
            run_id=run_id,
            base_runs_dir=base_runs_dir,
            job_description_path=job_description_path,
            resume_path=resume_path,
            transcript_path=transcript_path
        )

    save_status(workspace, status="running", phase="rosetta")

    # Phase 1: Candidate Profile Builder
    rosetta = build_candidate_rosetta(
        candidate_id=workspace.candidate_id,
        candidate_name=workspace.candidate_name,
        workspace=workspace
    )

    # Phase 2: Isolated Personas (Sealed Memos)
    save_status(workspace, status="running", phase="agents")
    memos = generate_sealed_memos(
        candidate_id=workspace.candidate_id,
        rosetta=rosetta,
        workspace=workspace
    )

    # Phase 3: Debate Orchestrator & General Secretary
    save_status(workspace, status="running", phase="debate")
    transcript = run_debate_session(
        candidate_id=workspace.candidate_id,
        rosetta=rosetta,
        memos=memos,
        workspace=workspace
    )

    # Phase 6 Stretch: Multi-Persona Voice Playback
    if enable_voice or dry_run_voice:
        playback_debate_audio(transcript, dry_run=dry_run_voice)

    # Phase 4: Decision & Final Report Generation
    save_status(workspace, status="running", phase="decision")
    report_data = synthesize_candidate_decision(
        candidate_id=workspace.candidate_id,
        rosetta=rosetta,
        memos=memos,
        transcript=transcript,
        workspace=workspace
    )

    save_status(workspace, status="running", phase="report")
    report_data, json_p, pdf_p, md_p = generate_candidate_report_artifacts(
        candidate_id=workspace.candidate_id,
        rosetta=rosetta,
        memos=memos,
        transcript=transcript,
        report_data=report_data,
        workspace=workspace
    )

    save_status(workspace, status="completed", phase="finalized")

    return EvaluationResult(
        workspace=workspace,
        rosetta=rosetta,
        memos=memos,
        transcript=transcript,
        report_data=report_data,
        json_path=json_p,
        pdf_path=pdf_p,
        md_path=md_p
    )
