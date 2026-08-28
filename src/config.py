"""Configuration settings for the Multi-Agent Interview Panel Simulator."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseSettings):
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Directory paths
    base_dir: Path = BASE_DIR
    data_dir: Path = BASE_DIR / "data"
    rosetta_dir: Path = BASE_DIR / "rosetta"
    memos_dir: Path = BASE_DIR / "memos"
    debate_dir: Path = BASE_DIR / "debate"
    reports_dir: Path = BASE_DIR / "reports"

    def ensure_directories(self) -> None:
        """Ensure all required artifact directories exist on disk."""
        for d in [self.data_dir, self.rosetta_dir, self.memos_dir, self.debate_dir, self.reports_dir]:
            d.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()
