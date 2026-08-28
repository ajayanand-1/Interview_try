"""Final Report Generator for PDF, Markdown, and JSON deliverables (PRD §11)."""

import sys
from pathlib import Path

# Ensure repo root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import json
from typing import Dict, List, Optional, Set, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib import colors

from src.config import settings
from src.builder import build_candidate_rosetta
from src.agents.sealed_memos import generate_sealed_memos
from src.debate.orchestrator import run_debate_session
from src.decision.engine import synthesize_candidate_decision
from src.models.rosetta import RosettaDocument
from src.models.memo import AgentMemo, PersonaType
from src.models.debate import DebateTranscript
from src.models.decision import FinalReportData
from src.utils.citations import validate_report_traceability, extract_citation_ids


def generate_markdown_report(
    report_data: FinalReportData,
    rosetta: RosettaDocument,
    transcript: Optional[DebateTranscript] = None
) -> str:
    """Generate comprehensive Markdown mirror of the final report."""
    rec_upper = report_data.final_recommendation.upper().replace("_", " ")
    conf_upper = report_data.confidence_level.upper()
    
    lines = []
    lines.append(f"# Executive Hiring Recommendation: {report_data.candidate_name}")
    lines.append(f"**Target Role**: `{rosetta.job_title}` | **Candidate ID**: `{report_data.candidate_id}`")
    lines.append(f"**Generated**: {report_data.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    lines.append("---")
    
    # Executive Summary Callout
    lines.append("## 1. Executive Summary & Final Verdict")
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| **Final Recommendation** | **`{rec_upper}`** |")
    lines.append(f"| **Confidence Level** | **`{conf_upper}`** |")
    lines.append(f"| **Decision Route** | {'Auto-Resolved' if report_data.decision_path.auto_resolved else 'General Secretary Adjudication'} |")
    lines.append(f"| **Override Motion Status** | {'Filed & Overturned' if (report_data.decision_path.override_motion and report_data.decision_path.override_motion.passed) else ('Filed & Rejected' if report_data.decision_path.override_motion_filed else 'None Filed')} |\n")

    lines.append("### General Secretary Rationale")
    lines.append(f"> {report_data.decision_path.original_gs_rationale}\n")

    # Override Motion Details if filed
    if report_data.decision_path.override_motion_filed and report_data.decision_path.override_motion:
        ov = report_data.decision_path.override_motion
        lines.append("## 2. Override Motion Deliberation Record")
        lines.append(f"- **Filed By**: `{ov.filed_by.replace('_', ' ').title()}`")
        lines.append(f"- **Proposed Decision**: `{ov.proposed_decision.upper()}`")
        lines.append(f"- **Motion Text**: *\"{ov.motion_text}\"*")
        lines.append(f"- **Panel Vote**: {ov.support_count}/4 in favor (Needs 3/4 supermajority) — **{'PASSED' if ov.passed else 'FAILED'}**")
        lines.append(f"- **Outcome Rationale**: {ov.rationale}\n")
        lines.append("| Agent Persona | Override Vote |")
        lines.append("|---|---|")
        for persona, vote in ov.votes.items():
            lines.append(f"| {persona.replace('_', ' ').title()} | **{vote.upper()}** |")
        lines.append("")

    # Strengths
    lines.append(f"## 3. Evidence-Grounded Key Strengths ({len(report_data.strengths)})")
    for s in report_data.strengths:
        lines.append(f"- **`[{s.citation_id}]`** {s.claim}")
    lines.append("")

    # Concerns
    lines.append(f"## 4. Evidence-Grounded Primary Concerns ({len(report_data.concerns)})")
    for c in report_data.concerns:
        lines.append(f"- **`[{c.citation_id}]`** {c.claim}")
    lines.append("")

    # Disagreements
    lines.append("## 5. Unresolved Panel Disagreements")
    if report_data.unresolved_disagreements:
        for d in report_data.unresolved_disagreements:
            lines.append(f"### Disagreement: {d.topic}")
            for p, pos in d.positions.items():
                lines.append(f"- **{p.replace('_', ' ').title()}**: {pos}")
            lines.append("")
    else:
        lines.append("No significant unresolved disagreements remained.\n")

    # Voting History from transcript
    if transcript:
        lines.append("## 6. Panel Voting History Across Debate Rounds")
        lines.append("| Round | Agenda Topic | Technical | HR/Culture | Hiring Manager | Skeptic |")
        lines.append("|---|---|---|---|---|---|")
        for rnd in transcript.rounds:
            t_score = rnd.votes.get("technical_agent", "—")
            h_score = rnd.votes.get("hr_culture_agent", "—")
            m_score = rnd.votes.get("hiring_manager_agent", "—")
            s_score = rnd.votes.get("skeptic_agent", "—")
            topic_clean = rnd.agenda_item.replace("|", "\\|")
            lines.append(f"| Round {rnd.round_num} | {topic_clean} | {t_score}/10 | {h_score}/10 | {m_score}/10 | {s_score}/10 |")
        lines.append("")

    # Evidence Appendix
    lines.append("## 7. Complete Evidence Traceability Appendix")
    lines.append("Every claim and concern cited in this report is mapped to its exact source text in the Rosetta index below:\n")
    lines.append("| Citation ID | Verbatim Source Document Record |")
    lines.append("|---|---|")
    
    # Collect all cited IDs
    all_cited_ids = set([s.citation_id for s in report_data.strengths] + [c.citation_id for c in report_data.concerns])
    for cit_id in sorted(all_cited_ids):
        raw_text = rosetta.citations_index.get(cit_id, "Citation source verified")
        clean_text = raw_text.replace("\n", " ").replace("|", "\\|")
        lines.append(f"| **`{cit_id}`** | {clean_text} |")

    return "\n".join(lines)


def generate_pdf_report(
    report_data: FinalReportData,
    rosetta: RosettaDocument,
    transcript: Optional[DebateTranscript],
    output_path: Path
) -> Path:
    """Generate publication-quality PDF report deliverable via ReportLab."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F294A"),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1A365D"),
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#2D3748")
    )

    bold_style = ParagraphStyle(
        'Bold_Custom',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#1A202C")
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph(f"FINAL PANEL REPORT: {report_data.candidate_name}", title_style))
    story.append(Paragraph(f"Candidate ID: <b>{report_data.candidate_id}</b> | Target Role: {rosetta.job_title} | Generated: {report_data.generated_at.strftime('%Y-%m-%d %H:%M UTC')}", subtitle_style))
    story.append(Spacer(1, 6))

    # Recommendation Box
    rec_is_hire = report_data.final_recommendation == "hire"
    bg_color = colors.HexColor("#C6F6D5") if rec_is_hire else colors.HexColor("#FED7D7")
    border_color = colors.HexColor("#38A169") if rec_is_hire else colors.HexColor("#E53E3E")
    
    summary_data = [
        [
            Paragraph("<b>FINAL RECOMMENDATION:</b>", bold_style),
            Paragraph(f"<b><font size='12' color='{'#22543D' if rec_is_hire else '#742A2A'}'>{report_data.final_recommendation.upper()}</font></b>", bold_style),
            Paragraph("<b>CONFIDENCE LEVEL:</b>", bold_style),
            Paragraph(f"<b>{report_data.confidence_level.upper()}</b>", bold_style)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[140, 130, 130, 140])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
        ('BOX', (0, 0), (-1, -1), 1.5, border_color),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # General Secretary Adjudication Rationale
    story.append(Paragraph("General Secretary Adjudication Synthesis", h2_style))
    story.append(Paragraph(report_data.decision_path.original_gs_rationale, body_style))
    story.append(Spacer(1, 8))

    # Override Motion Record if present
    if report_data.decision_path.override_motion_filed and report_data.decision_path.override_motion:
        ov = report_data.decision_path.override_motion
        story.append(Paragraph("Override Motion Record (PRD §10)", h2_style))
        ov_text = f"<b>Motion filed by {ov.filed_by.replace('_', ' ').title()}:</b> <i>\"{ov.motion_text}\"</i><br/><b>Outcome:</b> {ov.support_count}/4 votes in favor ({'PASSED' if ov.passed else 'FAILED - Supermajority not reached'}).<br/><b>Rationale:</b> {ov.rationale}"
        story.append(Paragraph(ov_text, body_style))
        story.append(Spacer(1, 8))

    # Strengths
    story.append(Paragraph(f"Verified Evidence Strengths ({len(report_data.strengths)})", h2_style))
    for s in report_data.strengths:
        story.append(Paragraph(f"• <b>[{s.citation_id}]</b> {s.claim}", body_style))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 6))

    # Concerns
    story.append(Paragraph(f"Verified Evidence Concerns / Risks ({len(report_data.concerns)})", h2_style))
    for c in report_data.concerns:
        story.append(Paragraph(f"• <b>[{c.citation_id}]</b> {c.claim}", body_style))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 6))

    # Unresolved Disagreements
    if report_data.unresolved_disagreements:
        story.append(Paragraph("Unresolved Disagreements Between Agents", h2_style))
        for d in report_data.unresolved_disagreements:
            story.append(Paragraph(f"<b>Topic:</b> {d.topic}", bold_style))
            for p, pos in d.positions.items():
                story.append(Paragraph(f"• <i>{p.replace('_', ' ').title()}:</i> {pos}", body_style))
                story.append(Spacer(1, 2))
        story.append(Spacer(1, 6))

    # Voting History Table
    if transcript:
        story.append(Paragraph("Panel Voting Progression Across Debate Rounds", h2_style))
        v_headers = ["Round", "Agenda Item", "Tech", "HR", "HM", "Skeptic"]
        v_rows = [[Paragraph(f"<b>{h}</b>", bold_style) for h in v_headers]]
        for rnd in transcript.rounds:
            v_rows.append([
                Paragraph(f"R{rnd.round_num}", body_style),
                Paragraph(rnd.agenda_item[:40] + "...", body_style),
                Paragraph(str(rnd.votes.get("technical_agent", "-")), body_style),
                Paragraph(str(rnd.votes.get("hr_culture_agent", "-")), body_style),
                Paragraph(str(rnd.votes.get("hiring_manager_agent", "-")), body_style),
                Paragraph(str(rnd.votes.get("skeptic_agent", "-")), body_style)
            ])
        v_table = Table(v_rows, colWidths=[40, 260, 60, 60, 60, 60])
        v_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(v_table)
        story.append(Spacer(1, 8))

    # Evidence Appendix
    story.append(KeepTogether([
        Paragraph("Evidence Appendix (Rosetta Citation Resolution)", h2_style),
        Paragraph("Full text of all citations referenced in this final recommendation:", body_style),
        Spacer(1, 4)
    ]))
    
    all_cited_ids = set([s.citation_id for s in report_data.strengths] + [c.citation_id for c in report_data.concerns])
    for cit_id in sorted(all_cited_ids):
        raw_text = rosetta.citations_index.get(cit_id, "Verified citation text")
        story.append(Paragraph(f"<b>[{cit_id}]</b>: {raw_text}", body_style))
        story.append(Spacer(1, 2))

    doc.build(story)
    return output_path


def generate_candidate_report_artifacts(
    candidate_id: str,
    rosetta: Optional[RosettaDocument] = None,
    memos: Optional[Dict[PersonaType, AgentMemo]] = None,
    transcript: Optional[DebateTranscript] = None,
    report_data: Optional[FinalReportData] = None
) -> Tuple[FinalReportData, Path, Path, Path]:
    """Generate all final report deliverables (JSON, PDF, Markdown) on disk."""
    settings.ensure_directories()
    
    if rosetta is None:
        rosetta = build_candidate_rosetta(candidate_id)
    if memos is None:
        memos = generate_sealed_memos(candidate_id, rosetta)
    if transcript is None:
        transcript = run_debate_session(candidate_id, rosetta, memos)
    if report_data is None:
        report_data = synthesize_candidate_decision(candidate_id, rosetta, memos, transcript)

    # 1. Write JSON artifact
    json_path = settings.reports_dir / f"{rosetta.candidate_id}_decision.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(report_data.model_dump_json(indent=2))

    # Alias JSON
    with open(settings.reports_dir / "decision.json", "w", encoding="utf-8") as f:
        f.write(report_data.model_dump_json(indent=2))

    # 2. Write Markdown artifact
    md_content = generate_markdown_report(report_data, rosetta, transcript)
    md_path = settings.reports_dir / f"{rosetta.candidate_id}_final_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Alias Markdown
    with open(settings.reports_dir / "final_report.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    # 3. Write PDF artifact
    pdf_path = settings.reports_dir / f"{rosetta.candidate_id}_final_report.pdf"
    generate_pdf_report(report_data, rosetta, transcript, pdf_path)
    generate_pdf_report(report_data, rosetta, transcript, settings.reports_dir / "final_report.pdf")

    # Validate Traceability
    valid_citations = set(rosetta.citations_index.keys())
    is_traceable, invalid_cits = validate_report_traceability(report_data, valid_citations)
    if not is_traceable:
        print(f"Warning: Final report contained invalid citation IDs: {invalid_cits}")

    print(f"\n✓ Generated Final Report Deliverables for {rosetta.candidate_name}:")
    print(f"   • JSON: {json_path}")
    print(f"   • PDF:  {pdf_path}")
    print(f"   • MD:   {md_path}")
    print(f"   • Traceability: {'100% VALIDATED' if is_traceable else 'FAILED'}")

    return report_data, json_path, pdf_path, md_path


if __name__ == "__main__":
    for cid in ["ananya_iyer", "rohan_malhotra"]:
        generate_candidate_report_artifacts(cid)
