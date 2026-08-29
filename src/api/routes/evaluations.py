"""API routes for Evaluation management, batch uploads, candidate and job queries."""

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

router = APIRouter(tags=["Evaluations"])


@router.post("/evaluations", status_code=status.HTTP_201_CREATED)
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
    if not candidate_id or not candidate_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate ID cannot be empty."
        )

    try:
        workspace = RunWorkspace.create(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            job_id=job_id or "default_job",
            run_id=run_id
        )

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

        initial_status = save_status(workspace, status="queued", phase="ingestion")
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


@router.get("/evaluations", response_model=List[Dict[str, Any]])
async def list_evaluations():
    """List all known evaluation runs and their current states."""
    return list_all_evaluations()


@router.get("/evaluations/{run_id}")
async def get_evaluation_metadata(run_id: str):
    """Get metadata and current status for a specific evaluation run."""
    st = load_status(run_id)
    if not st:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation run '{run_id}' not found."
        )
    return st


@router.get("/evaluations/{run_id}/status")
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


@router.get("/evaluations/{run_id}/rosetta")
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


@router.get("/evaluations/{run_id}/memos")
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


@router.get("/evaluations/{run_id}/debate")
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


@router.get("/evaluations/{run_id}/decision")
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


@router.get("/evaluations/{run_id}/feedback")
async def get_evaluation_feedback(run_id: str):
    """Get the multi-persona candidate feedback and growth playbook for a run."""
    ws = get_workspace_for_run(run_id)
    if not ws or not ws.decision_json_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback data for run '{run_id}' is not available yet."
        )
    with open(ws.decision_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("feedback") or {
        "overall_summary": "Evaluation feedback pending.",
        "resume_improvements": [],
        "required_skills": [],
        "company_expectations": [],
        "persona_feedback": []
    }


@router.get("/evaluations/{run_id}/report")
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

    has_pdf = ws.report_pdf_path.exists() or (ws.reports_dir.exists() and len(list(ws.reports_dir.glob("*.pdf"))) > 0)
    has_md = ws.report_md_path.exists() or (ws.reports_dir.exists() and len(list(ws.reports_dir.glob("*.md"))) > 0)

    return {
        "run_id": run_id,
        "candidate_id": ws.candidate_id,
        "candidate_name": ws.candidate_name,
        "decision": decision_data,
        "pdf_download_url": f"/api/evaluations/{run_id}/report/pdf",
        "has_pdf": has_pdf,
        "has_markdown": has_md
    }


@router.get("/evaluations/{run_id}/report/pdf")
async def download_evaluation_pdf(run_id: str):
    """Download the final publication-quality PDF report."""
    ws = get_workspace_for_run(run_id)
    if ws and ws.report_pdf_path.exists():
        return FileResponse(
            path=str(ws.report_pdf_path),
            media_type="application/pdf",
            filename=f"{ws.candidate_id}_final_report.pdf"
        )
    
    if ws and ws.reports_dir.exists():
        pdfs = list(ws.reports_dir.glob("*.pdf"))
        if pdfs:
            return FileResponse(
                path=str(pdfs[0]),
                media_type="application/pdf",
                filename=pdfs[0].name
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"PDF report for run '{run_id}' does not exist."
    )


# --- CANDIDATES & JOBS DIRECTORY API ---

@router.get("/candidates")
async def get_candidates_directory():
    """Return aggregated candidate directory with historical evaluation runs."""
    evals = list_all_evaluations()
    candidates: Dict[str, Dict[str, Any]] = {}

    for e in evals:
        cid = e["candidate_id"]
        if cid not in candidates:
            candidates[cid] = {
                "candidate_id": cid,
                "candidate_name": e["candidate_name"],
                "evaluations_count": 1,
                "latest_status": e["status"],
                "latest_run_id": e["run_id"],
                "latest_job_id": e["job_id"],
                "latest_date": e["created_at"],
                "runs": [e]
            }
        else:
            candidates[cid]["evaluations_count"] += 1
            candidates[cid]["runs"].append(e)

    return list(candidates.values())


@router.get("/jobs")
async def get_jobs_directory():
    """Return aggregated job roles directory."""
    evals = list_all_evaluations()
    jobs: Dict[str, Dict[str, Any]] = {}

    for e in evals:
        jid = e["job_id"]
        if jid not in jobs:
            jobs[jid] = {
                "job_id": jid,
                "job_title": jid.replace("_", " ").title(),
                "evaluations_count": 1,
                "candidates": [e["candidate_name"]],
                "runs": [e]
            }
        else:
            jobs[jid]["evaluations_count"] += 1
            if e["candidate_name"] not in jobs[jid]["candidates"]:
                jobs[jid]["candidates"].append(e["candidate_name"])
            jobs[jid]["runs"].append(e)

    return list(jobs.values())


@router.get("/jobs/{job_id}/candidates")
async def get_job_candidates_comparison(job_id: str):
    """Return candidate runs for a specific job with comparison metrics for the Hiring Room."""
    evals = list_all_evaluations()
    job_runs = [e for e in evals if e["job_id"] == job_id]
    
    comparisons = []
    for r in job_runs:
        run_id = r["run_id"]
        ws = get_workspace_for_run(run_id)
        decision_data = None
        memos_data = {}
        if ws and ws.decision_json_path.exists():
            try:
                with open(ws.decision_json_path, "r", encoding="utf-8") as f:
                    decision_data = json.load(f)
            except Exception:
                pass

        if ws and ws.memos_dir.exists():
            for p in PERSONAS:
                p_path = ws.memo_json_path(p)
                if p_path.exists():
                    try:
                        with open(p_path, "r", encoding="utf-8") as f:
                            memos_data[p] = json.load(f)
                    except Exception:
                        pass

        comparisons.append({
            "run_id": run_id,
            "candidate_id": r["candidate_id"],
            "candidate_name": r["candidate_name"],
            "status": r["status"],
            "phase": r["phase"],
            "created_at": r["created_at"],
            "recommendation": decision_data.get("final_recommendation") if decision_data else None,
            "confidence": decision_data.get("confidence_level") if decision_data else None,
            "strengths_count": len(decision_data.get("strengths", [])) if decision_data else 0,
            "concerns_count": len(decision_data.get("concerns", [])) if decision_data else 0,
            "scores": {p: memos_data[p].get("score") for p in memos_data if "score" in memos_data[p]}
        })

    return {
        "job_id": job_id,
        "job_title": job_id.replace("_", " ").title(),
        "total_candidates": len(comparisons),
        "candidates": comparisons
    }
