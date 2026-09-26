# Keel eth-credit-conservative LOG


### LOG | 2026-09-22T12:13:31Z
mandate_hash: aef34504f37abc904cadc1678c376221e027e916a94f9786605b238ff0c08855
demo_only: true
regime: B
fetch: {graphql_ok: False, llama_ok: True, rpc_ok: false, data_age_s_max: 0}
watch_n: 0
eligible:
  []
ineligible_n: 0
ref_idle_pct: 100
ref_alloc: []
encoded: {E1..E8: Morpho V1, wstETH only, cap 25%, lltv<=86e16, no risk-up w/o ALLOW, risk-down ok, no auto-dealloc forced, LRT EXIT}
operating: {O1..O7 applied on util/borrower; O3/O4 deferred (rpc_ok=false, stETH/ETH=1 assumption pending)}
confidence: LOW
exceptions: [{"limit": "DATA_GAP", "level": "HALT", "evidence": "HALT_FETCH:HTTP Error 400: Bad Request", "number": null}]
recommendation: HOLD
rationale: No ALLOW rows at t0 → IDLE_ALL. Eligible set scored; many may WARN/EXIT on O1/O2 — expected. Never allocate without ALLOW ∩ PASS.
draft_actions: [{fn: none, note: REFERENCE_ONLY idle, reference_only: true}]
action_human: PENDING
tx_hash: none
aftermath_24h:
aftermath_7d:
decision_quality: {false_alarm: null, missed_alarm: null, followed: null}
drill: {"label": "DRILL", "procedure": "P_WSTETH", "paper_apply": "If wst_dev EXIT: freeze new; EXIT open allocations; IDLE until O4 PASS", "book_effect": "REFERENCE 100 \u2192 IDLE_ALL (already idle)", "result": "PASS_DRILL \u2014 no allocated rows; idle unchanged"}
counts: weth=0 wsteth=0 eligible=0 pass=0 warn=0 exit=0


### LOG | 2026-09-22T12:14:23Z
mandate_hash: aef34504f37abc904cadc1678c376221e027e916a94f9786605b238ff0c08855
demo_only: true
regime: B
fetch: {graphql_ok: True, llama_ok: True, rpc_ok: false, data_age_s_max: 0}
watch_n: 97
eligible:
  []
ineligible_n: 5
ref_idle_pct: 100
ref_alloc: []
encoded: {E1..E8: Morpho V1, wstETH only, cap 25%, lltv<=86e16, no risk-up w/o ALLOW, risk-down ok, no auto-dealloc forced, LRT EXIT}
operating: {O1..O7 applied on util/borrower; O3/O4 deferred (rpc_ok=false, stETH/ETH=1 assumption pending)}
confidence: HIGH
exceptions: []
recommendation: IDLE_ALL
rationale: No ALLOW rows at t0 → IDLE_ALL. Eligible set scored; many may WARN/EXIT on O1/O2 — expected. Never allocate without ALLOW ∩ PASS.
draft_actions: [{fn: none, note: REFERENCE_ONLY idle, reference_only: true}]
action_human: PENDING
tx_hash: none
aftermath_24h:
aftermath_7d:
decision_quality: {false_alarm: null, missed_alarm: null, followed: null}
drill: {"label": "DRILL", "procedure": "P_WSTETH", "paper_apply": "If wst_dev EXIT: freeze new; EXIT open allocations; IDLE until O4 PASS", "book_effect": "REFERENCE 100 \u2192 IDLE_ALL (already idle)", "result": "PASS_DRILL \u2014 no allocated rows; idle unchanged"}
counts: weth=97 wsteth=5 eligible=0 pass=0 warn=0 exit=0


