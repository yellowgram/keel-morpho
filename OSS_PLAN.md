# Keel — OSS Founder-Lock Plan

**STATUS: PUBLIC_READY**
**Date:** 2026-09-26 09:24 EDT  
**Product lock:** Keel is an **OSS self-run toolkit** for a single operator's Morpho V1 Regime-B observe → score → recommend → REFERENCE_ONLY draft loop.  
**Not:** multi-user hosted vault · advisory/consulting product · Soft-WTP · kits sell / invoice outreach · auto-sign / auto-ALLOW / agent-held keys.

---

## 1. Public vs private split

| Area | Public (publish) | Private (founder-only; gitignore / `private/`) |
|---|---|---|
| Mandate & briefs | `BRIEF_v1.1.md`, `STANDING_BRIEF.md`, `mandate_hash.txt` | Personal amendments not in tree |
| Config | `config.example.json` (DEMO defaults) | `config.json` (local copy; may later hold vault) |
| Sample book | `eth-credit-conservative/` scrubbed sample (pack/log/allowlist shape) | Live packs with personal notes; any real vault fields |
| Scripts (toolkit) | `scripts/keel_ops_gates.py`, `hard_daily_observe.py`, `first_run.py`, `keel_daily_observe_once.sh`, `scripts/tests/` | `keel_targets_status.py`, `keel_followup_drafts.py` → `private/scripts/` |
| Ops docs | `ops/` (MENTAL_MODEL, RACI, SLAS, TRIAGE, LIVE_EXIT tick-sheet) | Founder attention calendars with PII |
| Income / outreach | **None** in public narrative | Entire `income/` tree → `private/income/` |
| Strategy docs | Kill-list mention only in README/ops | `STRATEGY_INCOME.md`, `INCOME_ALIGNMENT.md`, Soft-WTP / kits docs |
| Ops gap docs | `MINIMUM_OPS_CHECKLIST.md`, `OPERATOR_NEEDS_BEYOND_CHECKLIST.md`, `GAP_AUDIT_AND_PLAN.md`, `SHIP_NOTES_*` (scrubbed) | Email scoreboards, outbound drafts |
| License / entry | `LICENSE` (MIT), `README.md`, `.gitignore`, `OSS_PLAN.md`, `SHIP_NOTES_OSS.md` | RPC URLs with tokens, `.env`, key material |

---

## 2. Files to publish (public tree)

```
LICENSE
README.md
.gitignore
config.example.json
BRIEF_v1.1.md
STANDING_BRIEF.md
mandate_hash.txt
OSS_PLAN.md
SHIP_NOTES_OSS.md
MINIMUM_OPS_CHECKLIST.md
OPERATOR_NEEDS_BEYOND_CHECKLIST.md
GAP_AUDIT_AND_PLAN.md
SHIP_NOTES_OPS_GAPS.md
ops/
  README.md MENTAL_MODEL.md RACI.md SLAS.md TRIAGE_TREE.md LIVE_EXIT_GATE_TICKSHEET.md
scripts/
  keel_ops_gates.py
  hard_daily_observe.py
  first_run.py
  keel_daily_observe_once.sh
  tests/test_keel_ops_gates.py
eth-credit-conservative/          # sample sleeve (DEMO)
  config.json  (DEMO mirror of example; or symlink note)
  pack.md      (scrubbed sample shape — public Morpho ids OK)
  log.md       (truncate or keep DEMO log; no PII)
  allowlist.md
  day0_raw.json / observe_raw.json  (optional fixture; no secrets)
```

---

## 3. Files to gitignore / move to `private/`

**Move (preserve founder data — do not delete):**
- `income/` → `private/income/` (SCOREBOARD, targets.csv, briefs, client-kits, followup_drafts, SEND_KITS, OUTBOUND, pack_attach, FOUNDER_BRIEF)
- `scripts/keel_targets_status.py` → `private/scripts/`
- `scripts/keel_followup_drafts.py` → `private/scripts/`
- `STRATEGY_INCOME.md` → `private/`
- `INCOME_ALIGNMENT.md` → `private/`

**Gitignore (never publish):**
- `config.json` (operator-local; copy from example)
- `private/`
- `income/` (belt-and-suspenders if recreated)
- `.env`, `.env.*`, `*.pem`, `*.key`, `id_rsa*`, `keystore*`, `wallet.json`
- `**/__pycache__/`, `*.pyc`, `.pytest_cache/`
- RPC / provider secret files: `rpc.secrets*`, `*alchemy*key*`, `*infura*key*`
- Local overrides: `config.local.json`, `allowlist.local.md`

