from __future__ import annotations

from .models import IncidentReport


def render_report(report: IncidentReport) -> str:
    lines = [
        f"Incident Brief: {report.service}",
        f"Severity: {report.severity.value}",
        f"MiMo used: {'yes' if report.mimo_used else 'no, offline fallback'}",
        "",
        report.summary,
        "",
        "Timeline:",
    ]
    lines.extend(f"- {item}" for item in report.timeline or ["No notable events selected."])
    lines.append("")
    lines.append("Hypotheses:")
    for hyp in report.hypotheses:
        evidence = ", ".join(hyp.evidence_ids) or "no direct evidence IDs"
        lines.append(f"- {hyp.title} | confidence={hyp.confidence:.2f} | evidence={evidence}")
    lines.append("")
    lines.append("Recommended Actions:")
    for idx, action in enumerate(report.actions, start=1):
        suffix = f" | hint: {action.command_hint}" if action.command_hint else ""
        lines.append(f"{idx}. [{action.risk.value}] {action.title}{suffix}")
        lines.append(f"   rationale: {action.rationale}")
    return "\n".join(lines)