### LOG | 2026-09-22T12:15:02Z (2026-09-22 08:15 EDT)
mandate_hash: aef34504f37abc904cadc1678c376221e027e916a94f9786605b238ff0c08855
demo_only: true
regime: B
cycle: DEMO_ONLY pre-execution observe (first successful GraphQL)
fetch: {graphql_ok: true, llama_ok: true, rpc_ok: true, rpc_provider: ethereum.publicnode.com, data_age_s_llama: 142}
watch_n: 5
weth_loan_markets: 97
eligible_regime_B: []
ineligible_n: 5
ineligible_why: all wstETH–WETH markets lltv in {94.5%, 96.5%} > FORBIDDEN_LLTV_WAD_MIN_EXCLUSIVE_B (86e16)
prices: {weth_usd: 2743.161328, wsteth_usd: 3412.941940, steth_usd: 2741.368155, wsteth_weth: 1.24416377, steth_weth: 0.99934631, stEthPerToken: 1.2445580676, block: 26032958}
scoreboard: PARTIAL/INCOMPLETE (BRIEF_v1.1.md missing); util flags on observed markets only; oracle/wst secondary PARTIAL
ref_idle_pct: 100
ref_alloc: []
recommendation: IDLE_ALL
rationale: null vault + empty allowlist + DEMO_ONLY + zero Regime-B-eligible markets → IDLE is success. Never ALLOCATE. Never invent ALLOW.
draft_actions: [{fn: none, note: REFERENCE_ONLY idle — no deallocate needed, reference_only: true}]
action_human: PENDING
tx_hash: none
blockers: [BRIEF_v1.1.md missing, VAULT_ADDRESS null, allowlist empty, RegimeB_eligible=0]
drill: PASS_DRILL P_WSTETH — already idle
counts: weth=97 wsteth=5 eligible=0 pass=0 warn=0 exit=0

### LOG | 2026-09-22T12:19:42Z
mandate_hash: aef34504f37abc904cadc1678c376221e027e916a94f9786605b238ff0c08855
demo_only: true
regime: B
fetch: {graphql_ok: True, llama_ok: True, rpc_ok: false, data_age_s_max: 0}
watch_n: 97
eligible:
  []
ineligible_n: 5
ref_idle_pct: 100
ref_alloc: []
encoded: {E1..E8: Morpho V1, wstETH only, cap 25%, lltv<=86e16, no risk-up w/o ALLOW, risk-down ok, no auto-dealloc forced, LRT EXIT}
operating: {O1..O7 applied on util/borrower; O3/O4 deferred (rpc_ok=false, stETH/ETH=1 assumption pending)}
confidence: HIGH
exceptions: []
recommendation: IDLE_ALL
rationale: No ALLOW rows at t0 → IDLE_ALL. Eligible set scored; many may WARN/EXIT on O1/O2 — expected. Never allocate without ALLOW ∩ PASS.
draft_actions: [{fn: none, note: REFERENCE_ONLY idle, reference_only: true}]
action_human: PENDING
tx_hash: none
aftermath_24h:
aftermath_7d:
decision_quality: {false_alarm: null, missed_alarm: null, followed: null}
drill: {"label": "DRILL", "procedure": "P_WSTETH", "paper_apply": "If wst_dev EXIT: freeze new; EXIT open allocations; IDLE until O4 PASS", "book_effect": "REFERENCE 100 \u2192 IDLE_ALL (already idle)", "result": "PASS_DRILL \u2014 no allocated rows; idle unchanged"}
counts: weth=97 wsteth=5 eligible=0 pass=0 warn=0 exit=0



### LOG | 2026-09-22T12:20:17Z (2026-09-22 08:20 EDT)
mandate_hash: aef34504f37abc904cadc1678c376221e027e916a94f9786605b238ff0c08855
demo_only: true
regime: B
brief: BRIEF_v1.1.md present
fetch: {graphql_ok: true, llama_ok: true}
wsteth_weth_markets: 5
eligible_regime_B: []
ineligible: [{"marketId": "0xb8fc70e82bc5bb53e773626fcc6a23f7eefa036918d7ef216ecfb1950a94a85e", "lltv": 965000000000000000, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0xd0e50cdac92fe2172043f5e0c36532c6369d24947e40968f34a5e8819ca9ec5d", "lltv": 945000000000000000, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0xc54d7acf14de29e0e5527cabd7a576506870346a78a11a6762e2cca66322ec41", "lltv": 945000000000000000, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0x04951431341b022886954b9d99310ac2f738eb69fe5b4408042f0b505c9ef302", "lltv": 945000000000000000, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0x27dc2546042d49c948772a38432849a60fdb41f26af32fac42336f2278591296", "lltv": 965000000000000000, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}]
recommendation: IDLE_ALL
rationale: standing orders — idle unless B2; vault null; allow empty; eligible=0
action_human: PENDING
tx_hash: none

