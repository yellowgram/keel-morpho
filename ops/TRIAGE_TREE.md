# Keel — First-line triage tree (sticky)

**Date:** 2026-09-26 EDT · Keep this sticky for outages.

1. **Mandate hash match?** `config.json.mandate_hash` == `mandate_hash.txt` == pack header. Mismatch → **ABORT / halt**; do not trust pack; human fix + amendment if intentional.
2. **DEMO / KILL / INCONSISTENT flags?** DEMO_ONLY process gate on? KILL forcing IDLE_ALL? DEMO+open_size → **EXIT PRIORITY**.
3. **graphql_ok / llama_ok / rpc_ok?** GraphQL hard-fail → HOLD/STALE last known; never invent markets or clear ALLOW. rpc_ok=false OK under DEMO+idle; **not** OK for live size.
4. **STALE_S / O6?** Age > STALE_S → O6_FAIL → no PASS → no ALLOCATE.
5. **ALLOW poison vs eligible=0?** Rejected ALLOW rows in pack? Eligible=0 → IDLE success — do not loosen Regime B without B2.
6. **PARTIAL vs true EXIT?** PARTIAL under DEMO idle may be accepted; with open size treat O3/O4 PARTIAL as WARN floor. O*_EXIT → freeze new / EXIT path / agent may set KILL if open size.
7. **Human paste error on ACTION/ALLOW?** Format and latest market table; never sign from recommendation vibes.

## Loss / near-miss labels (use one)

Protocol bug · oracle · LST depeg · paste error · unsigned-from-recommendation · RPC lie · attention miss · regime-too-tight (zero P&L).

## Halt

Known-good config + last GREEN/AMBER pack; set KILL; stop signing independently of observe.
