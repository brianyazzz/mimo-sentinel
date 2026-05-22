from __future__ import annotations

from collections import Counter

from .mimo_client import MiMoClient
from .models import Event, Hypothesis, IncidentReport, Severity
from .risk import action

ERROR_WORDS = ("error", "exception", "timeout", "failed", "5xx", "panic")
DEPLOY_WORDS = ("deploy", "release", "rollout", "image tag", "migration")
DB_WORDS = ("database", "db", "postgres", "mysql", "pool", "connection")


def analyze_events(
    events: list[Event],
    service: str = "unknown",
    use_mimo: bool = False,
    mimo_client: MiMoClient | None = None,
) -> IncidentReport:
    if use_mimo and mimo_client:
        mimo_report = mimo_client.analyze(events, service)
        if mimo_report:
            return mimo_report

    scoped = [event for event in events if service == "unknown" or event.service in {service, "unknown"}]
    target_events = scoped or events
    levels = Counter(event.level for event in target_events)
    services = Counter(event.service for event in events)
    error_events = [event for event in target_events if event.level in {"error", "critical"} or _contains(event, ERROR_WORDS)]
    deploy_events = [event for event in events if _contains(event, DEPLOY_WORDS)]
    db_events = [event for event in target_events if _contains(event, DB_WORDS)]

    severity = _severity(len(error_events), len(target_events))
    timeline = _timeline(deploy_events, error_events, db_events)
    hypotheses = _hypotheses(error_events, deploy_events, db_events)
    actions = _actions(hypotheses, service)

    summary = (
        f"{service} shows {len(error_events)} suspicious events across "
        f"{len(target_events)} parsed records. Top services: {_top(services)}. "
        f"Level mix: {_top(levels)}."
    )
    return IncidentReport(
        service=service,
        severity=severity,
        summary=summary,
        timeline=timeline,
        hypotheses=hypotheses,
        actions=actions,
        mimo_used=False,
    )


def _contains(event: Event, words: tuple[str, ...]) -> bool:
    text = f"{event.level} {event.service} {event.message}".lower()
    return any(word in text for word in words)


def _severity(error_count: int, total: int) -> Severity:
    if error_count >= 20 or (total and error_count / total > 0.35):
        return Severity.critical
    if error_count >= 8:
        return Severity.high
    if error_count >= 2:
        return Severity.medium
    return Severity.low


def _timeline(deploy_events: list[Event], error_events: list[Event], db_events: list[Event]) -> list[str]:
    selected = (deploy_events[:3] + error_events[:5] + db_events[:3])[:10]
    return [f"{event.id} {event.timestamp or '-'} {event.service}: {event.message}" for event in selected]


def _hypotheses(error_events: list[Event], deploy_events: list[Event], db_events: list[Event]) -> list[Hypothesis]:
    hypotheses: list[Hypothesis] = []
    if deploy_events and error_events:
        hypotheses.append(
            Hypothesis(
                title="Recent deployment is correlated with the error burst",
                confidence=0.82,
                evidence_ids=[event.id for event in deploy_events[:2] + error_events[:3]],
            )
        )
    if db_events:
        hypotheses.append(
            Hypothesis(
                title="Database connectivity or pool pressure is degrading requests",
                confidence=0.78,
                evidence_ids=[event.id for event in db_events[:5]],
            )
        )
    if error_events and not hypotheses:
        hypotheses.append(
            Hypothesis(
                title="Application-level failures are present but need external context",
                confidence=0.55,
                evidence_ids=[event.id for event in error_events[:5]],
            )
        )
    if not hypotheses:
        hypotheses.append(Hypothesis(title="No major incident signature detected", confidence=0.4))
    return hypotheses


def _actions(hypotheses: list[Hypothesis], service: str):
    titles = " ".join(h.title.lower() for h in hypotheses)
    actions = [
        action(
            "Open read-only dashboards for latency, error rate, and saturation",
            "Read-only validation should happen before any production change.",
        )
    ]
    if "deployment" in titles:
        actions.append(
            action(
                f"Rollback {service} to the previous stable release",
                "Deployment correlation is strong and rollback is usually the fastest reversible mitigation.",
                f"kubectl rollout undo deployment/{service}",
            )
        )
    if "database" in titles:
        actions.append(
            action(
                "Increase database pool capacity only after confirming DB headroom",
                "Pool pressure can be mitigated, but scaling clients without DB headroom worsens the outage.",
            )
        )
    actions.append(
        action(
            "Write an incident note with evidence IDs and owner assignments",
            "A structured handoff prevents duplicated investigation work.",
        )
    )
    return actions


def _top(counter: Counter) -> str:
    return ", ".join(f"{key}={value}" for key, value in counter.most_common(3)) or "none"