### LOG | 2026-09-22T13:01:49Z (2026-09-22 09:01 EDT)
mandate_hash: aef34504f37abc904cadc1678c376221e027e916a94f9786605b238ff0c08855
demo_only: true
regime: B
brief: BRIEF_v1.1.md present
fetch: {graphql_ok: true, llama_ok: true, rpc_ok: false, rpc_provider: None, data_age_s_llama: 129}
fetch_errors: ["rpc:HTTP Error 403: Forbidden"]
weth_loan_markets: 97
wsteth_weth_markets: 5
eligible_regime_B: []
ineligible_n: 5
ineligible: [{"marketId": "0xb8fc70e82bc5bb53e773626fcc6a23f7eefa036918d7ef216ecfb1950a94a85e", "lltv": 965000000000000000, "lltv_pct": 96.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0xd0e50cdac92fe2172043f5e0c36532c6369d24947e40968f34a5e8819ca9ec5d", "lltv": 945000000000000000, "lltv_pct": 94.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0xc54d7acf14de29e0e5527cabd7a576506870346a78a11a6762e2cca66322ec41", "lltv": 945000000000000000, "lltv_pct": 94.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0x04951431341b022886954b9d99310ac2f738eb69fe5b4408042f0b505c9ef302", "lltv": 945000000000000000, "lltv_pct": 94.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0x27dc2546042d49c948772a38432849a60fdb41f26af32fac42336f2278591296", "lltv": 965000000000000000, "lltv_pct": 96.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}]
prices: {weth_usd: 2752.7386263403337, wsteth_usd: 3424.9470866539027, steth_usd: 2748.2687100076514, wsteth_weth: 1.244196253825684, steth_weth: 0.9983761929701895, stEthPerToken: None, block: None}
scoreboard: PARTIAL (O1 borrower schema often unavailable; O3 oracle secondary deferred; O5/O7 N/A while idle); util flags applied
ref_idle_pct: 100
ref_alloc: []
recommendation: IDLE_ALL
rationale: VAULT null + ALLOW empty + no B2 amendment + Regime-B-eligible=0. IDLE is success. Never ALLOCATE without ALLOW ∩ PASS.
draft_actions: [{fn: none, note: REFERENCE_ONLY idle — no deallocate needed, reference_only: true}]
action_human: PENDING
tx_hash: none
blockers: [VAULT_ADDRESS null, allowlist empty, RegimeB_eligible=0, no B2 amendment]
drill: PASS_DRILL P_WSTETH — already idle
counts: weth=97 wsteth=5 eligible=0 pass=0 warn=0 exit=0

### LOG | 2026-09-23T12:24:36Z (2026-09-23 08:24 EDT)
mandate_hash: aef34504f37abc904cadc1678c376221e027e916a94f9786605b238ff0c08855
demo_only: true
regime: B
brief: BRIEF_v1.1.md present
fetch: {graphql_ok: true, llama_ok: true, rpc_ok: false, rpc_provider: None, data_age_s_llama: 116}
fetch_errors: ["rpc:HTTP Error 403: Forbidden"]
weth_loan_markets: 97
wsteth_weth_markets: 5
eligible_regime_B: []
ineligible_n: 5
ineligible: [{"marketId": "0xb8fc70e82bc5bb53e773626fcc6a23f7eefa036918d7ef216ecfb1950a94a85e", "lltv": 965000000000000000, "lltv_pct": 96.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0xd0e50cdac92fe2172043f5e0c36532c6369d24947e40968f34a5e8819ca9ec5d", "lltv": 945000000000000000, "lltv_pct": 94.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0xc54d7acf14de29e0e5527cabd7a576506870346a78a11a6762e2cca66322ec41", "lltv": 945000000000000000, "lltv_pct": 94.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0x04951431341b022886954b9d99310ac2f738eb69fe5b4408042f0b505c9ef302", "lltv": 945000000000000000, "lltv_pct": 94.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0x27dc2546042d49c948772a38432849a60fdb41f26af32fac42336f2278591296", "lltv": 965000000000000000, "lltv_pct": 96.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}]
prices: {weth_usd: 2717.6418772562656, wsteth_usd: 3379.808185799951, steth_usd: 2721.934027602655, wsteth_weth: 1.2436547339387518, steth_weth: 1.0015793656928493, stEthPerToken: None, block: None}
scoreboard: PARTIAL (O1 borrower schema often unavailable; O3 oracle secondary deferred; O5/O7 N/A while idle); util flags applied
ref_idle_pct: 100
ref_alloc: []
recommendation: IDLE_ALL
rationale: VAULT null + ALLOW empty + no B2 amendment + Regime-B-eligible=0. IDLE is success. Never ALLOCATE without ALLOW ∩ PASS.
draft_actions: [{fn: none, note: REFERENCE_ONLY idle — no deallocate needed, reference_only: true}]
action_human: PENDING
tx_hash: none
blockers: [VAULT_ADDRESS null, allowlist empty, RegimeB_eligible=0, no B2 amendment]
drill: PASS_DRILL P_WSTETH — already idle
counts: weth=97 wsteth=5 eligible=0 pass=0 warn=0 exit=0

