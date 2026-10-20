# Keel report — 2026-10-19T14:00:00Z (2026-10-19 10:00 EDT)

## Recommendation: IDLE_ALL

1 market(s) meet the filters and pass every check, but: DEMO_ONLY is true; VAULT_ADDRESS is not set.

Keel does not sign or move funds. Any transaction is yours to make.

### Blockers
- DEMO_ONLY is true
- VAULT_ADDRESS is not set

## Markets (WETH loans against wstETH, Ethereum mainnet)

| Market | LLTV | Eligible | Ready | Utilization | Supply APY | Supply |
|---|---:|:---:|:---:|---:|---:|---:|
| `0xcccccccc…` | 94.5% | no | no | 88.0% | 1.6% | $95,800,000 |
| `0xaaaaaaaa…` | 86.0% | yes | yes | 62.0% | 2.1% | $28,700,000 |
| `0xbbbbbbbb…` | 86.0% | no | no | 40.0% | 3.5% | $7,100,000 |

### `0xcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc`

Not eligible: LLTV 94.5% is above 86.0%.

| Check | Result | Detail |
|---|---|---|
| top_borrower | EXIT | 25.6% > exit 15.0% |
| utilization | WARN | 88.0% > warn 80.0% |
| oracle_deviation | PASS | oracle 1.24650 vs market 1.24511 WETH/wstETH: 11 bps |
| wsteth_rate | PASS | market 1.24709 vs on-chain 1.24670 stETH/wstETH: 3 bps |
| exit_liquidity | PASS | 4,800.0 WETH idle, need 4,000.0 |
| freshness | PASS | prices 300s old (limit 2100s) |

### `0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`

| Check | Result | Detail |
|---|---|---|
| top_borrower | PASS | 7.0% |
| utilization | PASS | 62.0% |
| oracle_deviation | PASS | oracle 1.24670 vs market 1.24511 WETH/wstETH: 13 bps |
| wsteth_rate | PASS | market 1.24709 vs on-chain 1.24670 stETH/wstETH: 3 bps |
| exit_liquidity | PASS | 4,560.0 WETH idle, need 1,200.0 |
| freshness | PASS | prices 300s old (limit 2100s) |

### `0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`

Not eligible: collateral wstETH at 0xdededededededededededededededededededede is not the wstETH contract.

| Check | Result | Detail |
|---|---|---|
| top_borrower | PASS | 8.3% |
| utilization | PASS | 40.0% |
| oracle_deviation | PASS | oracle 1.24670 vs market 1.24511 WETH/wstETH: 13 bps |
| wsteth_rate | PASS | market 1.24709 vs on-chain 1.24670 stETH/wstETH: 3 bps |
| exit_liquidity | PASS | 1,800.0 WETH idle, need 300.0 |
| freshness | PASS | prices 300s old (limit 2100s) |

## Inputs

- Prices (DefiLlama): wstETH $2,982, WETH $2,395, stETH $2,391
- stETH per wstETH (on-chain): 1.246696
- DEMO_ONLY: true · KILL: false · VAULT_ADDRESS: not set · OPEN_SIZE_WETH: 0.0
- Allowlist: 1 accepted, 1 rejected
  - rejected `ALLOW \| 2026-10-19 \| 0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`: market is not eligible: collateral wstETH at 0xdededededededededededededededededededede is not the wstETH contract
- Policy fingerprint: `a142f4953aa0447aaecb4ed52248bd86b91cb4a4561a3ec95b22c01524319dbb`
