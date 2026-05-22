from __future__ import annotations

import json
import re
from pathlib import Path

from .models import Event

LOG_RE = re.compile(
    r"^(?P<ts>\S+\s+\S+|\S+)\s+(?P<level>DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL)\s+(?P<service>[\w.-]+)\s+-\s+(?P<msg>.*)$",
    re.IGNORECASE,
)


def parse_line(line: str, index: int) -> Event:
    raw = line.rstrip("\n")
    if not raw.strip():
        return Event(id=f"E{index:04d}", message="", raw=raw)

    try:
        data = json.loads(raw)
        return Event(
            id=f"E{index:04d}",
            timestamp=str(data.get("timestamp") or data.get("ts") or ""),
            service=str(data.get("service") or "unknown"),
            level=str(data.get("level") or "info").lower(),
            message=str(data.get("message") or data.get("msg") or raw),
            raw=raw,
        )
    except json.JSONDecodeError:
        pass

    match = LOG_RE.match(raw)
    if match:
        return Event(
            id=f"E{index:04d}",
            timestamp=match.group("ts"),
            service=match.group("service"),
            level=match.group("level").lower(),
            message=match.group("msg"),
            raw=raw,
        )

    return Event(id=f"E{index:04d}", message=raw, raw=raw)


def parse_file(path: str | Path) -> list[Event]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [event for idx, line in enumerate(lines, start=1) if (event := parse_line(line, idx)).message]
