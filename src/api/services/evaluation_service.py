"""Background Evaluation Service and Status Management (Phase 6B)."""

import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from src.config import settings
from src.workspace import RunWorkspace
from src.builder import build_candidate_rosetta
from src.agents.sealed_memos import generate_sealed_memos, PERSONAS
from src.debate.orchestrator import run_debate_session
from src.decision.engine import synthesize_candidate_decision
from src.decision.reporter import generate_candidate_report_artifacts


def get_status_file(workspace_or_dir: Any) -> Path:
    """Return path to status.json within a workspace root directory."""
    if isinstance(workspace_or_dir, RunWorkspace):
        return workspace_or_dir.root_dir / "status.json"
    elif isinstance(workspace_or_dir, Path):
        return workspace_or_dir / "status.json"
    else:
        return Path(workspace_or_dir) / "status.json"


def save_status(
    workspace: RunWorkspace,
    status: str,
    phase: str,
    error: Optional[str] = None
) -> Dict[str, Any]:
    """Persist run status and phase to status.json inside the run workspace."""
    now_iso = datetime.now(timezone.utc).isoformat()
    status_path = get_status_file(workspace)
    
    # Read existing created_at if present
    created_at = now_iso
    if status_path.exists():
        try:
            with open(status_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                created_at = data.get("created_at", now_iso)
        except Exception:
            pass

    status_data = {
        "run_id": workspace.run_id,
        "candidate_id": workspace.candidate_id,
        "candidate_name": workspace.candidate_name,
        "job_id": workspace.job_id,
        "status": status,  # "queued", "running", "completed", "failed"
        "phase": phase,    # "ingestion", "rosetta", "agents", "debate", "decision", "report", "finalized"
        "error": error,
        "created_at": created_at,
        "updated_at": now_iso
    }

    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2)

    return status_data


def load_status(run_id: str, base_runs_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Read status.json for a given run_id."""
    runs_root = base_runs_dir or settings.runs_dir
    run_dir = runs_root / run_id
    if not run_dir.exists():
        return None

    status_file = run_dir / "status.json"
    if status_file.exists():
        try:
            with open(status_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # If status.json doesn't exist, inspect rosetta files or infer state from disk artifacts
    cid = run_id.replace("run_", "").split("_")[0]
    c_name = cid.replace("_", " ").title()

    rosetta_files = list((run_dir / "rosetta").glob("*.json")) if (run_dir / "rosetta").exists() else []
    if rosetta_files:
        try:
            with open(rosetta_files[0], "r", encoding="utf-8") as f:
                rdata = json.load(f)
                cid = rdata.get("candidate_id", cid)
                c_name = rdata.get("candidate_name", c_name)
        except Exception:
            pass

    rosetta_exists = len(rosetta_files) > 0
    report_exists = (run_dir / "reports").exists() and any((run_dir / "reports").glob("*_decision.json"))

    return {
        "run_id": run_id,
        "candidate_id": cid,
        "candidate_name": c_name,
        "job_id": "default_job",
        "status": "completed" if report_exists else ("running" if rosetta_exists else "unknown"),
        "phase": "report" if report_exists else ("rosetta" if rosetta_exists else "unknown"),
        "error": None,
        "created_at": datetime.fromtimestamp(run_dir.stat().st_ctime, timezone.utc).isoformat(),
        "updated_at": datetime.fromtimestamp(run_dir.stat().st_mtime, timezone.utc).isoformat()
    }


def list_all_evaluations(base_runs_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Scan all runs in runs_dir and return sorted evaluation run summaries."""
    runs_root = base_runs_dir or settings.runs_dir
    if not runs_root.exists():
        return []

    evaluations = []
    for d in sorted(runs_root.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if d.is_dir() and not d.name.startswith("."):
            info = load_status(d.name, base_runs_dir=runs_root)
            if info:
                evaluations.append(info)

    return evaluations


def get_workspace_for_run(run_id: str, base_runs_dir: Optional[Path] = None) -> Optional[RunWorkspace]:
    """Reconstruct a RunWorkspace object for an existing run_id."""
    runs_root = base_runs_dir or settings.runs_dir
    root_dir = runs_root / run_id
    if not root_dir.exists():
        return None

    status_data = load_status(run_id, base_runs_dir=runs_root)
    cid = status_data.get("candidate_id", "unknown_candidate") if status_data else "unknown_candidate"
    c_name = status_data.get("candidate_name", cid.replace("_", " ").title()) if status_data else cid.replace("_", " ").title()
    job_id = status_data.get("job_id", "default_job") if status_data else "default_job"

    input_dir = root_dir / "input"
    rosetta_dir = root_dir / "rosetta"
    memos_dir = root_dir / "memos"
    debate_dir = root_dir / "debate"
    reports_dir = root_dir / "reports"

    jd_p = input_dir / "job_description.pdf"
    res_p = input_dir / "resume.pdf"
    trn_p = input_dir / "transcript.pdf"

    return RunWorkspace(
        run_id=run_id,
        candidate_id=cid,
        candidate_name=c_name,
        job_id=job_id,
        root_dir=root_dir,
        input_dir=input_dir,
        rosetta_dir=rosetta_dir,
        memos_dir=memos_dir,
        debate_dir=debate_dir,
        reports_dir=reports_dir,
        job_description_path=jd_p,
        resume_path=res_p,
        transcript_path=trn_p
    )


def execute_evaluation_pipeline(workspace: RunWorkspace) -> None:
    """Execute complete 5-phase evaluation pipeline in background, updating status per phase."""
    try:
        # Phase 1: Rosetta Profile
        save_status(workspace, status="running", phase="rosetta")
        rosetta = build_candidate_rosetta(
            candidate_id=workspace.candidate_id,
            candidate_name=workspace.candidate_name,
            workspace=workspace
        )

        # Phase 2: Isolated Agent Memos
        save_status(workspace, status="running", phase="agents")
        memos = generate_sealed_memos(
            candidate_id=workspace.candidate_id,
            rosetta=rosetta,
            workspace=workspace
        )

        # Phase 3: Debate Session
        save_status(workspace, status="running", phase="debate")
        transcript = run_debate_session(
            candidate_id=workspace.candidate_id,
            rosetta=rosetta,
            memos=memos,
            workspace=workspace
        )

        # Phase 4: Decision & Override Engine
        save_status(workspace, status="running", phase="decision")
        report_data = synthesize_candidate_decision(
            candidate_id=workspace.candidate_id,
            rosetta=rosetta,
            memos=memos,
            transcript=transcript,
            workspace=workspace
        )

        # Phase 5: Final Report Generation
        save_status(workspace, status="running", phase="report")
        generate_candidate_report_artifacts(
            candidate_id=workspace.candidate_id,
            rosetta=rosetta,
            memos=memos,
            transcript=transcript,
            report_data=report_data,
            workspace=workspace
        )

        # Complete
        save_status(workspace, status="completed", phase="finalized")
        print(f"✓ API Evaluation Run '{workspace.run_id}' completed successfully for {workspace.candidate_name}.")

    except Exception as e:
        err_msg = f"{type(e).__name__}: {str(e)}"
        print(f"✗ Evaluation failed for run '{workspace.run_id}': {err_msg}")
        traceback.print_exc()
        save_status(workspace, status="failed", phase="error", error=err_msg)
