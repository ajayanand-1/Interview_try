import os
import pytest
from src.config import settings


@pytest.fixture(autouse=True)
def configure_test_environment(monkeypatch):
    """Ensure fast, deterministic offline execution for the automated test suite."""
    if "TEST_LIVE_LLM" not in os.environ:
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.setattr(settings, "gemini_api_key", None)
