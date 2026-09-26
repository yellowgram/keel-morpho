# ALLOCATOR PACK | 2026-09-26T13:20:14Z (2026-09-26 09:20 EDT)
STATUS: AMBER — BRIEF_v1.1.md present; DEMO_ONLY=true; KILL=false
MANDATE: ETH Credit Conservative | Regime B | `aef34504f37abc904cadc1678c376221e027e916a94f9786605b238ff0c08855`
DEMO_ONLY: true | KILL: false | Never sign | Never keys | Never auto-ALLOW | Never invent ACTION | Never price BMNR/BMNU/CoinDCX

## Book / vault
- REFERENCE_BOOK_ID: `eth-credit-conservative-ref-001` | REFERENCE_UNITS: 100 | open_size_weth: 0.0 | idle_pct: **100**
- VAULT_ADDRESS: **null** | ALLOW accepted: **0** | ALLOW rejected: **0** | AMENDMENTS: none | B2: none
- BRIEF_v1.1.md: **present** | REGIME: **B** locked | size_caps: BOOK=None PER_MKT=None MAX_OPEN=None DUST=None
- five_way_AND: `ALLOW=N ∩ PASS=N ∩ VAULT=N ∩ NOT_DEMO=N ∩ NOT_KILL=Y | failed=['ALLOW', 'PASS', 'VAULT', 'NOT_DEMO']`
- drill: **SKIP_IDLE** (P_WSTETH path) | quiet_if_IDLE: False | missed_observe: none

## Prices (Llama + optional RPC)
| WETH | wstETH | stETH | wstETH/WETH | stETH/WETH | stEthPerToken (RPC) | block |
|---:|---:|---:|---:|---:|---:|---:|
| 2686.3241 | 3345.6287 | 2687.1711 | 1.24543001 | 1.00031529 | — | — |

- Llama age_s: 94 | RPC provider: —
- fetch: graphql_ok=True llama_ok=True rpc_ok=False
- fetch_errors: ['rpc:HTTP Error 403: Forbidden']

## All wstETH–WETH markets (mandatory table)
| marketId (Morpho uniqueKey) | lltv (wad) | lltv% | RegimeB eligible | ineligible_reason | util | supplyApy% | supplyUsd | oracle |
|---|---:|---:|:---:|---|---:|---:|---:|---|
| `0xb8fc70e82bc5bb53e773626fcc6a23f7eefa036918d7ef216ecfb1950a94a85e` | 965000000000000000 | 96.50 | NO | lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket | 0.9039 | 1.949 | 96,541,413 | `0xbD60A6770b27E084E8617335ddE769241B0e71D8` |
| `0xd0e50cdac92fe2172043f5e0c36532c6369d24947e40968f34a5e8819ca9ec5d` | 945000000000000000 | 94.50 | NO | lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket | 0.8920 | 1.629 | 32,962,956 | `0xbD60A6770b27E084E8617335ddE769241B0e71D8` |
| `0xc54d7acf14de29e0e5527cabd7a576506870346a78a11a6762e2cca66322ec41` | 945000000000000000 | 94.50 | NO | lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket | 0.8970 | 1.645 | 42,131 | `0x2a01EB9496094dA03c4E364Def50f5aD1280AD72` |
| `0x04951431341b022886954b9d99310ac2f738eb69fe5b4408042f0b505c9ef302` | 945000000000000000 | 94.50 | NO | lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket | 0.8567 | 1.336 | 5 | `0xcBd5323D71a3424A7e0Fd11c367565bad3838867` |
| `0x27dc2546042d49c948772a38432849a60fdb41f26af32fac42336f2278591296` | 965000000000000000 | 96.50 | NO | lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket | 0.0000 | 0.000 | 0 | `0x3A7bB36Ee3f3eE32A60e9f2b33c1e5f2E83ad766` |

**Counts:** WETH_loan_markets=97 | wstETH–WETH=5 | RegimeB_eligible=0 | ALLOW_accepted=0 | ALLOW_rejected=0 | countTotal=97
ALLOW_rejected_detail: none

## Scoreboard O1–O7 (PARTIAL where data missing)
| marketId | flags | top_borrower_pct |
|---|---|---:|
| `0xb8fc70e82bc5bb53…` | O2_WARN; O1_PARTIAL; O3_PARTIAL; O4_PARTIAL; O5_N/A; O6_PASS(age=879s); O7_N/A | — |
| `0xd0e50cdac92fe217…` | O2_WARN; O1_PARTIAL; O3_PARTIAL; O4_PARTIAL; O5_N/A; O6_PASS(age=867s); O7_N/A | — |
| `0xc54d7acf14de29e0…` | O2_WARN; O1_PARTIAL; O3_PARTIAL; O4_PARTIAL; O5_N/A; O6_PASS(age=879s); O7_N/A | — |
| `0x04951431341b0228…` | O2_WARN; O1_PARTIAL; O3_PARTIAL; O4_PARTIAL; O5_N/A; O6_FAIL(age=915s>900); O7_N/A | — |
| `0x27dc2546042d49c9…` | O2_PASS; O1_PARTIAL; O3_PARTIAL; O4_PARTIAL; O5_N/A; O6_FAIL(age=915s>900); O7_N/A | — |

Score aggregate: ALLOCATE only if five-way AND (ALLOW ∩ PASS ∩ VAULT ∩ !DEMO_ONLY ∩ !KILL). O6 age>STALE_S → FAIL. Flag **PARTIAL** on O1/O3/O4 as needed; O5/O7 N/A while idle.

## Recommendation
# **IDLE_ALL**
Rationale: Five-way blocked (ALLOW=N ∩ PASS=N ∩ VAULT=N ∩ NOT_DEMO=N ∩ NOT_KILL=Y | failed=['ALLOW', 'PASS', 'VAULT', 'NOT_DEMO']); RegimeB_eligible=0. IDLE is success. Never ALLOCATE without ALLOW ∩ PASS ∩ VAULT ∩ !DEMO ∩ !KILL.
ACTION: human-only — observe refuses invent (`action_human: PENDING`). REFERENCE_ONLY deallocate drafts only; ALLOCATE drafts frozen while DEMO or KILL.

## Blockers
1. DEMO_ONLY=true
2. VAULT_ADDRESS null
3. ALLOW empty/rejected
4. RegimeB_eligible=0
5. no market PASS score

## Next human actions
- Paste B2 amendment only if Regime B / idle default should change
- Paste ALLOW rows (format in allowlist.md) when a ≤86% LLTV Regime-B-eligible market exists
- Set VAULT_ADDRESS only after control proven; flip DEMO only via live-exit tick-sheet (`ops/LIVE_EXIT_GATE_TICKSHEET.md`)
- Clear KILL only as human (agent may set on EXIT-class with open size)

## Schedule
Weekday observe 08:00 America/New_York (`keel_daily_observe_once.sh`). Quiet-if-IDLE when rec+blockers+eligible unchanged. SLA: `ops/SLAS.md`.
