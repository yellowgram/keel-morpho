# Keel — Gap Audit & Implementation Plan (Founder GO close)

**Date:** 2026-09-26 09:17 EDT  
**Scope:** MINIMUM_OPS_CHECKLIST.md §A–H items 1–33 + OPERATOR_NEEDS Keel-shippable (docs/scripts only).  
**Standing:** `DEMO_ONLY=true`, `VAULT_ADDRESS=null`, `ALLOW=[]`, `KILL=false` (to be added). Never invent vault/ALLOW/live capital.  
**Income:** P&L after exit DEMO — kits/targets/Soft-WTP/multi-user stay killed.

Legend: **Done** = already true in pack/script/config · **Partial** = present but incomplete vs checklist · **Missing** = not enforced · Owner **Keel** = ship now · **Founder** = tick-sheet/doc only (do not fake custody/RPC payment/Safe).

---

## MINIMUM_OPS §A–H (1–33)

### A. Mandate lock & DEMO gate

| # | Item | Status | Owner | Plan |
|---|---|---|---|---|
| 1 | Mandate hash triple-pin + abort on mismatch | **Partial** → implement | Keel | Hash exists in config + mandate_hash.txt + pack header, but observe does **not** abort on mismatch. Wire check at observe entry; STATUS RED + abort (no pack overwrite claiming wrong mandate). |
| 2 | DEMO_ONLY hard process gate | **Partial** → implement | Keel | Label printed; no key load today by luck of code path. Add explicit gate: print `DEMO_ONLY`; refuse env private-key paths; refuse ACTION invent / ALLOW invent / vault invent; refuse ALLOCATE drafts while DEMO. |
| 3 | Live-exit gate human flip checklist | **Missing** (doc) | Founder + Keel doc | Write tick-sheet under `ops/LIVE_EXIT_GATE_TICKSHEET.md`. Do **not** fake vault/RPC/drill execution. |
| 4 | Regime B filters config-only | **Done** | Keel | Enforced in `hard_daily_observe.py` ineligible_reason; agent must not loosen without amendment (document in RACI). |

### B. Kill switch & human authority

| # | Item | Status | Owner | Plan |
|---|---|---|---|---|
| 5 | KILL=true → IDLE_ALL, freeze ALLOCATE; agent may set on EXIT; human clears | **Missing** → implement | Keel | Add `KILL` to config (default false). Observe reads config/env; if true → IDLE_ALL + freeze ALLOCATE drafts. Agent may write KILL=true on EXIT-class O* trips; only document that human clears (no auto-clear). |
| 6 | Human owns ALLOW/ACTION/sign/B2; agent none | **Partial** → harden | Keel | Already true by convention; encode refuse invent in DEMO gate + ALLOW paste-check + five-way AND. |
| 7 | P_WSTETH drill status PASS_DRILL/SKIP_IDLE | **Partial** → harden | Keel | Log already writes PASS_DRILL while idle; pack must surface drill status explicitly every run. |
| 8 | ACTION line human-only append-only | **Partial** → gate | Keel | Observe must refuse to invent/complete ACTION; document format in ops; pack notes `action_human: PENDING` only. |

### C. Observe cadence & attention

| # | Item | Status | Owner | Plan |
|---|---|---|---|---|
| 9 | Cadence 1× weekday 08:00 ET; quiet-if-IDLE | **Partial** → implement quiet | Keel | Shell wrapper exists; add quiet-if-IDLE (short log line when rec+blockers+eligible unchanged). Weekend auto only if KILL/open WARN — document in SLA. |
| 10 | Founder attention SLA ≤5 min skim | **Missing** (doc) | Keel doc | Write in `ops/SLAS.md`. |
| 11 | Agent attention SLA (no kits/targets as ops) | **Partial** → fix wrapper | Keel | `keel_daily_observe_once.sh` still calls `keel_targets_status.py` — **remove from ops path** (killed track). |
| 12 | Missed-observe notes | **Missing** → implement | Keel | On next run, if prior weekday observe missing: note gap in pack/log. DEMO+idle = log-only. |

### D. Size rules & book shape

| # | Item | Status | Owner | Plan |
|---|---|---|---|---|
| 13 | Book size caps fields in config | **Missing** → config | Keel | Add `BOOK_NOTIONAL_CAP_WETH`, `PER_MARKET_CAP_WETH`, `MAX_MARKETS_OPEN`, `DUST_CAP_WETH` placeholders (null or tiny defaults); agent never raises. Numbers are founder-owned before live. |
| 14 | MARKET_REL_CAP 0.25 on ALLOCATE draft | **Partial** → paste-check | Keel | Cap in config; enforce on ALLOW paste-check + any ALLOCATE draft path (refuse → IDLE/REDUCE). |
| 15 | Five-way AND ALLOCATE | **Partial** → implement | Keel | Empty ALLOW ⇒ IDLE today; wire explicit `ALLOW ∩ PASS ∩ VAULT ∩ !DEMO_ONLY ∩ !KILL`. |
| 16 | O5 exit-liq preflight | **Partial** | Keel | O5_N/A while idle (correct). Gate stays wired; full Morpho liq fetch may stay N/A under DEMO idle. |
| 17 | O7 outflow before >dust | **Partial** | Keel | O7_N/A while idle; document gate; no fake PASS. |

### E. Data plane health

