# Architecture

MiMo Sentinel is split into small, auditable stages. This keeps the MiMo reasoning layer powerful while making every transformation inspectable.

## Pipeline

```text
1. Ingest
   Raw logs, JSONL events, deploy notes, incident chat exports

2. Normalize
   Convert every line into an Event with a stable event ID

3. Build Prompt
   Create an evidence-bound MiMo prompt with explicit output schema

4. Reason
   MiMo-7B compresses signal; MiMo-S1 ranks RCA hypotheses

5. Validate
   Reject hypotheses that cite missing event IDs

6. Gate Risk
   Label remediation as low, medium, high, or blocked

7. Render
   Produce human-readable incident brief and machine-readable JSON
```

## Design Principles

- **Evidence over vibes**: every RCA claim should cite concrete event IDs.
- **Human-approved action**: the tool recommends actions, it does not mutate production by default.
- **Graceful fallback**: offline heuristic mode keeps demos, tests, and local triage available without API access.
- **Composable agents**: summarizer, RCA analyst, and risk reviewer can be split across MiMo models.

## MiMo Prompt Contract

The MiMo prompt requires:

- JSON output matching `IncidentReport`
- one or more hypotheses
- confidence score per hypothesis
- evidence event IDs per hypothesis
- remediation actions with risk labels

The local validator checks whether evidence IDs exist in the input event set. This creates a lightweight hallucination guard that is easy to expand into stricter policy checks.