**Keep in place but not “product narrative”:** founder gap/ship notes stay; README must not link Soft-WTP or kits as features.

---

## 4. LICENSE

**MIT** — short, standard OSS. README + LICENSE must state: no custody, no warranty for capital loss, operator signs own transactions.

---

## 5. README outline (stranger-operator)

1. One-liner: self-run Morpho Regime-B observe toolkit (not a vault, not custody)
2. **Loud:** `IDLE_ALL` + RegimeB eligible=0 is **success**
3. **Loud:** **You** paste ALLOW / ACTION; **you** sign; agent never holds keys
4. Quickstart: copy `config.example.json` → `config.json`; run observe DEMO
5. Mental model → `ops/MENTAL_MODEL.md` + RACI / triage / SLAs
6. How gates work (five-way AND, KILL, mandate abort, DEMO refuse keys)
7. What not to expect (no hosted multi-user, no Soft-WTP, no kits/invoice bot, no auto-ALLOW)
8. Kill list
9. License / disclaimer

---

## 6. DEMO defaults (`config.example.json`)

- `DEMO_ONLY`: **true**
- `VAULT_ADDRESS` / `HOST_VAULT` / `LIVE_SLEEVE_ADDRESSES`: **null**
- `ALLOW`: **[]**
- `KILL`: **false**
- `OPEN_SIZE_WETH`: **0**
- No RPC API keys; public Morpho GraphQL + Llama prices only
- Well-known token addresses (WETH/wstETH/stETH) OK — not secrets
- Paths relative / documented as repo-relative after ROOT portability fix

---

## 7. Scrub checklist

- [ ] No private keys / mnemonics / seed phrases in tree
- [ ] No RPC URLs with embedded API keys
- [ ] No founder Gmail threads or personal emails in README / public packs
- [ ] Scoreboards / targets / outreach → `private/`
- [ ] `config.json` gitignored; example has DEMO defaults
- [ ] Observe wrapper does not require `income/` for public path
- [ ] Scripts resolve `ROOT` from repo location (not hardcoded `/workspace/keel` only)
- [ ] Sample pack has no personal notes / BMNR holdings as positions
- [ ] Scan: `rg` for key-like patterns before declare PUBLIC_READY

---

## 8. Founder-only (stays off public product)

- Income funnel, client kits, Soft-WTP, invoice outreach
- Real vault address, paid RPC credentials, signer / Safe
- DEMO → live flip (tick-sheet is public; execution is founder)
- Push to GitHub / release tagging (founder-owned)
- Any Gmail / X / contact CRM state

---

## 9. Kill list (must stay killed in public narrative)

1. Multi-user hosted vault  
2. Advisory / consulting packaging as Keel “product”  
3. Soft-WTP  
4. Kits sell / invoice outreach automation  
5. Auto-sign / auto-ALLOW / agent-held keys  
6. Pricing BMNR / BMNU / CoinDCX as book positions  

---

## 10. Success criteria — “public-ready”

1. Stranger can clone (or copy tree), `cp config.example.json config.json`, run `python3 scripts/tests/test_keel_ops_gates.py` → **12/12**
2. Stranger can run DEMO observe (network) and get `IDLE_ALL` without secrets
3. README loudly states IDLE success + human ACTION
4. `income/` and outreach scripts are under `private/` or gitignored — not in public narrative
5. No secrets in public paths (scrub pass clean)
6. MIT LICENSE present
7. Ops gates remain the safety core (unchanged five-way AND / KILL / mandate abort)
8. `SHIP_NOTES_OSS.md` has 3 design + 3 code-review adversarial iterations with fixes applied
9. `STATUS: PUBLIC_READY` written at top of this file when done

---

## 11. Implementation order (this run)

1. Design ×3 in `SHIP_NOTES_OSS.md` → flag ready  
2. Create `private/`, move income + outreach scripts + income strategy docs  
3. Add LICENSE, `.gitignore`, `config.example.json`, stranger README  
4. Make ROOT portable; decouple observe shell from `income/`  
5. Scrub pass + sample fixture note  
6. Code-review ×3 + fix; smoke 12/12  
7. Set `STATUS: PUBLIC_READY`
