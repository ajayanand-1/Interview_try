"""Comprehensive Test Suite for FastAPI Backend (Phase 6B)."""

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
    decision_json = resp_decision.json()
    assert decision_json["final_recommendation"] == "hire"
    assert decision_json["decision_path"]["override_motion_filed"] is True

    # 6. Report Summary
    resp_report = client.get(f"/api/evaluations/{run_id}/report")
    assert resp_report.status_code == 200
    rep_json = resp_report.json()
    assert rep_json["has_pdf"] is True

    # 7. PDF Download
    resp_pdf = client.get(f"/api/evaluations/{run_id}/report/pdf")
    assert resp_pdf.status_code == 200
    assert resp_pdf.headers["content-type"] == "application/pdf"
    assert len(resp_pdf.content) > 1000


def test_404_handling_for_nonexistent_run():
    """Verify structured 404 response for invalid run IDs."""
    resp = client.get("/api/evaluations/nonexistent_run_999999/status")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_custom_file_upload_evaluation():
    """Verify POST /api/evaluations accepting multipart file uploads."""
    run_id = "test_api_upload_run"
    dummy_pdf_content = b"%PDF-1.4 dummy pdf content for testing"

    files = {
        "job_description_file": ("custom_jd.pdf", io.BytesIO(dummy_pdf_content), "application/pdf"),
        "resume_file": ("custom_resume.pdf", io.BytesIO(dummy_pdf_content), "application/pdf"),
        "transcript_file": ("custom_transcript.pdf", io.BytesIO(dummy_pdf_content), "application/pdf"),
    }
    data = {
        "candidate_id": "marcus_vance",
        "candidate_name": "Marcus Vance",
        "job_id": "lead_mlops",
        "run_id": run_id
    }

    response = client.post("/api/evaluations", data=data, files=files)
    assert response.status_code == 201
    created = response.json()
    assert created["run_id"] == run_id
    assert created["candidate_id"] == "marcus_vance"
