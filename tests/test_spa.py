"""Tests for unified SPA serving and non-API route handling in FastAPI."""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_root_serves_spa_html():
    """Verify GET / returns the compiled React SPA HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert '<div id="root">' in response.text


def test_spa_route_evaluations_serves_html():
    """Verify GET /evaluations returns the SPA HTML instead of 404."""
    response = client.get("/evaluations")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert '<div id="root">' in response.text


def test_spa_route_evaluations_new_serves_html():
    """Verify GET /evaluations/new returns the SPA HTML."""
    response = client.get("/evaluations/new")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert '<div id="root">' in response.text


def test_spa_route_detail_serves_html():
    """Verify GET /evaluations/:run_id returns the SPA HTML for client-side routing."""
    response = client.get("/evaluations/run_test_spa_deep_link_123")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert '<div id="root">' in response.text


def test_spa_route_candidates_and_jobs_serve_html():
    """Verify GET /candidates and /jobs return the SPA HTML."""
    for path in ["/candidates", "/jobs", "/reports"]:
        res = client.get(path)
        assert res.status_code == 200
        assert "text/html" in res.headers.get("content-type", "")
        assert '<div id="root">' in res.text


def test_api_route_not_found_returns_json_404():
    """Verify unknown /api/* routes return JSON 404 (not HTML SPA)."""
    response = client.get("/api/unknown_endpoint_xyz")
    assert response.status_code == 404
    assert "application/json" in response.headers.get("content-type", "")
    assert "detail" in response.json()


def test_api_docs_and_openapi_still_work():
    """Verify /docs and /openapi.json are accessible."""
    docs_resp = client.get("/docs")
    assert docs_resp.status_code == 200
    assert "text/html" in docs_resp.headers.get("content-type", "")

    openapi_resp = client.get("/openapi.json")
    assert openapi_resp.status_code == 200
    assert "application/json" in openapi_resp.headers.get("content-type", "")
