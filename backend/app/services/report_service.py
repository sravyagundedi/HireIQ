from pathlib import Path
from xml.sax.saxutils import escape
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

REPORT_DIR = Path(__file__).resolve().parents[2] / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _radar(values: list[float], labels: list[str], output: Path):
    values = values or [0]
    labels = labels or ["Overall"]
    n = len(values)
    angles = [2 * math.pi * i / n for i in range(n)] + [0]
    vals = values + values[:1]

    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111, polar=True)
    ax.plot(angles, vals)
    ax.fill(angles, vals, alpha=0.15)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 10)
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def generate_report(interview, candidate, responses) -> Path:
    filename = f"candidate_{candidate.id}_interview_{interview.id}.pdf"
    pdf_path = REPORT_DIR / filename
    chart_path = REPORT_DIR / f"chart_{interview.id}.png"

    criteria_totals = {}
    criteria_counts = {}
    for r in responses:
        if not r.evaluation:
            continue
        for key, value in (r.evaluation.criteria_scores or {}).items():
            criteria_totals[key] = criteria_totals.get(key, 0) + float(value)
            criteria_counts[key] = criteria_counts.get(key, 0) + 1

    labels = list(criteria_totals.keys()) or ["Overall"]
    values = [
        criteria_totals[k] / criteria_counts[k] if criteria_counts[k] else 0
        for k in labels
    ]
    _radar(values, labels, chart_path)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=36, leftMargin=36)
    story = [
        Paragraph("HireIQ — Candidate Evaluation Report", styles["Title"]),
        Spacer(1, 10),
        Paragraph(f"<b>Candidate:</b> {candidate.name}", styles["Normal"]),
        Paragraph(f"<b>Email:</b> {candidate.email}", styles["Normal"]),
        Paragraph(f"<b>Interview:</b> {interview.title}", styles["Normal"]),
        Paragraph(f"<b>Overall score:</b> {interview.overall_score or 0:.2f}/10", styles["Normal"]),
        Paragraph(f"<b>Recommendation:</b> {interview.recommendation or 'Hold'}", styles["Normal"]),
        Spacer(1, 12),
        Image(str(chart_path), width=4.8*inch, height=4.8*inch),
        Spacer(1, 12),
    ]

    for index, response in enumerate(responses, start=1):
        evaluation = response.evaluation
        score = evaluation.score if evaluation else 0
        story.append(Paragraph(f"Question {index}: {response.question.text}", styles["Heading2"]))
        story.append(Paragraph(f"<b>Score:</b> {score:.2f}/10", styles["Normal"]))
        story.append(Paragraph("<b>Transcript:</b>", styles["Normal"]))
        story.append(Paragraph(escape(response.transcript or "No transcript"), styles["BodyText"]))
        if evaluation:
            story.append(Paragraph(f"<b>Strengths:</b> {', '.join(evaluation.strengths or [])}", styles["BodyText"]))
            story.append(Paragraph(f"<b>Weaknesses:</b> {', '.join(evaluation.weaknesses or [])}", styles["BodyText"]))
            story.append(Paragraph(f"<b>Sentiment:</b> {evaluation.sentiment}", styles["BodyText"]))
            story.append(Paragraph(f"<b>Confidence signal:</b> {evaluation.confidence:.2f}/100", styles["BodyText"]))
        story.append(Spacer(1, 10))

    doc.build(story)
    return pdf_path
