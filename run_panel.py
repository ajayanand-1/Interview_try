#!/usr/bin/env python3
"""
Multi-Agent AI Interview Panel Simulator ("Project Rosetta")
Main Standalone CLI Runner (PRD §13 & Phase 6A Run-Scoped Execution).
"""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Ensure repo root is in sys.path
_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.workspace import RunWorkspace
from src.evaluator import evaluate_candidate, EvaluationResult

console = Console()


def run_pipeline_for_candidate(
    candidate_id: str,
    candidate_name: str = None,
    run_id: str = None,
    job_description_path: str = None,
    resume_path: str = None,
    transcript_path: str = None,
    enable_voice: bool = False,
    dry_run_voice: bool = False
) -> EvaluationResult:
    """Execute complete end-to-end interview panel pipeline inside an isolated run workspace."""
    jd_p = Path(job_description_path) if job_description_path else None
    res_p = Path(resume_path) if resume_path else None
    trn_p = Path(transcript_path) if transcript_path else None

    # 1. Initialize Run Workspace
    workspace = RunWorkspace.create(
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        run_id=run_id,
        job_description_path=jd_p,
        resume_path=res_p,
        transcript_path=trn_p
    )

    console.print(Panel(
        f"[bold cyan]PROJECT ROSETTA: Multi-Agent AI Interview Panel Simulator[/bold cyan]\n"
        f"[yellow]Candidate:[/yellow] [bold]{workspace.candidate_name}[/bold] (`{workspace.candidate_id}`)\n"
        f"[green]Run Workspace:[/green] [dim]{workspace.root_dir}[/dim]",
        box=box.DOUBLE,
        border_style="cyan"
    ))

    # Run universal evaluation pipeline
    result = evaluate_candidate(
        candidate_id=workspace.candidate_id,
        candidate_name=workspace.candidate_name,
        workspace=workspace,
        enable_voice=enable_voice,
        dry_run_voice=dry_run_voice
    )

    # Display Phase 2 Memos Table
    memo_table = Table(title=f"Sealed Agent Memos: {result.rosetta.candidate_name}", box=box.ROUNDED)
    memo_table.add_column("Persona", style="cyan", no_wrap=True)
    memo_table.add_column("Score", justify="center", style="magenta")
    memo_table.add_column("Confidence", justify="center", style="green")
    memo_table.add_column("Strengths", justify="center")
    memo_table.add_column("Gaps", justify="center")
    memo_table.add_column("Run Workspace Artifacts", style="dim")

    for persona, memo in result.memos.items():
        score_str = f"{memo.score}/10" if memo.score is not None else "N/A"
        memo_table.add_row(
            persona.replace("_", " ").title(),
            score_str,
            memo.confidence.upper(),
            str(len(memo.strengths)),
            str(len(memo.gaps)),
            f"runs/{workspace.run_id}/memos/{workspace.candidate_id}_{persona}.[json|pdf]"
        )
    console.print(memo_table)

    # Display Phase 3 Debate Table
    debate_table = Table(title="Debate Progression & Integer Voting", box=box.ROUNDED)
    debate_table.add_column("Round", justify="center", style="bold")
    debate_table.add_column("Agenda Topic", style="yellow")
    debate_table.add_column("Tech", justify="center")
    debate_table.add_column("HR", justify="center")
    debate_table.add_column("HM", justify="center")
    debate_table.add_column("Skeptic", justify="center")

    for rnd in result.transcript.rounds:
        debate_table.add_row(
            f"R{rnd.round_num}",
            rnd.agenda_item,
            f"{rnd.votes.get('technical_agent', '-')}/10",
            f"{rnd.votes.get('hr_culture_agent', '-')}/10",
            f"{rnd.votes.get('hiring_manager_agent', '-')}/10",
            f"{rnd.votes.get('skeptic_agent', '-')}/10"
        )
    console.print(debate_table)

    # Display Phase 4 Final Verdict
    rec = result.report_data.final_recommendation.upper()
    is_hire = rec == "HIRE"
    style = "bold green" if is_hire else "bold red"
    border = "green" if is_hire else "red"

    ov_info = "None Filed"
    if result.report_data.decision_path.override_motion_filed and result.report_data.decision_path.override_motion:
        ov = result.report_data.decision_path.override_motion
        ov_info = f"Filed by {ov.filed_by.replace('_', ' ').title()} ({ov.support_count}/4 in favor -> {'PASSED' if ov.passed else 'FAILED'})"

    summary_text = (
        f"[{style}]FINAL RECOMMENDATION: {rec}[/{style}]  |  Confidence: [bold]{result.report_data.confidence_level.upper()}[/bold]\n\n"
        f"[bold]General Secretary Adjudication:[/bold]\n{result.report_data.decision_path.original_gs_rationale}\n\n"
        f"[bold]Override Motion:[/bold] {ov_info}\n"
        f"[bold]Key Strengths:[/bold] {len(result.report_data.strengths)} verified citations\n"
        f"[bold]Primary Concerns:[/bold] {len(result.report_data.concerns)} verified citations\n\n"
        f"[dim]Run-Scoped Deliverables:[/dim]\n"
        f"  • PDF: [underline]{result.pdf_path}[/underline]\n"
        f"  • MD:  [underline]{result.md_path}[/underline]\n"
        f"  • JSON: [underline]{result.json_path}[/underline]"
    )
    console.print(Panel(summary_text, title=f"Panel Verdict: {result.report_data.candidate_name}", border_style=border, box=box.HEAVY))
    return result


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent AI Interview Panel Simulator (Project Rosetta)")
    parser.add_argument(
        "--candidate",
        type=str,
        default="ananya_iyer",
        help="Candidate ID or slug (default: ananya_iyer)"
    )
    parser.add_argument(
        "--candidate-name",
        type=str,
        default=None,
        help="Optional human-readable candidate name"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Explicit unique run identifier (default: auto-generated timestamp + UUID)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run full evaluation unattended for both standard demo candidates"
    )
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Enable multi-persona TTS voice playback over the debate transcript"
    )
    parser.add_argument(
        "--dry-run-voice",
        action="store_true",
        help="Print voice playback transcript and timing without audio playback"
    )

    args = parser.parse_args()

    if args.all:
        for cid in ["ananya_iyer", "rohan_malhotra"]:
            run_pipeline_for_candidate(
                candidate_id=cid,
                run_id=f"{args.run_id}_{cid}" if args.run_id else None,
                enable_voice=args.voice,
                dry_run_voice=args.dry_run_voice
            )
            console.print("\n" + "="*80 + "\n")
    else:
        run_pipeline_for_candidate(
            candidate_id=args.candidate,
            candidate_name=args.candidate_name,
            run_id=args.run_id,
            enable_voice=args.voice,
            dry_run_voice=args.dry_run_voice
        )


if __name__ == "__main__":
    main()
