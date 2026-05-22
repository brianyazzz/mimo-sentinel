from __future__ import annotations

import os
from typing import Any

import httpx

from .models import Event, IncidentReport
from .prompt import build_incident_prompt
from .validator import validate_citations


class MiMoClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None, model: str = "mimo-s1"):
        self.api_key = api_key or os.getenv("MIMO_API_KEY")
        self.base_url = (base_url or os.getenv("MIMO_BASE_URL") or "https://api.xiaomimimo.com/v1").rstrip("/")
        self.model = model

    def analyze(self, events: list[Event], service: str) -> IncidentReport | None:
        if not self.api_key:
            return None

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": build_incident_prompt(events, service),
            "response_format": {"type": "json_object"},
        }
        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                timeout=45,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            report = IncidentReport.model_validate_json(content)
            validate_citations(report, events)
            report.mimo_used = True
            return report
        except Exception:
            return None
