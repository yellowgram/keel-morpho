# KEEL — ETH CREDIT CONSERVATIVE — BRIEF v1.1
Version: 1.1 | 2026-09-22 | DEMO_ONLY | PRE-EXECUTION
Mandate hash: aef34504f37abc904cadc1678c376221e027e916a94f9786605b238ff0c08855

## Standing orders (human, 2026-09-22)
- Keep **REGIME B**.
- **VAULT_ADDRESS** remains **none** until human sets it in config.
- **ALLOW** remains **empty** until human pastes ALLOW rows (never invent).
- Schedule **daily observe**.
- Each **PACK** must **table all** Morpho wstETH–WETH markets: `uniqueKey`/`marketId` + `lltv` + `ineligible_reason` (every row, including ineligible).
- Recommendation stays **IDLE_ALL** unless a human **B2 amendment** is pasted into chat / amendments.

## Bot scope
Observe, fetch (Morpho GraphQL + Llama + public RPC), score, recommend, draft REFERENCE_ONLY deallocate only, append `log.md`, emit `pack.md` under `eth-credit-conservative/`.
Never sign. Never hold keys. Never raise risk. Never auto-ALLOW. Never price BMNR / BMNU / CoinDCX.
Human owns ALLOW rows, ACTION line, any future signature.
First principle: **IDLE is success**; flat / no allocation OK.

## Config authority
Thresholds and addresses live in `config.json (copy from config.example.json)`. Do not loosen them without a human amendment.

### Regime B hard filters
- Collateral: wstETH only for this sleeve; FORBIDDEN_COLLATERAL includes weETH, rsETH, ezETH, cbETH, rETH, PT-*
- LLTV: forbidden if `lltv > FORBIDDEN_LLTV_WAD_MIN_EXCLUSIVE_B` (860000000000000000) — i.e. allowed only if `lltv ≤ 0.86` WAD
- MARKET_REL_CAP 0.25; no ALLOCATE without ALLOW ∩ PASS

### Operating thresholds (config)
- ORACLE_WARN_BPS 100 / ORACLE_EXIT_BPS 150; ORACLE_WARN_S 900 / ORACLE_EXIT_S 1800
- WST_WARN_BPS 80 / WST_EXIT_BPS 150
- UTIL_WARN 0.8 / UTIL_EXIT 0.92
- BORROWER_WARN 0.1 / BORROWER_EXIT 0.15
- STALE_S 900
- EXIT_LIQ_PCT 0.1; EXIT_LIQ_FLOOR_WETH 50
- MODELED_OUTFLOW_PCT 0.2 over MODELED_OUTFLOW_DAYS 2

### Encoded constraints E1–E8 (summary)
1. Morpho V1 only (chain 1)
2. wstETH collateral sleeve only (this book)
3. Relative market cap ≤ 25%
4. LLTV ≤ 86e16 (Regime B)
5. No risk-up without human ALLOW
6. Risk-down (REDUCE/EXIT/IDLE) OK without ALLOW
7. No auto-deallocate forced beyond DEMO REFERENCE_ONLY drafts
8. LRT / forbidden collateral → EXIT / ineligible

### Operating checks O1–O7 (summary; apply when data available)
1. Top borrower concentration vs BORROWER_WARN/EXIT
2. Utilization vs UTIL_WARN/EXIT
3. Oracle freshness / deviation vs ORACLE_* (Morpho market oracle + secondary)
4. wstETH rate / stEthPerToken vs Llama secondary (WST_*)
5. Liquidity vs EXIT_LIQ_* for any EXIT path
6. Staleness of market state vs STALE_S
7. Modeled outflow / liquidity resilience (MODELED_OUTFLOW_*)

Score aggregate: PASS / WARN / EXIT per market. Book action only from ALLOW ∩ PASS. Empty ALLOW → **IDLE_ALL**.

## Pack requirements (mandatory every run)
1. Timestamp (UTC + America/New_York label), mandate_hash, DEMO_ONLY, REGIME
2. Vault / allowlist / amendment status
3. Prices snapshot (Llama + optional RPC)
4. **Full table of ALL wstETH–WETH markets**: marketId/uniqueKey | lltv | RegimeB eligible? | ineligible_reason (or — if eligible) | util | key APYs | oracle
5. Scoreboard (flag PARTIAL if a check could not run)
6. Recommendation: IDLE_ALL by default; HOLD only on hard fetch halt if pack still emitted; never ALLOCATE without ALLOW ∩ PASS and VAULT
7. Blockers + next human actions
8. Append matching LOG entry

## Amendments
- Only human-pasted **B2** (or later) amendments may change IDLE_ALL default or Regime B filters.
- Record amendment text under config `AMENDMENTS` or in pack when pasted; do not invent.

## Drill
P_WSTETH (paper): If wst_dev EXIT → freeze new; EXIT open allocations; IDLE until O4 PASS.
