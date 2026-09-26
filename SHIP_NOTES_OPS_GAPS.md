# Keel — Ship Notes: Ops Gaps Close (Founder GO)

**Date:** 2026-09-26 EDT  
**Constraint:** DEMO_ONLY=true forever unless human flips (do not flip). No keys, no auto-ALLOW/ACTION, no vault invent, no BMN* pricing.  
**Audit:** `/workspace/keel/GAP_AUDIT_AND_PLAN.md`

---

## (2) Adversarial DESIGN iterations (before coding)

### Design Iteration 1 — Expert A (security / authority abuse)

**Attack thesis:** Soft DEMO labels + agent-writable vault/ALLOW + recommendations that feel like orders = fund loss. Mandate hash that is printed but not aborted on mismatch lets a brief edit silently authorize risk. Kill switch only clearable by agent fails under EXIT when founder AFK — but auto-clear by agent is worse.

| Hardening applied to plan | Why |
|---|---|
| Mandate triple-pin check **aborts before pack overwrite** | Prevents silent mandate drift into a “valid” pack |
| DEMO gate is a **process function** at script entry: refuse key-env patterns, refuse invent of ACTION/ALLOW/VAULT, print DEMO_ONLY on every emit | Label-only DEMO is theater |
| Five-way AND as a pure function `can_allocate(...)` with unit tests | Removes “almost live” allocate paths |
| KILL: agent may **set** on EXIT-class; never auto-clear; human-only clear documented | AFK EXIT coverage without agent authority creep |
| ALLOW paste-check rejects ineligible rows **before** they count toward AND | Poison ALLOW must not become authorized |

**Killed from naive plan:** Writing a fake VAULT for “testing”; auto-ALLOW from eligible markets; inventing ACTION from recommendation.

### Design Iteration 2 — Expert B (reliability / thin attention)

**Attack thesis:** Founder pages on noise; GraphQL death clears state; missed observes while live go unnoticed; quiet IDLE regenerates busywork; STALE markets still get PASS vibes.

| Hardening | Why |
|---|---|
| Quiet-if-IDLE: same rec + blockers fingerprint + eligible set → append short log line, still refresh pack header/fetch but recommendation path unchanged | Prevents observe-as-busywork |
| Missed-observe: detect weekday gap vs last log; DEMO+idle = note only; never auto-pager invent | Differentiated severity |
| GraphQL hard-fail: HOLD recommendation; never clear ALLOW/DEMO/KILL; STATUS RED | Avoid empty-markets ⇒ wipe disaster |
| O6: age > STALE_S → **FAIL** (not WARN) for PASS/ALLOCATE eligibility | Stale PASS worse than honest IDLE |
| Config/brief presence abort at entry | Unreadable config must not emit “GREEN” packs |
| Remove `keel_targets_status.py` from observe-once shell | Kill list: kits/targets not ops |

**Killed:** Weekend vanity auto-observe; regenerating income kits on observe; treating PARTIAL O4 under DEMO idle as RED.

### Design Iteration 3 — Expert C (capital / size / path dependence)

**Attack thesis:** Book blows on first-size hubris, relative market cap, exit-liq fiction, and “eligible=0 so loosen Regime B.” Caps missing from config means live flip with “TBA.”

| Hardening | Why |
|---|---|
| Size cap **fields** in config with null/placeholder defaults; agent never raises | Checklist §D before live; numbers founder-owned |
| MARKET_REL_CAP enforced in ALLOW paste-check (`cap_rel ≤ MARKET_REL_CAP`) | Relative share discipline at paste time |
| ALLOCATE draft path: if five-way fails → IDLE_ALL (or REDUCE/EXIT if open — N/A today) | No allocate theater under DEMO |
| Live-exit tick-sheet as **doc only**; paper→dust path documented | Do not fake custody/RPC/drills |
| Ops docs: mental model, RACI, triage, SLAs | Operator needs that are checklist/docs |
| INCONSISTENT detector stub: DEMO_ONLY ∧ open_size_weth>0 → EXIT PRIORITY banner | Future-proof; today open_size=0 |

**Killed:** Soft-WTP, multi-user vault, grants packaging, inventing eligible markets, BMN* hedges.

---

## Implementation summary (after design)

See sections below after code ships. Files touched listed in final report.

---