### LOG | 2026-09-24T12:19:59Z (2026-09-24 08:19 EDT)
mandate_hash: aef34504f37abc904cadc1678c376221e027e916a94f9786605b238ff0c08855
demo_only: true
regime: B
brief: BRIEF_v1.1.md present
fetch: {graphql_ok: true, llama_ok: true, rpc_ok: false, rpc_provider: None, data_age_s_llama: 69}
fetch_errors: ["rpc:HTTP Error 403: Forbidden"]
weth_loan_markets: 97
wsteth_weth_markets: 5
eligible_regime_B: []
ineligible_n: 5
ineligible: [{"marketId": "0xb8fc70e82bc5bb53e773626fcc6a23f7eefa036918d7ef216ecfb1950a94a85e", "lltv": 965000000000000000, "lltv_pct": 96.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0xd0e50cdac92fe2172043f5e0c36532c6369d24947e40968f34a5e8819ca9ec5d", "lltv": 945000000000000000, "lltv_pct": 94.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0xc54d7acf14de29e0e5527cabd7a576506870346a78a11a6762e2cca66322ec41", "lltv": 945000000000000000, "lltv_pct": 94.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0x04951431341b022886954b9d99310ac2f738eb69fe5b4408042f0b505c9ef302", "lltv": 945000000000000000, "lltv_pct": 94.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0x27dc2546042d49c948772a38432849a60fdb41f26af32fac42336f2278591296", "lltv": 965000000000000000, "lltv_pct": 96.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}]
prices: {weth_usd: 2647.563275870474, wsteth_usd: 3293.881508510405, steth_usd: 2646.5354510594943, wsteth_weth: 1.2441181438534015, steth_weth: 0.9996117846095135, stEthPerToken: None, block: None}
scoreboard: PARTIAL (O1 borrower schema often unavailable; O3 oracle secondary deferred; O5/O7 N/A while idle); util flags applied
ref_idle_pct: 100
ref_alloc: []
recommendation: IDLE_ALL
rationale: VAULT null + ALLOW empty + no B2 amendment + Regime-B-eligible=0. IDLE is success. Never ALLOCATE without ALLOW ∩ PASS.
draft_actions: [{fn: none, note: REFERENCE_ONLY idle — no deallocate needed, reference_only: true}]
action_human: PENDING
tx_hash: none
blockers: [VAULT_ADDRESS null, allowlist empty, RegimeB_eligible=0, no B2 amendment]
drill: PASS_DRILL P_WSTETH — already idle
counts: weth=97 wsteth=5 eligible=0 pass=0 warn=0 exit=0

### LOG | 2026-09-25T12:12:31Z (2026-09-25 08:12 EDT)
mandate_hash: aef34504f37abc904cadc1678c376221e027e916a94f9786605b238ff0c08855
demo_only: true
regime: B
brief: BRIEF_v1.1.md present
fetch: {graphql_ok: true, llama_ok: true, rpc_ok: false, rpc_provider: None, data_age_s_llama: 111}
fetch_errors: ["rpc:HTTP Error 403: Forbidden"]
weth_loan_markets: 97
wsteth_weth_markets: 5
eligible_regime_B: []
ineligible_n: 5
ineligible: [{"marketId": "0xb8fc70e82bc5bb53e773626fcc6a23f7eefa036918d7ef216ecfb1950a94a85e", "lltv": 965000000000000000, "lltv_pct": 96.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0xd0e50cdac92fe2172043f5e0c36532c6369d24947e40968f34a5e8819ca9ec5d", "lltv": 945000000000000000, "lltv_pct": 94.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0xc54d7acf14de29e0e5527cabd7a576506870346a78a11a6762e2cca66322ec41", "lltv": 945000000000000000, "lltv_pct": 94.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0x04951431341b022886954b9d99310ac2f738eb69fe5b4408042f0b505c9ef302", "lltv": 945000000000000000, "lltv_pct": 94.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0x27dc2546042d49c948772a38432849a60fdb41f26af32fac42336f2278591296", "lltv": 965000000000000000, "lltv_pct": 96.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}]
prices: {weth_usd: 2722.5198445022174, wsteth_usd: 3385.4041788191053, steth_usd: 2717.8568100673683, wsteth_weth: 1.2434819109419895, steth_weth: 0.9982872358325448, stEthPerToken: None, block: None}
scoreboard: PARTIAL (O1 borrower schema often unavailable; O3 oracle secondary deferred; O5/O7 N/A while idle); util flags applied
ref_idle_pct: 100
ref_alloc: []
recommendation: IDLE_ALL
rationale: VAULT null + ALLOW empty + no B2 amendment + Regime-B-eligible=0. IDLE is success. Never ALLOCATE without ALLOW ∩ PASS.
draft_actions: [{fn: none, note: REFERENCE_ONLY idle — no deallocate needed, reference_only: true}]
action_human: PENDING
tx_hash: none
blockers: [VAULT_ADDRESS null, allowlist empty, RegimeB_eligible=0, no B2 amendment]
drill: PASS_DRILL P_WSTETH — already idle
counts: weth=97 wsteth=5 eligible=0 pass=0 warn=0 exit=0

