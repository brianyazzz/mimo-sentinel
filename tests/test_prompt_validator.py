import pytest

from mimo_sentinel.models import Hypothesis, IncidentReport, RemediationAction, RiskLevel, Severity
from mimo_sentinel.parser import parse_file
from mimo_sentinel.prompt import build_incident_prompt
from mimo_sentinel.validator import CitationValidationError, validate_citations


def test_prompt_contains_event_ids_and_schema():
    events = parse_file("examples/outage.log")
    messages = build_incident_prompt(events, "checkout-api")

    assert messages[0]["role"] == "system"
    assert "evidence-bound" in messages[0]["content"]
    assert "E0001" in messages[1]["content"]
    assert "hypotheses" in messages[1]["content"]


def test_validator_rejects_unknown_evidence_id():
    events = parse_file("examples/outage.log")
    report = IncidentReport(
        service="checkout-api",
        severity=Severity.high,
        summary="test",
        timeline=[],
        hypotheses=[Hypothesis(title="bad citation", confidence=0.5, evidence_ids=["E9999"])],
        actions=[RemediationAction(title="check", risk=RiskLevel.low, rationale="safe")],
    )

    with pytest.raises(CitationValidationError):
        validate_citations(report, events)
