from __future__ import annotations

import json

from .models import Event

SYSTEM_PROMPT = """You are MiMo Sentinel, an evidence-bound incident analyst.

Rules:
- Return strict JSON matching the IncidentReport schema.
- Every hypothesis must cite event IDs from the provided event list.
- Do not invent services, timestamps, metrics, or commands.
- Prefer reversible remediation actions.
- Mark destructive actions as blocked.
"""


def build_incident_prompt(events: list[Event], service: str, max_events: int = 400) -> list[dict]:
    compact_events = [
        {
            "id": event.id,
            "timestamp": event.timestamp,
            "service": event.service,
            "level": event.level,
            "message": event.message,
        }
        for event in events[:max_events]
    ]
    schema_hint = {
        "service": service,
        "severity": "low|medium|high|critical",
        "summary": "short incident summary",
        "timeline": ["E0001 timestamp service: important event"],
        "hypotheses": [
            {
                "title": "root cause hypothesis",
                "confidence": 0.0,
                "evidence_ids": ["E0001"],
            }
        ],
        "actions": [
            {
                "title": "recommended action",
                "risk": "low|medium|high|blocked",
                "command_hint": "optional command or null",
                "rationale": "why this action is safe or useful",
            }
        ],
        "mimo_used": True,
    }
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": json.dumps(
                {
                    "task": "Analyze the incident and produce an evidence-bound remediation brief.",
                    "primary_service": service,
                    "schema": schema_hint,
                    "events": compact_events,
                },
                ensure_ascii=True,
            ),
        },
    ]