| # | Item | Status | Owner | Plan |
|---|---|---|---|---|
| 18 | Triple-fetch + GREEN/AMBER/RED | **Done** (minor harden) | Keel | Already present; RED on GraphQL fail; add RED on mandate mismatch. |
| 19 | RPC optional DEMO idle; required live | **Done** (doc) | Keel + Founder | Pack shows rpc_ok=false under DEMO; live gate tick-sheet requires provider (founder-owned payment). |
| 20 | STALE_S → O6 FAIL blocks PASS/ALLOCATE | **Partial** → fix | Keel | Today O6_WARN on age>STALE_S; change to **O6_FAIL** for ALLOCATE path; IDLE/HOLD still ok. |
| 21 | O3/O4 non-PARTIAL with open size | **Partial** | Keel | Correct PARTIAL while idle; document WARN floor when open size (post-DEMO). |
| 22 | GraphQL hard-fail → HOLD/STALE, no wipe | **Partial** → harden | Keel | Emits HOLD on graphql fail but still overwrites pack; keep last-known note; never clear ALLOW/DEMO. |

### F. Logging, pack integrity

| # | Item | Status | Owner | Plan |
|---|---|---|---|---|
| 23 | Pack mandatory sections | **Done** (add drill/KILL/gates) | Keel | Add drill status, KILL, five-way gate summary, DEMO_ONLY print. |
| 24 | Append-only log.md | **Done** | Keel | Already append-only. |
| 25 | ALLOW paste-check | **Missing** → implement | Keel | Parse allowlist.md; reject bad collateral/lltv/uniqueKey/cap_rel. |
| 26 | Config/brief presence check | **Partial** → abort | Keel | Pack claims brief present; observe must refuse if BRIEF missing or config unreadable. |

### G. DEMO → live runbook

| # | Item | Status | Owner | Plan |
|---|---|---|---|---|
| 27 | Paper sleeve ≥5 weekday observes | **Partial** (ops) | Founder + Keel doc | Tick-sheet; reference book already continuous. |
| 28 | Dust live sleeve | **Missing** (founder) | Founder | Tick-sheet only; no fake vault. |
| 29 | Size-up by amendment only | **Done** (policy) | Keel doc | RACI + amend ritual. |
| 30 | Rollback DEMO+open = INCONSISTENT EXIT PRIORITY | **Missing** → detect | Keel | If DEMO_ONLY and open_size>0 (future field), pack STATUS INCONSISTENT — EXIT PRIORITY. Today open_size=0 → N/A. |

### H. Kill list

| # | Item | Status | Owner | Plan |
|---|---|---|---|---|
| 31 | Killed tracks stay killed | **Partial** → fix wrapper | Keel | Remove targets from observe once script; do not schedule kits. |
| 32 | No multi-user vault surface | **Done** | — | Standing. |
| 33 | No BMNR/BMNU/CoinDCX | **Done** | Keel | Pack banner already forbids. |

---

## OPERATOR_NEEDS — Keel-shippable vs founder-owned

### Implement now (docs under `/workspace/keel/ops/` + script gates)

| Need # | Topic | Action |
|---|---|---|
| 1 | Mental model | `ops/MENTAL_MODEL.md` |
| 10 | RACI | `ops/RACI.md` |
| 29 / 3 | Live-exit tick-sheet | `ops/LIVE_EXIT_GATE_TICKSHEET.md` |
| 48 | Triage tree sticky | `ops/TRIAGE_TREE.md` |
| 10,14 (checklist) | SLAs | `ops/SLAS.md` |
| PASTE / ALLOW | ALLOW paste guide | fold into RACI + paste-check code |
| 13–17 (size) | Caps placeholders | config fields only; numbers founder |

### Founder-owned (tick-sheet / accept absence — DO NOT FAKE)

| Need # | Topic | Note |
|---|---|---|
| 3–4, 54 | Custody / signer / Safe | Founder designs; never load keys |
| 5, 41 | RPC payment / API keys / bills | Founder buys; not in git |
| 4, 24 | Vault control proof | Human sets VAULT only after control proven |
| 31, 55 | Pre-sign sim tooling | Founder chooses Tenderly/Safe/etc. |
| 36 | MEV acceptance | Founder accepts |
| 42 | Backup signer | Founder or accept halt |
| 6 | Secondary oracle ownership names | Doc stub; founder names escalation |
| 8–9 | Kill notify channel / drill calendar | Founder books |
| 35 | Post-tx reconciliation ledger | Founder after live |
| 57–64 | Markets creation, insurance, legal “safe”, kits revival | NOT Keel |

---

## Implementation order (this GO)

1. Adversarial design ×3 → `SHIP_NOTES_OPS_GAPS.md`
2. Config fields: KILL, size caps placeholders, ALLOW=[], open_size_weth=0
3. `scripts/keel_ops_gates.py` — testable gates (mandate, DEMO, KILL, five-way, ALLOW paste, STALE, quiet-IDLE, miss)
4. Extend `hard_daily_observe.py` to call gates at entry + recommendation
5. Fix `keel_daily_observe_once.sh` (drop targets call)
6. Ops docs pack
7. Adversarial code-review ×3 + fixes
8. Smoke: local gate unit tests (no network required) + optional dry observe

*End gap audit.*


---

## Post-implement status (2026-09-26 ~09:21 EDT)

Keel-shippable items from the plan above are **implemented** under DEMO_ONLY:
mandate abort, DEMO process gate, KILL field + semantics, five-way AND, ALLOW paste-check, STATUS/triple-fetch, pack sections + drill SKIP_IDLE, append-only log, quiet-if-IDLE, missed-observe notes, STALE_S→O6_FAIL, brief/config abort, size-cap placeholders, ops SLAs/RACI/mental model/tick-sheet/triage, observe-once kill-list fix.

**Still founder-owned (docs only):** custody/signer/Safe, RPC payment/keys, vault control proof, pre-sign sim choice, MEV acceptance, backup signer, provider bills, live drill execution, DEMO flip.

**Standing unchanged:** DEMO_ONLY=true, VAULT_ADDRESS=null, ALLOW=[], KILL=false, eligible=0 → IDLE_ALL success.
