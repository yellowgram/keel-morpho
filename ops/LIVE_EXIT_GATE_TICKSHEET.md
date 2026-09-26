# Keel — Live-exit gate tick-sheet (FOUNDER-OWNED)

**Date:** 2026-09-26 EDT  
**Purpose:** Before flipping `DEMO_ONLY → false`, human ticks **all** items. Missing any → **stay DEMO**.  
**Agent does not** set vault, pay RPC, run custody drills, or invent ALLOW.

| # | Gate item | Tick | Date / note |
|---|---|---|---|
| a | `VAULT_ADDRESS` set by human after **control proven** (can sign for address / allocator roles) | ☐ | |
| b | ≥1 ALLOW row pasted for a market that is Regime-B-eligible **in the current pack** (paste-check accepted) | ☐ | |
| c | O1–O7 not systematically PARTIAL on markets you will touch | ☐ | |
| d | RPC health green for **3 consecutive weekday** observes (authenticated provider wired & paid) | ☐ | |
| e | Kill-switch / P_WSTETH: paper drill once + zero-size dry-run vs intended vault (**zero size**) | ☐ | |
| f | Size rules written in config (`BOOK_*`, `PER_MARKET_*`, `MAX_MARKETS_OPEN`, `DUST_*`) and re-hashed / amendment recorded | ☐ | |
| g | Pre-sign sim tooling chosen (Tenderly / Safe sim / explorer) — founder-owned | ☐ | |
| h | Mental model + RACI accepted; kits/targets stay killed | ☐ | |

**After flip:** dust allocate → full exit cycle in `log.md` before any size-up amendment.  
**Rollback:** human may re-set `DEMO_ONLY=true`; open live size ⇒ pack must show **INCONSISTENT — EXIT PRIORITY**.
