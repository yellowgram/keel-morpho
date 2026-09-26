# Keel — RACI (operator book)

**Date:** 2026-09-26 EDT

Self-run toolkit: **you** are the operator. There is no hosted multi-user vault.

| Lever / task | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Paste ALLOW rows | Operator | Operator | — | Agent (reads allowlist) |
| Paste ACTION line | Operator | Operator | — | Agent (logs PENDING only) |
| Any signature / broadcast | Operator | Operator | — | — |
| B2+ amendments | Operator | Operator | — | Agent |
| Set VAULT_ADDRESS | Operator | Operator | — | Agent |
| Flip DEMO_ONLY | Operator (tick-sheet) | Operator | — | Agent |
| Clear KILL | Operator **only** | Operator | — | Agent |
| Set KILL on EXIT-class (open size) | Agent may set | Operator | — | Operator skim |
| Run observe / emit pack+log | Agent | Operator | — | Operator |
| Raise size caps | Operator via amendment | Operator | — | Agent **never raises** |
| Pay RPC / rotate keys | Operator | Operator | — | — |
| Custody / Safe / signer hardware | Operator | Operator | — | — (never in observe host) |

Agent **must not** “helpfully” paste ALLOW, ACTION, vault, or clear KILL.
