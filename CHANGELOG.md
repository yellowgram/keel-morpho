# Changelog

## 0.2.1 — 2026-10-20

### Changed

- `STALE_S` in `config.example.json` is now 2100 s (was 900 s). DefiLlama
  stores a wstETH/stETH price about every 1800 s (measured 1793–1813 s) and
  serves it 90–150 s later, so an on-schedule price is up to about 1,950 s old
  (1,901 s measured just before an update appeared). With 900 s, `freshness`
  WARNed on about half of all runs and a market could rarely become ready.
  2100 s is the cadence plus the publish lag plus about 150 s of jitter: an
  on-schedule run passes, and a missed update WARNs. It is a loosening: price
  cross-checks may now use a price up to 35 minutes old. This is a policy
  change: the example's policy fingerprint is now
  `a142f4953aa0447aaecb4ed52248bd86b91cb4a4561a3ec95b22c01524319dbb`
  (was `95af7dfc…`). An existing `config.json` keeps its own `STALE_S`; to adopt
  the new value, set it to 2100 and update `POLICY_SHA256`
  (`python3 -m keel fingerprint`).
- `examples/sample-pack.md` regenerated (freshness limit and fingerprint).

## 0.2.0 — 2026-10-19

First versioned release. The scripts were rebuilt as the `keel` package
(`python3 -m keel observe`); `scripts/keel_daily_observe_once.sh` still works.

### Changed

- Docs: `STALE_S` (900 s in the example) is below DefiLlama's measured wstETH/stETH
  update cadence (prices sampled 925–986 s old), so `freshness` usually WARNs.
  The threshold is unchanged; OPERATING explains when to raise it.
- `KEEL_NOT_SIGNING_KEYS=NAME[,NAME]` waives exact variable names from the
  signing-key refusal (for example a CI app key).

### Fixed

- Broken data could pass as good data: a NaN or negative utilization or oracle
  reading, a price timestamp in the future, an empty positions list on a market
  with borrows, or a missing LLTV. Each is now `UNKNOWN` (or ineligible, for LLTV),
  and zero or non-numeric prices no longer crash a run. A missing or broken
  `borrowAssets`, a negative or broken `supplyAssets`/`liquidityAssets`, and
  liquidity above supply are `UNKNOWN` too (NaN liquidity used to crash the run). So are borrow above
  supply (it used to pass every check and hide top-borrower concentration), a top position larger than
  the market's borrow, and amounts that are not plain ASCII digits (`"²"` used to crash the run; `"5 "` and
  other scripts' digits were accepted). A NaN policy value or a
  NaN, infinite or non-positive allowlist `cap_rel` is refused.
- A market whose collateral token was merely *named* wstETH could pass the
  collateral filter. Collateral and loan asset are now matched by contract
  address only.
- The top-borrower check never ran: its Morpho API query used a field that no
  longer exists. It now uses `marketPositions`.
- The wstETH rate check never ran: it called a function selector that reverts.
  It now calls `stEthPerToken()` (`0x035faf82`).
- `ALLOCATE_ELIGIBLE` could never be reached, because three checks were
  hard-coded as incomplete. All six checks now run on real data.
- The allocation gate accepted *any* market passing its checks, not
  necessarily one on your allowlist. The allowlisted market itself must now
  be ready.
- Automatic `KILL` fired on an `EXIT` in any market, including markets you
  were not in. It now watches only markets named in your allowlist.
- Market fetching stopped silently at 600 markets. It now pages through all
  of them and refuses (rather than truncates) beyond 1,000.
- The market-list query failed on every run and only a fallback query worked.
- Public RPC endpoints rejected requests with HTTP 403 because of the default
  Python User-Agent.
- Two tests depended on a local, git-ignored `config.json`.

### Changed

- Checks have names (`top_borrower`, `utilization`, `oracle_deviation`,
  `wsteth_rate`, `exit_liquidity`, `freshness`) instead of codes, and results
  are `PASS` / `WARN` / `EXIT` / `UNKNOWN`.
- `oracle_deviation` compares the market's own oracle with DefiLlama prices.
  `exit_liquidity` checks unborrowed WETH. `freshness` measures price age
  (previously the market's last-interaction time).
- The fixed "mandate hash" is replaced by a policy fingerprint over the actual
  thresholds; pin it with `POLICY_SHA256`.
- The config is validated: types, addresses, and warn ≤ exit.
  `FORBIDDEN_LLTV_WAD_MIN_EXCLUSIVE_B` is now `MAX_LLTV_WAD` (the old name
  still loads, with a warning). Unused keys were dropped.
- Reports go to `out/pack.md`, `out/latest.json` and `out/log.jsonl`.
  The allowlist moved to `allowlist.md` at the repository root.
- An allowlist line must also match the market's oracle.
- Offline mode: `--fixture` replays a snapshot; `examples/sample-pack.md` is
  generated from it and checked in CI.

### Removed

- Internal planning documents, run logs and the sample sleeve directory.
- `scripts/first_run.py`, `scripts/hard_daily_observe.py`,
  `scripts/keel_ops_gates.py`, and the `draft_actions` placeholder (it never
  contained a transaction).

### Migrating from the scripts

1. Move `eth-credit-conservative/allowlist.md` to `allowlist.md`.
2. Compare your `config.json` with `config.example.json`; unknown keys are ignored.
3. Run `python3 -m keel observe` and read `out/pack.md`.