## (4) Adversarial CODE-REVIEW iterations (after implement)

### Code-review Iteration 1 — Expert A (authority / DEMO bypass)

**Findings:**
1. Mandate mismatch must abort **before** pack write — verified; pack mtime unchanged on abort smoke.
2. DEMO_ONLY still allowed `ALLOCATE_ELIGIBLE` recommendation if five-way somehow true — **fixed**: hard freeze reallocates to IDLE_ALL under DEMO.
3. `set_kill_in_config(False)` could clear KILL — **fixed**: raises RuntimeError; clear is human-only.
4. Key-env substrings checked; observe aborts if present under DEMO process gate.

**Fixes applied:** DEMO freeze on ALLOCATE_*; refuse clear KILL; abort path proven.

### Code-review Iteration 2 — Expert B (reliability / stale / quiet)

**Findings:**
1. O6 used WARN for age>STALE_S — **fixed** → O6_FAIL; ALLOCATE PASS blocked.
2. Clock skew produced negative ages historically — **fixed**: `age = max(0, ...)`.
3. GraphQL hard-fail overwrote pack with empty markets looking like wipe — **hardened**: HOLD rationale + stale_cache marker; never clear ALLOW/DEMO/KILL; empty table preferred over inventing markets.
4. Quiet-if-IDLE fingerprint + missed-observe weekday gap wired; append-only log preserved (short line when quiet).
5. `keel_daily_observe_once.sh` no longer calls killed `keel_targets_status.py`.

**Fixes applied:** O6_FAIL, age clamp, HOLD/STALE notes, shell kill-list respect.

### Code-review Iteration 3 — Expert C (capital gates / paste poison)

**Findings:**
1. Five-way AND missing as explicit function — **added** `five_way_and` + pack/log display.
2. ALLOW paste-check missing — **added** against latest table + Regime-B-eligible; rejects high LLTV, bad collateral, cap_rel > MARKET_REL_CAP, ineligible uniqueKey.
3. Size cap fields missing from config — **added** placeholders (null); agent never raises.
4. KILL / OPEN_SIZE_WETH / ALLOW=[] added; VAULT remains null; DEMO_ONLY remains true.
5. Drill status now **SKIP_IDLE** while no open size (checklist PASS_DRILL/SKIP_IDLE).

**Residual accepted this pass:** Full O5/O7 Morpho liquidity modeling stays N/A under DEMO idle; live RPC provider payment is founder-owned; GraphQL-fail does not reconstruct full prior market table (marker only — no invent).

---

## Implementation file list

| Path | Change |
|---|---|
| `GAP_AUDIT_AND_PLAN.md` | New — full §1–33 + operator needs audit |
| `SHIP_NOTES_OPS_GAPS.md` | This file — design ×3 + code-review ×3 |
| `config.json` | +KILL, ALLOW=[], OPEN_SIZE_WETH, size cap placeholders |
| `eth-credit-conservative/config.json` | Synced |
| `scripts/keel_ops_gates.py` | New — testable gates |
| `scripts/hard_daily_observe.py` | Gates at entry; five-way; ALLOW check; O6_FAIL; quiet/miss; pack/log |
| `scripts/keel_daily_observe_once.sh` | Dropped targets/kits from ops path |
| `scripts/tests/test_keel_ops_gates.py` | Local unit tests (12) |
| `ops/MENTAL_MODEL.md` | Operator mental model |
| `ops/RACI.md` | RACI |
| `ops/SLAS.md` | Attention SLAs |
| `ops/LIVE_EXIT_GATE_TICKSHEET.md` | Founder live-exit tick-sheet |
| `ops/TRIAGE_TREE.md` | Sticky triage |
| `ops/README.md` | Index |

## Smoke results (2026-09-26 ~09:20 EDT)

- Unit gates: **12/12 PASS** (no network).
- Mandate mismatch abort: exit 1, pack mtime unchanged.
- Dry observe: STATUS **AMBER**, recommendation **IDLE_ALL**, eligible=0, five-way blocked (ALLOW/PASS/VAULT/DEMO), drill SKIP_IDLE, rpc_ok=false (403 accepted under DEMO), graphql_ok=true, llama_ok=true.

*Ship closed for Keel-shippable ops gaps under DEMO_ONLY. Founder-owned custody/RPC/Safe/drills remain tick-sheet only.*

