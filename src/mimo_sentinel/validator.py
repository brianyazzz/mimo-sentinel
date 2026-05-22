from __future__ import annotations

from .models import Event, IncidentReport


class CitationValidationError(ValueError):
    pass


def validate_citations(report: IncidentReport, events: list[Event]) -> None:
    valid_ids = {event.id for event in events}
    missing: list[str] = []
    for hypothesis in report.hypotheses:
        for evidence_id in hypothesis.evidence_ids:
            if evidence_id not in valid_ids:
                missing.append(evidence_id)
    if missing:
        unique = ", ".join(sorted(set(missing)))
        raise CitationValidationError(f"MiMo report cited unknown event IDs: {unique}")
