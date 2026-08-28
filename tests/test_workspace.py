"""Tests for Phase 6A: Run Isolation and Universal Evaluation Boundary."""

import concurrent.futures
from pathlib import Path
from src.workspace import RunWorkspace
from src.evaluator import evaluate_candidate, EvaluationResult
from src.utils.citations import validate_report_traceability


def test_run_workspace_creation(tmp_path):
    """Test explicit creation of a run workspace with input staging."""
    ws = RunWorkspace.create(
        candidate_id="ananya_iyer",
        job_id="ai_engineer_freight",
        run_id="test_run_001",
        base_runs_dir=tmp_path
    )

    assert ws.run_id == "test_run_001"
    assert ws.candidate_id == "ananya_iyer"
    assert ws.root_dir.exists()
    assert ws.input_dir.exists()
    assert ws.rosetta_dir.exists()
    assert ws.memos_dir.exists()
    assert ws.debate_dir.exists()
    assert ws.reports_dir.exists()
    assert ws.job_description_path.exists()
    assert ws.resume_path.exists()
    assert ws.transcript_path.exists()


def test_two_runs_different_candidates_no_collision(tmp_path):
    """Verify two runs for different candidates do not share files or collide."""
    res_a = evaluate_candidate(
        candidate_id="ananya_iyer",
        run_id="run_ananya_alpha",
        base_runs_dir=tmp_path
    )
    res_b = evaluate_candidate(
        candidate_id="rohan_malhotra",
        run_id="run_rohan_beta",
        base_runs_dir=tmp_path
    )

    assert res_a.workspace.root_dir != res_b.workspace.root_dir
    assert res_a.workspace.root_dir.exists()
    assert res_b.workspace.root_dir.exists()

    # Verify Ananya's files only exist in Run A
    assert res_a.json_path.exists()
    assert not (res_b.workspace.reports_dir / f"{res_a.workspace.candidate_id}_decision.json").exists()

    # Verify Rohan's files only exist in Run B
    assert res_b.json_path.exists()
    assert not (res_a.workspace.reports_dir / f"{res_b.workspace.candidate_id}_decision.json").exists()


def test_two_runs_same_candidate_no_collision(tmp_path):
    """Verify two runs for the SAME candidate do not overwrite or share files."""
    res_1 = evaluate_candidate(
        candidate_id="ananya_iyer",
        run_id="run_ananya_01",
        base_runs_dir=tmp_path
    )
    res_2 = evaluate_candidate(
        candidate_id="ananya_iyer",
        run_id="run_ananya_02",
        base_runs_dir=tmp_path
    )

    assert res_1.workspace.root_dir != res_2.workspace.root_dir
    assert res_1.json_path != res_2.json_path
    assert res_1.json_path.exists()
    assert res_2.json_path.exists()


def test_concurrent_evaluations_thread_safety(tmp_path):
    """Verify concurrent execution cannot overwrite another run's outputs."""
    def run_eval(cid, rid):
        return evaluate_candidate(
            candidate_id=cid,
            run_id=rid,
            base_runs_dir=tmp_path
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(run_eval, "ananya_iyer", "concurrent_run_1")
        f2 = executor.submit(run_eval, "rohan_malhotra", "concurrent_run_2")
        r1 = f1.result()
        r2 = f2.result()

    assert r1.json_path.exists()
    assert r2.json_path.exists()
    assert r1.workspace.root_dir != r2.workspace.root_dir


def test_universal_evaluation_arbitrary_candidate(tmp_path):
    """Test evaluation of an arbitrary, non-demo candidate packet."""
    res = evaluate_candidate(
        candidate_id="alex_chen",
        candidate_name="Alex Chen",
        job_id="platform_lead",
        run_id="run_alex_custom",
        base_runs_dir=tmp_path
    )

    assert isinstance(res, EvaluationResult)
    assert res.rosetta.candidate_name == "Alex Chen"
    assert res.workspace.rosetta_json_path.exists()
    assert res.workspace.rosetta_md_path.exists()
    assert res.workspace.debate_json_path.exists()
    assert res.workspace.report_pdf_path.exists()
    assert res.workspace.report_md_path.exists()

    # Traceability check on arbitrary candidate
    valid_cits = set(res.rosetta.citations_index.keys())
    is_traceable, invalid = validate_report_traceability(res.report_data, valid_cits)
    assert is_traceable, f"Untraceable citations found: {invalid}"


def test_citations_traceability_in_run_workspace(tmp_path):
    """Verify all evidence items in generated report resolve to workspace rosetta index."""
    res = evaluate_candidate(
        candidate_id="ananya_iyer",
        run_id="run_trace_verification",
        base_runs_dir=tmp_path
    )
    
    valid_citations = set(res.rosetta.citations_index.keys())
    is_traceable, invalid_citations = validate_report_traceability(res.report_data, valid_citations)
    
    assert is_traceable is True
    assert len(invalid_citations) == 0