### LOG | 2026-09-26T13:20:14Z (2026-09-26 09:20 EDT)
mandate_hash: aef34504f37abc904cadc1678c376221e027e916a94f9786605b238ff0c08855
demo_only: true
kill: false
regime: B
brief: BRIEF_v1.1.md present
five_way: ALLOW=N ∩ PASS=N ∩ VAULT=N ∩ NOT_DEMO=N ∩ NOT_KILL=Y | failed=['ALLOW', 'PASS', 'VAULT', 'NOT_DEMO']
quiet_fp: IDLE_ALL::DEMO_ONLY=true|VAULT_ADDRESS null|ALLOW empty/rejected|RegimeB_eligible=0|no market PASS score::
missed_observe: none
fetch: {graphql_ok: true, llama_ok: true, rpc_ok: false, rpc_provider: None, data_age_s_llama: 94}
fetch_errors: ["rpc:HTTP Error 403: Forbidden"]
weth_loan_markets: 97
wsteth_weth_markets: 5
eligible_regime_B: []
ineligible_n: 5
ineligible: [{"marketId": "0xb8fc70e82bc5bb53e773626fcc6a23f7eefa036918d7ef216ecfb1950a94a85e", "lltv": 965000000000000000, "lltv_pct": 96.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0xd0e50cdac92fe2172043f5e0c36532c6369d24947e40968f34a5e8819ca9ec5d", "lltv": 945000000000000000, "lltv_pct": 94.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0xc54d7acf14de29e0e5527cabd7a576506870346a78a11a6762e2cca66322ec41", "lltv": 945000000000000000, "lltv_pct": 94.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0x04951431341b022886954b9d99310ac2f738eb69fe5b4408042f0b505c9ef302", "lltv": 945000000000000000, "lltv_pct": 94.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}, {"marketId": "0x27dc2546042d49c948772a38432849a60fdb41f26af32fac42336f2278591296", "lltv": 965000000000000000, "lltv_pct": 96.5, "reason": "lltv>860000000000000000 (Regime B max 86%); forbidden_lltv_bucket"}]
allow_accepted: 0
allow_rejected: []
prices: {weth_usd: 2686.3241478392224, wsteth_usd: 3345.628711553848, steth_usd: 2687.171115367994, wsteth_weth: 1.245430010464279, steth_weth: 1.0003152886554858, stEthPerToken: None, block: None}
scoreboard: O1–O7 as pack; STALE_S=900 → O6_FAIL blocks PASS
ref_idle_pct: 100
ref_alloc: []
recommendation: IDLE_ALL
rationale: Five-way blocked (ALLOW=N ∩ PASS=N ∩ VAULT=N ∩ NOT_DEMO=N ∩ NOT_KILL=Y | failed=['ALLOW', 'PASS', 'VAULT', 'NOT_DEMO']); RegimeB_eligible=0. IDLE is success. Never ALLOCATE without ALLOW ∩ PASS ∩ VAULT ∩ !DEMO ∩ !KILL.
draft_actions: [{fn: none, note: REFERENCE_ONLY — ALLOCATE frozen under DEMO/KILL, reference_only: true}]
action_human: PENDING
tx_hash: none
blockers: ["DEMO_ONLY=true", "VAULT_ADDRESS null", "ALLOW empty/rejected", "RegimeB_eligible=0", "no market PASS score"]
drill: SKIP_IDLE
counts: weth=97 wsteth=5 eligible=0 pass=0 allow_ok=0
warnings: []
