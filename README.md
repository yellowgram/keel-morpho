# Keel

**Self-run OSS toolkit** for a single operator: Morpho V1 **Regime B** observe → score → recommend → REFERENCE_ONLY draft for a wstETH–WETH credit sleeve.

It is **not** a custodian, multi-user vault, yield optimizer, Soft-WTP product, consulting kit, or auto-signer.

---

## Loud truths (read these)

1. **`IDLE_ALL` + Regime-B eligible = 0 is success** — not a bug. Regime B (LLTV ≤ 0.86 WAD, wstETH-only) may leave every observed market ineligible. Staying idle is a valid capital policy.
2. **You sign your own ACTION.** You paste ALLOW rows, the ACTION line, any B2 amendment, and any future signature. The agent / scripts **never** hold keys, never auto-ALLOW, never invent VAULT_ADDRESS or ACTION.
3. **DEMO_ONLY=true by default.** Public tree ships with null vault, empty ALLOW, no secrets. Do not invent live capital.

---

## Quickstart (DEMO observe)

```bash
cp config.example.json config.json
python3 scripts/tests/test_keel_ops_gates.py   # expect 12/12
python3 scripts/hard_daily_observe.py          # network: Morpho GraphQL + Llama
# or: bash scripts/keel_daily_observe_once.sh
```

Outputs land under `eth-credit-conservative/pack.md` + append-only `log.md`.

Requires: Python 3.10+, outbound HTTPS. RPC is optional while DEMO+idle (`rpc_ok=false` is OK).

---

## Mental model

| Role | Does | Does not |
|---|---|---|
| Scripts / agent | Fetch, score, recommend, draft REFERENCE_ONLY, log, emit pack | Sign, load keys, auto-ALLOW, invent ACTION/vault |
| You (operator) | Paste ALLOW / ACTION / B2; set vault; flip DEMO via tick-sheet; clear KILL; sign txs | Expect Keel to custody or “just allocate” |

See:

- [`ops/MENTAL_MODEL.md`](ops/MENTAL_MODEL.md) — what Keel is / is not
- [`ops/RACI.md`](ops/RACI.md) — who pastes / signs / clears KILL
- [`ops/TRIAGE_TREE.md`](ops/TRIAGE_TREE.md) — sticky outage runbook
- [`ops/SLAS.md`](ops/SLAS.md) — cadence / skim
- [`ops/LIVE_EXIT_GATE_TICKSHEET.md`](ops/LIVE_EXIT_GATE_TICKSHEET.md) — before flipping DEMO
- [`BRIEF_v1.1.md`](BRIEF_v1.1.md) / [`STANDING_BRIEF.md`](STANDING_BRIEF.md) — mandate

---

## How gates work (safety core)

Do **not** weaken these for convenience:

- **Five-way AND** before any ALLOCATE path: `ALLOW ∩ PASS ∩ VAULT ∩ !DEMO_ONLY ∩ !KILL`
- **KILL** → IDLE_ALL; freeze ALLOCATE; only **you** clear KILL
- **Mandate hash** mismatch → abort (no pack claiming the wrong mandate)
- **DEMO process gate** → refuse private-key-like env vars; refuse inventing ACTION / ALLOW / vault
- **ALLOW paste-check** → reject poison collateral / LLTV / uniqueKey / cap

Unit tests: `python3 scripts/tests/test_keel_ops_gates.py` → **12/12**.

---

## Config

- Copy `config.example.json` → `config.json` (gitignored).
- Defaults: `DEMO_ONLY=true`, `VAULT_ADDRESS=null`, `ALLOW=[]`, `KILL=false`, `OPEN_SIZE_WETH=0`.
- Thresholds and Regime B filters are config-owned; do not loosen without a human amendment.

---

## Sample pack shape

`eth-credit-conservative/` is a scrubbed DEMO sleeve (public Morpho market ids, empty allowlist, IDLE_ALL). Use it to learn pack/log shape — not as live capital.

---

## What not to expect

- No hosted multi-user vault or shared custody
- No Soft-WTP / advisory packaging as “the product”
- No kits-sell / invoice outreach automation in this toolkit
- No auto-sign, auto-ALLOW, or agent-held keys
- No BMNR / BMNU / CoinDCX priced as book positions

---

## Kill list

Multi-user vault · Soft-WTP · kits/invoice outreach · auto-sign/auto-ALLOW/agent keys · consulting-as-Keel-product.

---

## License & risk

[MIT](LICENSE). **No warranty.** Protocol risk + operator paste quality can mean total loss. You alone sign.

Founder-private book state (if any) lives under `private/` and is gitignored — not part of the public toolkit narrative.
