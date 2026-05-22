from mimo_sentinel.analyzer import analyze_events
from mimo_sentinel.parser import parse_file


def test_analyzer_detects_deploy_and_database_pressure():
    events = parse_file("examples/outage.log")
    report = analyze_events(events, service="checkout-api")

    assert report.severity.value in {"medium", "high", "critical"}
    assert any("deployment" in hyp.title.lower() for hyp in report.hypotheses)
    assert any("database" in hyp.title.lower() for hyp in report.hypotheses)
    assert any(action.risk.value == "high" for action in report.actions)
