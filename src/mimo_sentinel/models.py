from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    blocked = "blocked"


class Event(BaseModel):
    id: str
    timestamp: str | None = None
    service: str = "unknown"
    level: str = "info"
    message: str
    raw: str


class Hypothesis(BaseModel):
    title: str
    confidence: float = Field(ge=0, le=1)
    evidence_ids: list[str] = Field(default_factory=list)


class RemediationAction(BaseModel):
    title: str
    risk: RiskLevel
    command_hint: str | None = None
    rationale: str


class IncidentReport(BaseModel):
    service: str
    severity: Severity
    summary: str
    timeline: list[str]
    hypotheses: list[Hypothesis]
    actions: list[RemediationAction]
    mimo_used: bool = False
