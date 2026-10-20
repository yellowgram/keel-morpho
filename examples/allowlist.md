# Allowlist

One line per market you have reviewed and are willing to lend into. Keel rejects
a line unless every field matches a market in today's report and that market
meets the filters.

Format: ALLOW | date | marketId | lltv_wad | collateral | oracle | cap_rel | why

ALLOW | 2026-10-19 | 0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 860000000000000000 | wstETH | 0xa1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1 | 0.25 | reviewed oracle and IRM
ALLOW | 2026-10-19 | 0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb | 860000000000000000 | wstETH | 0xb1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1 | 0.25 | higher APY
