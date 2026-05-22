# Demo Report

Command:

```bash
mimo-sentinel examples/outage.log --service checkout-api
```

Input: 10 lines of mixed deploy, warning, error, and dependency-health logs.

Output:

```text
Incident Brief: checkout-api
Severity: critical
MiMo used: no, offline fallback

checkout-api shows 5 suspicious events across 8 parsed records. Top services: checkout-api=8, deployer=1, payment-worker=1. Level mix: error=5, warn=2, info=1.

Timeline:
- E0001 2026-05-22T14:02:11Z deployer: deploy checkout-api image tag 2026.05.22-rc3 started
- E0004 2026-05-22T14:04:22Z checkout-api: database pool timeout after 2000ms route=/checkout
- E0005 2026-05-22T14:04:24Z checkout-api: 5xx response status=503 route=/checkout
- E0006 2026-05-22T14:04:30Z checkout-api: database connection acquisition failed pool_used=20 pool_max=20
- E0008 2026-05-22T14:04:49Z checkout-api: 5xx response status=503 route=/checkout
- E0010 2026-05-22T14:05:41Z checkout-api: database pool timeout after 2000ms route=/checkout

Hypotheses:
- Recent deployment is correlated with the error burst | confidence=0.82 | evidence=E0001, E0004, E0005, E0006
- Database connectivity or pool pressure is degrading requests | confidence=0.78 | evidence=E0004, E0006, E0010

Recommended Actions:
1. [low] Open read-only dashboards for latency, error rate, and saturation
2. [high] Rollback checkout-api to the previous stable release | hint: kubectl rollout undo deployment/checkout-api
3. [medium] Increase database pool capacity only after confirming DB headroom
4. [low] Write an incident note with evidence IDs and owner assignments
```

## Why This Demo Matters

The report does more than summarize text. It connects the deploy marker, database pool errors, 5xx responses, and healthy payment-worker signal into a bounded blast-radius narrative. Each hypothesis includes event IDs so an engineer can verify the reasoning.
