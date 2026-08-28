"""API routes for Evaluation management and inspection (Phase 6B)."""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse

from src.workspace import RunWorkspace
from src.agents.sealed_memos import PERSONAS
from src.api.services.evaluation_service import (
    save_status,
    load_status,
    list_all_evaluations,
    get_workspace_for_run,
    execute_evaluation_pipeline,
)

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    background_tasks: BackgroundTasks,
    candidate_id: str = Form(...),
    candidate_name: Optional[str] = Form(None),
    job_id: Optional[str] = Form("default_job"),
    run_id: Optional[str] = Form(None),
    job_description_file: Optional[UploadFile] = File(None),
    resume_file: Optional[UploadFile] = File(None),
    transcript_file: Optional[UploadFile] = File(None),
):
    """Create a new isolated evaluation run with optional file uploads and trigger background execution."""
    try:
        # Create run-scoped workspace
        workspace = RunWorkspace.create(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            job_id=job_id or "default_job",
            run_id=run_id
        )

        # Handle uploaded custom files if provided
        if job_description_file and job_description_file.filename:
            target_jd = workspace.input_dir / "job_description.pdf"
            with open(target_jd, "wb") as f:
                shutil.copyfileobj(job_description_file.file, f)
            workspace.job_description_path = target_jd

        if resume_file and resume_file.filename:
            target_res = workspace.input_dir / "resume.pdf"
            with open(target_res, "wb") as f:
                shutil.copyfileobj(resume_file.file, f)
            workspace.resume_path = target_res

        if transcript_file and transcript_file.filename:
            target_trn = workspace.input_dir / "transcript.pdf"
            with open(target_trn, "wb") as f:
                shutil.copyfileobj(transcript_file.file, f)
            workspace.transcript_path = target_trn

        # Persist initial status
        initial_status = save_status(workspace, status="queued", phase="ingestion")

        # Dispatch background pipeline execution
        background_tasks.add_task(execute_evaluation_pipeline, workspace)

        return {
            "run_id": workspace.run_id,
            "candidate_id": workspace.candidate_id,
            "candidate_name": workspace.candidate_name,
            "job_id": workspace.job_id,
            "status": "queued",
            "phase": "ingestion",
            "workspace_dir": str(workspace.root_dir),
            "created_at": initial_status["created_at"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create evaluation run: {str(e)}"
        )


@router.get("", response_model=List[Dict[str, Any]])
async def list_evaluations():
    """List all known evaluation runs and their current states."""
    return list_all_evaluations()


@router.get("/{run_id}")
async def get_evaluation_metadata(run_id: str):
    """Get metadata and current status for a specific evaluation run."""
    st = load_status(run_id)
    if not st:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation run '{run_id}' not found."
        )
    return st


@router.get("/{run_id}/status")
async def get_evaluation_status(run_id: str):
    """Get current lifecycle status and phase for an evaluation run."""
    st = load_status(run_id)
    if not st:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation run '{run_id}' not found."
        )
    return {
        "run_id": st.get("run_id"),
        "status": st.get("status"),
        "phase": st.get("phase"),
        "error": st.get("error"),
        "updated_at": st.get("updated_at")
    }


@router.get("/{run_id}/rosetta")
async def get_evaluation_rosetta(run_id: str):
    """Get the Rosetta candidate document JSON for a run."""
    ws = get_workspace_for_run(run_id)
    if not ws or not ws.rosetta_json_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rosetta document for run '{run_id}' is not available yet."
        )
    with open(ws.rosetta_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/{run_id}/memos")
async def get_evaluation_memos(run_id: str):
    """Get the 4 sealed agent memos for a run."""
    ws = get_workspace_for_run(run_id)
    if not ws or not ws.memos_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memos for run '{run_id}' are not available yet."
        )

    memos_dict = {}
    for persona in PERSONAS:
        memo_path = ws.memo_json_path(persona)
        if memo_path.exists():
            with open(memo_path, "r", encoding="utf-8") as f:
                memos_dict[persona] = json.load(f)

    if not memos_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memos for run '{run_id}' have not been generated yet."
        )

    return memos_dict


@router.get("/{run_id}/debate")
async def get_evaluation_debate(run_id: str):
    """Get the debate transcript and voting rounds for a run."""
    ws = get_workspace_for_run(run_id)
    if not ws or not ws.debate_json_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Debate transcript for run '{run_id}' is not available yet."
        )
    with open(ws.debate_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/{run_id}/decision")
async def get_evaluation_decision(run_id: str):
    """Get the final decision synthesis and override motion for a run."""
    ws = get_workspace_for_run(run_id)
    if not ws or not ws.decision_json_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision data for run '{run_id}' is not available yet."
        )
    with open(ws.decision_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/{run_id}/report")
async def get_evaluation_report(run_id: str):
    """Get summary report metadata and deliverable file paths for a run."""
    ws = get_workspace_for_run(run_id)
    if not ws or not ws.decision_json_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report deliverables for run '{run_id}' are not ready yet."
        )

    with open(ws.decision_json_path, "r", encoding="utf-8") as f:
        decision_data = json.load(f)

    return {
        "run_id": run_id,
        "candidate_id": ws.candidate_id,
        "candidate_name": ws.candidate_name,
        "decision": decision_data,
        "pdf_download_url": f"/api/evaluations/{run_id}/report/pdf",
        "has_pdf": ws.report_pdf_path.exists(),
        "has_markdown": ws.report_md_path.exists()
    }


@router.get("/{run_id}/report/pdf")
async def download_evaluation_pdf(run_id: str):
    """Download the final publication-quality PDF report."""
    ws = get_workspace_for_run(run_id)
    if not ws or not ws.report_pdf_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PDF report for run '{run_id}' does not exist."
        )

    return FileResponse(
        path=str(ws.report_pdf_path),
        media_type="application/pdf",
        filename=f"{ws.candidate_id}_final_report.pdf"
    )
