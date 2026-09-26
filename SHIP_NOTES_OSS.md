# Keel — SHIP_NOTES_OSS (Founder lock / OSS public-ready)

**Date:** 2026-09-26 EDT  
**Standing practice:** 3 progressive adversarial DESIGN iterations → implement → 3 deep adversarial CODE-REVIEW iterations → fix → smoke.

---

## DESIGN iterations (improve the plan)

### Design-1 — Adversarial: “Stranger opens the repo and thinks Keel is Soft-WTP / outreach”

**Attack:** Root tree mixed toolkit with `income/` (SCOREBOARD, targets.csv, client-kits, SEND_KITS) and income strategy docs. A README that “also mentions pilots” reopens Soft-WTP / kits.

**Improve plan:** Move entire `income/` → `private/income/`; move outreach scripts → `private/scripts/`; move `STRATEGY_INCOME.md` / `INCOME_ALIGNMENT.md` → `private/`; public README kill list first-class; observe shell must not `mkdir income`.

**Applied.**

### Design-2 — Adversarial: “Hardcoded `/workspace/keel` + live `config.json` in tree = unusable / fake custody”

**Attack:** Absolute ROOT breaks clones; publishing operator `config.json` teaches committing vault later; box-specific venv PATH.

**Improve plan:** `ROOT = Path(__file__).resolve().parents[N]`; publish `config.example.json` only; gitignore `config.json`; portable observe shell; clear abort if config missing.

**Applied.**

### Design-3 — Adversarial: “Scrub miss leaks founder CRM; gates weakened for DX”

**Attack:** Scoreboard emails / CRM state, personal FOUNDER_BRIEF. Temptation to simplify five-way AND or DEMO key refuse. Missing MIT / custody disclaimer.

**Improve plan:** Scrub checklist; CRM only under `private/`; gates sacred; MIT + loud IDLE + human ACTION; require 12/12 after moves.

**Applied.** `OSS_PLAN_READY.flag` + `STATUS: PLAN_READY` (then PUBLIC_READY).

---

## CODE-REVIEW iterations (attack the implementation; fix)

### Code-review-1 — Adversarial: “Observe still couples to income/; absolute paths remain”

**Attack:** `keel_daily_observe_once.sh` still `mkdir -p income` and copies pack there; scripts still `ROOT = Path("/workspace/keel")`; missing `config.json` yields opaque crash.

**Findings / fixes:**
- Rewrote shell: repo-relative `ROOT`, `python3` on PATH, optional mirror only if `private/income/` exists.
- Portable ROOT in `hard_daily_observe.py`, `first_run.py`, tests.
- Explicit `ABORT: config.json missing — copy config.example.json…`.
- Outreach scripts path-updated under `private/scripts/` → `private/income/`.

### Code-review-2 — Adversarial: “OSS DX quietly loosens safety core”

**Attack:** Skip mandate abort, allow empty five-way for “hello world ALLOCATE”, or stop refusing key-like env so demos “feel live.”

**Findings / fixes:**
- Did **not** change `keel_ops_gates.py` gate logic (five-way AND, KILL, key-env refuse, paste-check, mandate mismatch).
- Smoke: `python3 scripts/tests/test_keel_ops_gates.py` → **12/12** from `/tmp` (ROOT portable).
- README documents gates as sacred; kill list explicit.

### Code-review-3 — Adversarial: “Public tree still narrates Soft-WTP or leaks PII”

**Attack:** Emails in README/packs; Soft-WTP as feature; `income/` still present; `MINIMUM_OPS` says “OSS not in scope.”

**Findings / fixes:**
- Confirmed `income/` absent from public root; scoreboards only under `private/`.
- Public email scrub: no operator CRM emails in product docs (kill-list mentions of Soft-WTP only).
- 64-char hex in packs = public Morpho `uniqueKey`s, not private keys — accepted.
- Updated `MINIMUM_OPS_CHECKLIST.md` header: OSS toolkit in scope; Soft-WTP/kits still killed.
- Softened BRIEF absolute paths; added `eth-credit-conservative/README.md`; ops RACI/MENTAL_MODEL operator-facing.
- MIT `LICENSE` + custody disclaimer present.

---

## Smoke (2026-09-26 EDT)

| Check | Result |
|---|---|
| Gates unit tests | **12/12 passed** (cwd=/tmp) |
| Missing config abort | OK |
| README / plan paths exist | OK |
| `income/` not in public root | OK |
| Outreach scripts not in `scripts/` | OK |
| `config.example.json` DEMO invariants | OK |
| Live network observe | Skipped for ship smoke (can hang on GraphQL/RPC); gates + DEMO defaults verified offline |

**PUBLIC_READY** criteria from `OSS_PLAN.md` §10 met on box. GitHub push remains founder-owned.
