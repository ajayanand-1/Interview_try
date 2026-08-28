"""PDF Export utility using ReportLab for memos and final reports."""

from pathlib import Path
from typing import Optional, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from src.models.memo import AgentMemo
from src.models.decision import FinalReportData


def export_memo_to_pdf(memo: AgentMemo, output_path: Path) -> Path:
    """Generate a clean, structured PDF artifact for a sealed persona memo."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output_path), pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=10
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=5
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2D3748")
    )
    
    bold_style = ParagraphStyle(
        'BoldDark',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#1A202C")
    )

    story = []
    persona_title = memo.persona.replace("_", " ").title()
    story.append(Paragraph(f"SEALED MEMO: {persona_title}", title_style))
    story.append(Paragraph(f"Candidate: <b>{memo.candidate_id}</b> | Created: {memo.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}", body_style))
    story.append(Spacer(1, 10))

    # Meta table
    score_display = str(memo.score) if memo.score is not None else "N/A (Insufficient Evidence)"
    meta_data = [
        [Paragraph("Score (1-10)", bold_style), Paragraph(score_display, body_style)],
        [Paragraph("Confidence", bold_style), Paragraph(memo.confidence.upper(), body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[150, 380])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EDF2F7")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # Verdict summary
    story.append(Paragraph("Verdict Summary", section_style))
    story.append(Paragraph(memo.verdict_summary, body_style))
    story.append(Spacer(1, 10))

    # Strengths
    story.append(Paragraph(f"Identified Strengths ({len(memo.strengths)})", section_style))
    if memo.strengths:
        for s in memo.strengths:
            story.append(Paragraph(f"• <b>[{s.citation_id}]</b> {s.claim}", body_style))
            story.append(Spacer(1, 3))
    else:
        story.append(Paragraph("None noted.", body_style))
    story.append(Spacer(1, 10))

    # Gaps
    story.append(Paragraph(f"Identified Gaps / Concerns ({len(memo.gaps)})", section_style))
    if memo.gaps:
        for g in memo.gaps:
            story.append(Paragraph(f"• <b>[{g.citation_id}]</b> {g.claim}", body_style))
            story.append(Spacer(1, 3))
    else:
        story.append(Paragraph("None noted.", body_style))
    story.append(Spacer(1, 10))

    # Contrarian / Devil's advocate if present
    if memo.contrarian_argument:
        story.append(Paragraph("Contrarian / Devil's Advocate Argument", section_style))
        story.append(Paragraph(memo.contrarian_argument, body_style))
        story.append(Spacer(1, 10))

    # Insufficient evidence
    if memo.insufficient_evidence_items:
        story.append(Paragraph("Insufficient Evidence Items", section_style))
        for item in memo.insufficient_evidence_items:
            story.append(Paragraph(f"• {item}", body_style))
            story.append(Spacer(1, 3))

    doc.build(story)
    return output_path
