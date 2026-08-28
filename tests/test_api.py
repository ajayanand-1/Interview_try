"""Comprehensive Test Suite for FastAPI Backend (Phase 6B, B, K, L, M, O)."""

import io
from pathlib import Path
from fastapi.testclient import TestClient

from src.api.main import app
from src.evaluator import evaluate_candidate
from src.workspace import RunWorkspace

client = TestClient(app)


def test_api_health():
    """Verify health check endpoint returns 200 OK and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "project-rosetta-api"


def test_create_evaluation_and_status_cycle(tmp_path):
    """Test POST /api/evaluations creation and subsequent status inspection."""
    run_id = "test_api_cycle_001"
    response = client.post(
        "/api/evaluations",
        data={
            "candidate_id": "ananya_iyer",
            "candidate_name": "Ananya Iyer",
            "job_id": "ai_engineer_cargonet",
            "run_id": run_id
        }
    )
    assert response.status_code == 201
    created = response.json()
    assert created["run_id"] == run_id
    assert created["candidate_id"] == "ananya_iyer"
    assert created["status"] in ["queued", "running", "completed"]

    # Verify status endpoint
    status_resp = client.get(f"/api/evaluations/{run_id}/status")
    assert status_resp.status_code == 200
    st = status_resp.json()
    assert st["run_id"] == run_id
    assert "status" in st
    assert "phase" in st


def test_list_evaluations():
    """Verify GET /api/evaluations returns a list of evaluation runs."""
    response = client.get("/api/evaluations")
    assert response.status_code == 200
    runs = response.json()
    assert isinstance(runs, list)
    assert len(runs) > 0


def test_evaluation_artifact_endpoints(tmp_path):
    """Verify all phase artifact endpoints for a completed evaluation run."""
    run_id = "test_api_artifacts_complete"
    
    # Run evaluation synchronously to guarantee artifacts are ready
    ws = RunWorkspace.create(
        candidate_id="ananya_iyer",
        run_id=run_id
    )
    evaluate_candidate(candidate_id="ananya_iyer", workspace=ws)

    # 1. Metadata
    resp = client.get(f"/api/evaluations/{run_id}")
    assert resp.status_code == 200
    assert resp.json()["candidate_id"] == "ananya_iyer"

    # 2. Rosetta
    resp_rosetta = client.get(f"/api/evaluations/{run_id}/rosetta")
    assert resp_rosetta.status_code == 200
    rosetta_json = resp_rosetta.json()
    assert rosetta_json["candidate_id"] == "ananya_iyer"
    assert "citations_index" in rosetta_json

    # 3. Memos
    resp_memos = client.get(f"/api/evaluations/{run_id}/memos")
    assert resp_memos.status_code == 200
    memos_json = resp_memos.json()
    assert "technical_agent" in memos_json
    assert "hr_culture_agent" in memos_json
    assert "hiring_manager_agent" in memos_json
    assert "skeptic_agent" in memos_json

    # 4. Debate
    resp_debate = client.get(f"/api/evaluations/{run_id}/debate")
    assert resp_debate.status_code == 200
    debate_json = resp_debate.json()
    assert "rounds" in debate_json
    assert len(debate_json["rounds"]) >= 3

    # 5. Decision
    resp_decision = client.get(f"/api/evaluations/{run_id}/decision")
    assert resp_decision.status_code == 200
    dec_json = resp_decision.json()
    assert dec_json["final_recommendation"] in ["hire", "no_hire", "auto_hire", "auto_reject"]
    assert "decision_path" in dec_json

    # 6. Report metadata
    resp_report = client.get(f"/api/evaluations/{run_id}/report")
    assert resp_report.status_code == 200
    rep_json = resp_report.json()
    assert rep_json["run_id"] == run_id
    assert rep_json["has_pdf"] is True

    # 7. Report PDF download
    resp_pdf = client.get(f"/api/evaluations/{run_id}/report/pdf")
    assert resp_pdf.status_code == 200
    assert resp_pdf.headers["content-type"] == "application/pdf"
    assert len(resp_pdf.content) > 1000


def test_404_handling_for_nonexistent_run():
    """Verify 404 responses for non-existent run requests."""
    fake_id = "nonexistent_run_999999"
    assert client.get(f"/api/evaluations/{fake_id}").status_code == 404
    assert client.get(f"/api/evaluations/{fake_id}/status").status_code == 404
    assert client.get(f"/api/evaluations/{fake_id}/rosetta").status_code == 404
    assert client.get(f"/api/evaluations/{fake_id}/memos").status_code == 404
    assert client.get(f"/api/evaluations/{fake_id}/debate").status_code == 404
    assert client.get(f"/api/evaluations/{fake_id}/decision").status_code == 404
    assert client.get(f"/api/evaluations/{fake_id}/report").status_code == 404
    assert client.get(f"/api/evaluations/{fake_id}/report/pdf").status_code == 404


def test_custom_file_upload_evaluation():
    """Verify evaluation creation with custom multipart uploaded files."""
    run_id = "test_api_upload_run"
    fake_jd = io.BytesIO(b"%PDF-1.4 dummy jd content")
    fake_resume = io.BytesIO(b"%PDF-1.4 dummy resume content")
    fake_transcript = io.BytesIO(b"%PDF-1.4 dummy transcript content")

    response = client.post(
        "/api/evaluations",
        data={
            "candidate_id": "uploaded_candidate",
            "candidate_name": "Uploaded Candidate",
            "job_id": "custom_job_pos",
            "run_id": run_id
        },
        files={
            "job_description_file": ("custom_jd.pdf", fake_jd, "application/pdf"),
            "resume_file": ("custom_resume.pdf", fake_resume, "application/pdf"),
            "transcript_file": ("custom_transcript.pdf", fake_transcript, "application/pdf"),
        }
    )
    assert response.status_code == 201
    created = response.json()
    assert created["run_id"] == run_id
    assert created["candidate_id"] == "uploaded_candidate"


def test_candidates_directory_endpoint():
    """Verify GET /api/candidates returns aggregated candidate directory."""
    resp = client.get("/api/candidates")
    assert resp.status_code == 200
    candidates = resp.json()
    assert isinstance(candidates, list)
    assert len(candidates) > 0
    first = candidates[0]
    assert "candidate_id" in first
    assert "candidate_name" in first
    assert "evaluations_count" in first


def test_jobs_directory_endpoint():
    """Verify GET /api/jobs returns aggregated job roles directory."""
    resp = client.get("/api/jobs")
    assert resp.status_code == 200
    jobs = resp.json()
    assert isinstance(jobs, list)
    assert len(jobs) > 0
    first = jobs[0]
    assert "job_id" in first
    assert "job_title" in first
    assert "evaluations_count" in first


def test_job_candidates_comparison_endpoint():
    """Verify GET /api/jobs/{job_id}/candidates returns side-by-side comparison data."""
    resp = client.get("/api/jobs/default_job/candidates")
    assert resp.status_code == 200
    comp = resp.json()
    assert comp["job_id"] == "default_job"
    assert "candidates" in comp
    assert isinstance(comp["candidates"], list)


def test_empty_candidate_id_validation_error():
    """Verify validation error when candidate_id is empty."""
    resp = client.post("/api/evaluations", data={"candidate_id": "   "})
    assert resp.status_code == 400
    assert "Candidate ID cannot be empty" in resp.json()["detail"]
