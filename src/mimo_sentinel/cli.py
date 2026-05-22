from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from .analyzer import analyze_events
from .mimo_client import MiMoClient
from .parser import parse_file
from .report import render_report

app = typer.Typer(help="MiMo-powered incident analysis CLI")
console = Console()


@app.command()
def analyze(
    log_file: Path = typer.Argument(..., help="Path to raw log, JSONL, or incident notes"),
    service: str = typer.Option("unknown", "--service", "-s", help="Primary service under investigation"),
    use_mimo: bool = typer.Option(False, "--use-mimo", help="Call MiMo API when MIMO_API_KEY is set"),
    model: str = typer.Option("mimo-s1", "--model", help="MiMo model name"),
) -> None:
    """Analyze an incident and print a structured remediation brief."""
    events = parse_file(log_file)
    report = analyze_events(events, service=service, use_mimo=use_mimo, mimo_client=MiMoClient(model=model))
    console.print(render_report(report))


if __name__ == "__main__":
    app()
