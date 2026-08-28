"""Run-scoped Workspace Abstraction to eliminate output collisions (Phase 6A)."""

import shutil
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from src.config import settings


def sanitize_path_string(name: str) -> str:
    """Sanitize string to be safe for directory and file names."""
    clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', name.strip())
    return clean.lower()


@dataclass
class RunWorkspace:
    run_id: str
    candidate_id: str
    candidate_name: str
    job_id: str
    root_dir: Path
    input_dir: Path
    rosetta_dir: Path
    memos_dir: Path
    debate_dir: Path
    reports_dir: Path
    
    # Input file locations
    job_description_path: Path
    resume_path: Path
    transcript_path: Path

    @classmethod
    def create(
        cls,
        candidate_id: str,
        candidate_name: Optional[str] = None,
        job_id: str = "default_job",
        run_id: Optional[str] = None,
        base_runs_dir: Optional[Path] = None,
        job_description_path: Optional[Path] = None,
        resume_path: Optional[Path] = None,
        transcript_path: Optional[Path] = None,
    ) -> "RunWorkspace":
        """Initialize a new, isolated run workspace on disk with staged inputs."""
        clean_cid = sanitize_path_string(candidate_id)
        c_name = candidate_name or clean_cid.replace("_", " ").title()
        
        # Generate collision-resistant run_id if not provided
        if not run_id:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            short_uid = uuid.uuid4().hex[:6]
            run_id = f"run_{timestamp}_{clean_cid}_{short_uid}"
        else:
            run_id = sanitize_path_string(run_id)

        runs_root = base_runs_dir or settings.runs_dir
        root_dir = runs_root / run_id
        
        input_dir = root_dir / "input"
        rosetta_dir = root_dir / "rosetta"
        memos_dir = root_dir / "memos"
        debate_dir = root_dir / "debate"
        reports_dir = root_dir / "reports"

        # Create directories
        for d in [input_dir, rosetta_dir, memos_dir, debate_dir, reports_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # Stage Job Description
        target_jd_path = input_dir / "job_description.pdf"
        src_jd = job_description_path or (settings.data_dir / "job_description.pdf")
        if src_jd.exists():
            shutil.copy2(src_jd, target_jd_path)
        else:
            target_jd_path = src_jd

        # Stage Resume
        target_resume_path = input_dir / "resume.pdf"
        src_resume = resume_path or (settings.data_dir / f"{clean_cid}_resume.pdf")
        if src_resume.exists():
            shutil.copy2(src_resume, target_resume_path)
        else:
            target_resume_path = src_resume

        # Stage Transcript
        target_transcript_path = input_dir / "transcript.pdf"
        src_transcript = transcript_path or (settings.data_dir / f"{clean_cid}_transcript.pdf")
        if src_transcript.exists():
            shutil.copy2(src_transcript, target_transcript_path)
        else:
            target_transcript_path = src_transcript

        return cls(
            run_id=run_id,
            candidate_id=clean_cid,
            candidate_name=c_name,
            job_id=job_id,
            root_dir=root_dir,
            input_dir=input_dir,
            rosetta_dir=rosetta_dir,
            memos_dir=memos_dir,
            debate_dir=debate_dir,
            reports_dir=reports_dir,
            job_description_path=target_jd_path,
            resume_path=target_resume_path,
            transcript_path=target_transcript_path
        )

    # Path helper methods
    @property
    def rosetta_json_path(self) -> Path:
        return self.rosetta_dir / f"{self.candidate_id}.json"

    @property
    def rosetta_md_path(self) -> Path:
        return self.rosetta_dir / f"{self.candidate_id}.md"

    def memo_json_path(self, persona: str) -> Path:
        return self.memos_dir / f"{self.candidate_id}_{persona}.json"

    def memo_pdf_path(self, persona: str) -> Path:
        return self.memos_dir / f"{self.candidate_id}_{persona}.pdf"

    @property
    def debate_json_path(self) -> Path:
        return self.debate_dir / f"{self.candidate_id}_transcript.json"

    @property
    def debate_md_path(self) -> Path:
        return self.debate_dir / f"{self.candidate_id}_transcript.md"

    @property
    def decision_json_path(self) -> Path:
        return self.reports_dir / f"{self.candidate_id}_decision.json"

    @property
    def report_pdf_path(self) -> Path:
        return self.reports_dir / f"{self.candidate_id}_final_report.pdf"

    @property
    def report_md_path(self) -> Path:
        return self.reports_dir / f"{self.candidate_id}_final_report.md"
