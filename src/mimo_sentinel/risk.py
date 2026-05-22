from __future__ import annotations

from .models import RemediationAction, RiskLevel

BLOCKED_TERMS = ("drop database", "rm -rf", "delete volume", "truncate table")
HIGH_TERMS = ("rollback", "restart", "failover", "shift traffic")
MEDIUM_TERMS = ("scale", "increase", "decrease", "config")


def classify_action(title: str, command_hint: str | None = None) -> RiskLevel:
    text = f"{title} {command_hint or ''}".lower()
    if any(term in text for term in BLOCKED_TERMS):
        return RiskLevel.blocked
    if any(term in text for term in HIGH_TERMS):
        return RiskLevel.high
    if any(term in text for term in MEDIUM_TERMS):
        return RiskLevel.medium
    return RiskLevel.low


def action(title: str, rationale: str, command_hint: str | None = None) -> RemediationAction:
    return RemediationAction(
        title=title,
        risk=classify_action(title, command_hint),
        command_hint=command_hint,
        rationale=rationale,
    )
