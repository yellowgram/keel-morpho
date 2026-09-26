# Keel — Attention SLAs

**Date:** 2026-09-26 EDT · DEMO_ONLY

## Cadence

- **1× weekday observe @ 08:00 America/New_York** via `scripts/keel_daily_observe_once.sh` only.
- No weekend auto unless KILL set or open allocation WARN/EXIT.
- **Quiet-if-IDLE:** if recommendation + blockers + eligible set unchanged vs prior weekday, log short line; do not treat re-observe as progress.

## Founder attention SLA

- Weekday skim: pack header + recommendation + blockers + fetch booleans (**≤5 min**).
- Escalate only on: KILL set, any O*_EXIT, mandate mismatch, fetch hard-fail 2 days running, DEMO-exit flip request, INCONSISTENT DEMO+open size.
- No daily deep-dive required while IDLE_ALL + DEMO.

## Agent attention SLA

- Run observe, emit pack+log, flag PARTIAL checks.
- Never chase income kits / targets.csv as Keel-ops work.
- Never invent ALLOW / ACTION / vault / live capital.

## Missed-observe

- 1 miss: next run notes gap.
- 2 consecutive weekday misses with open allocation (post-DEMO): pack KILL warn; human must ack.
- While DEMO+idle: miss is **log-only**, not pager.
