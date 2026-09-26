# Keel — Operator Mental Model

**Date:** 2026-09-26 EDT · DEMO_ONLY

Keel is a **Regime-B observe → score → recommend → REFERENCE_ONLY draft** loop for an **operator Morpho V1 wstETH–WETH sleeve** (self-run; not a hosted vault).

It is **not**: a custodian, signer, yield optimizer, curator dashboard, multi-user vault, or “safe autonomous allocator.”

## Success

- `IDLE_ALL` with Regime-B-eligible = **0** is **success**, not a bug.
- Agent **never** signs, never loads private keys, never auto-ALLOW, never invents ACTION or VAULT_ADDRESS.
- Capital risk = protocol risk + human paste quality + founder attention.

## Mandate as capital policy

Regime B (LLTV ≤ 0.86 WAD, wstETH-only) may leave **all** observed markets ineligible. Choosing stay-IDLE forever vs a pasted B2 amendment that loosens filters is a **capital policy** decision — not an observe defect. Do not “fix” eligible=0 with poison ALLOW or busywork observes.

## Kill list (attention)

Client kits, Soft-WTP, multi-user vault, grants packaging, unattended outreach, `targets.csv` as ops — **killed** (not part of the public OSS toolkit). Not on the observe skim.
