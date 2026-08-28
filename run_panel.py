#!/usr/bin/env python3
"""
Multi-Agent AI Interview Panel Simulator ("Project Rosetta")
Main Standalone CLI Runner (PRD §13).
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

from src.config import settings
from src.builder import build_candidate_rosetta
from src.agents.sealed_memos import generate_sealed_memos
from src.debate.orchestrator import run_debate_session
from src.debate.voice import playback_debate_audio
from src.decision.engine import synthesize_candidate_decision
from src.decision.reporter import generate_candidate_report_artifacts

console = Console()


def run_pipeline_for_candidate(candidate_id: str, enable_voice: bool = False, dry_run_voice: bool = False):
    """Execute complete end-to-end interview panel pipeline for one candidate."""
    console.print(Panel(
        f"[bold cyan]PROJECT ROSETTA: Multi-Agent AI Interview Panel Simulator[/bold cyan]\n"
        f"[yellow]Evaluating Candidate Packet: {candidate_id}[/yellow]",
        box=box.DOUBLE,
        border_style="cyan"
    ))

    # Phase 1: Candidate Profile Builder -> Rosetta Document
    console.print("\n[bold blue]=== Phase 1: Candidate Profile Builder ===[/bold blue]")
    with console.status("[bold green]Parsing PDFs into evidence-indexed Rosetta document..."):
        rosetta = build_candidate_rosetta(candidate_id)
    console.print(f"[green]✓ Rosetta Document created:[/green] {len(rosetta.citations_index)} citations indexed")
    console.print(f"  • JSON: [dim]{settings.rosetta_dir / f'{rosetta.candidate_id}.json'}[/dim]")
    console.print(f"  • MD:   [dim]{settings.rosetta_dir / f'{rosetta.candidate_id}.md'}[/dim]")

    # Phase 2: Four Independent Personas (Sealed Memos)
    console.print("\n[bold blue]=== Phase 2: Isolated Agent Reasoning & Sealed Memos ===[/bold blue]")
    with console.status("[bold green]Running 4 isolated, code-enforced agent sessions..."):
        memos = generate_sealed_memos(candidate_id, rosetta)

    memo_table = Table(title=f"Sealed Agent Memos: {rosetta.candidate_name}", box=box.ROUNDED)
    memo_table.add_column("Persona", style="cyan", no_wrap=True)
    memo_table.add_column("Score", justify="center", style="magenta")
    memo_table.add_column("Confidence", justify="center", style="green")
    memo_table.add_column("Strengths", justify="center")
    memo_table.add_column("Gaps", justify="center")
    memo_table.add_column("Sealed JSON + PDF Artifacts", style="dim")

    for persona, memo in memos.items():
        score_str = f"{memo.score}/10" if memo.score is not None else "N/A"
        memo_table.add_row(
            persona.replace("_", " ").title(),
            score_str,
            memo.confidence.upper(),
            str(len(memo.strengths)),
            str(len(memo.gaps)),
            f"memos/{candidate_id}_{persona}.[json|pdf]"
        )
    console.print(memo_table)

    # Phase 3: Debate Orchestrator & General Secretary
    console.print("\n[bold blue]=== Phase 3: Agenda-Driven Debate & Voting ===[/bold blue]")
    with console.status("[bold green]General Secretary unsealing memos & chairing debate..."):
        transcript = run_debate_session(candidate_id, rosetta, memos)

    debate_table = Table(title="Debate Progression & Integer Voting", box=box.ROUNDED)
    debate_table.add_column("Round", justify="center", style="bold")
    debate_table.add_column("Agenda Topic", style="yellow")
    debate_table.add_column("Tech", justify="center")
    debate_table.add_column("HR", justify="center")
    debate_table.add_column("HM", justify="center")
    debate_table.add_column("Skeptic", justify="center")

    for rnd in transcript.rounds:
        debate_table.add_row(
            f"R{rnd.round_num}",
            rnd.agenda_item,
            f"{rnd.votes.get('technical_agent', '-')}/10",
            f"{rnd.votes.get('hr_culture_agent', '-')}/10",
            f"{rnd.votes.get('hiring_manager_agent', '-')}/10",
            f"{rnd.votes.get('skeptic_agent', '-')}/10"
        )
    console.print(debate_table)
    console.print(f"[green]✓ Debate transcript logged:[/green] [dim]{settings.debate_dir / f'{rosetta.candidate_id}_transcript.json'}[/dim]")

    # Phase 6 Stretch: Voice Playback if enabled
    if enable_voice or dry_run_voice:
        console.print("\n[bold blue]=== Phase 6 Stretch: Multi-Persona Voice Debate Playback ===[/bold blue]")
        playback_debate_audio(transcript, dry_run=dry_run_voice)

    # Phase 4: Decision & Final Report Generator
    console.print("\n[bold blue]=== Phase 4: Adjudication, Overrides & Final Report ===[/bold blue]")
    with console.status("[bold green]Synthesizing decision & compiling PDF/Markdown reports..."):
        report_data, json_p, pdf_p, md_p = generate_candidate_report_artifacts(
            candidate_id, rosetta, memos, transcript
        )

    # Outcome Summary Panel
    rec = report_data.final_recommendation.upper()
    is_hire = rec == "HIRE"
    style = "bold green" if is_hire else "bold red"
    border = "green" if is_hire else "red"

    ov_info = "None Filed"
    if report_data.decision_path.override_motion_filed and report_data.decision_path.override_motion:
        ov = report_data.decision_path.override_motion
        ov_info = f"Filed by {ov.filed_by.replace('_', ' ').title()} ({ov.support_count}/4 in favor -> {'PASSED' if ov.passed else 'FAILED'})"

    summary_text = (
        f"[{style}]FINAL RECOMMENDATION: {rec}[/{style}]  |  Confidence: [bold]{report_data.confidence_level.upper()}[/bold]\n\n"
        f"[bold]General Secretary Adjudication:[/bold]\n{report_data.decision_path.original_gs_rationale}\n\n"
        f"[bold]Override Motion:[/bold] {ov_info}\n"
        f"[bold]Key Strengths:[/bold] {len(report_data.strengths)} verified citations\n"
        f"[bold]Primary Concerns:[/bold] {len(report_data.concerns)} verified citations\n\n"
        f"[dim]Deliverables Saved to Disk:[/dim]\n"
        f"  • PDF: [underline]{pdf_p}[/underline]\n"
        f"  • MD:  [underline]{md_p}[/underline]\n"
        f"  • JSON: [underline]{json_p}[/underline]"
    )
    console.print(Panel(summary_text, title=f"Panel Verdict: {report_data.candidate_name}", border_style=border, box=box.HEAVY))


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent AI Interview Panel Simulator")
    parser.add_argument(
        "--candidate",
        type=str,
        default="ananya_iyer",
        choices=["ananya_iyer", "rohan_malhotra", "ananya", "rohan"],
        help="Candidate packet to evaluate (default: ananya_iyer)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run full evaluation unattended for both candidates"
    )
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Enable multi-persona TTS voice playback over the debate transcript (Phase 6 Stretch)"
    )
    parser.add_argument(
        "--dry-run-voice",
        action="store_true",
        help="Print voice playback transcript and timing without audio playback"
    )

    args = parser.parse_args()

    if args.all:
        for cid in ["ananya_iyer", "rohan_malhotra"]:
            run_pipeline_for_candidate(cid, enable_voice=args.voice, dry_run_voice=args.dry_run_voice)
            console.print("\n" + "="*80 + "\n")
    else:
        run_pipeline_for_candidate(args.candidate, enable_voice=args.voice, dry_run_voice=args.dry_run_voice)


if __name__ == "__main__":
    main()
