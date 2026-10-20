# Keel

Keel is a read-only checker for one decision: **should I lend WETH into a Morpho
market that takes wstETH as collateral, and which one?**

Once a day (or whenever you run it) Keel reads every WETH-loan / wstETH-collateral
market on [Morpho](https://morpho.org) on Ethereum mainnet, keeps only the ones
that meet conservative filters, runs six risk checks on each, compares the result
with the markets you have personally approved, and writes a short markdown report
with one recommendation.

Keel never holds a key, never signs, and never moves funds. You make every
transaction yourself.

It is normal for Keel to recommend holding everything idle. That means no market
met the safety filters. As of October 2026, every live wstETH/WETH market on
Morpho has a liquidation LTV of 94.5% or more, above the default 86% limit, so
the default policy recommends idle.

## Quickstart (five minutes, no network, no keys)

Requires Python 3.10 or newer. There are no third-party dependencies.

```bash
git clone https://github.com/yellowgram/keel-morpho && cd keel-morpho
cp config.example.json config.json

# 1. Offline demo on a saved snapshot:
python3 -m keel observe --fixture examples/fixture.json --allowlist examples/allowlist.md --out /tmp/keel-demo
cat /tmp/keel-demo/pack.md

# 2. Live run (Morpho API, DefiLlama prices, two public Ethereum RPCs):
python3 -m keel observe
cat out/pack.md

# 3. Tests:
python3 -m unittest
```

Keel refuses to start if any environment variable whose name looks like signing
material (`PRIVATE_KEY`, `MNEMONIC`, `SEED_PHRASE`, ...) is set. It never needs
one; unset it in the shell that runs Keel. If a matching name is not a wallet key
(for example a CI job's `GITHUB_APP_PRIVATE_KEY`), name it exactly in
`KEEL_NOT_SIGNING_KEYS=NAME[,NAME]`; there is no wildcard.

## What Keel does on each run

1. **Fetch.** All Morpho markets on the configured chain with WETH as the loan
   asset and the wstETH contract as collateral, filtered by token address on the
   server and again locally. The token symbol is never trusted.
2. **Filter.** A market is *eligible* only if the collateral is the wstETH
   contract, the loan asset is WETH, and its liquidation LTV is at most
   `MAX_LLTV_WAD` (default 86%).
3. **Check.** Every market gets six checks. Each is `PASS`, `WARN`, `EXIT`, or
   `UNKNOWN` (data missing). A market is *ready* only if it is eligible and all six
   are `PASS`; missing data never counts as a pass. Broken data is treated as
   missing: a NaN or negative reading, a missing or non-integer `borrowAssets`,
   `supplyAssets` or `liquidityAssets`, liquidity above supply, a zero or
   non-numeric price, a price timestamp more than 60 s in the future, or a market
   that reports borrows while the positions query returns none is `UNKNOWN`. A missing or invalid LLTV makes
   the market ineligible.

   | Check | What it measures | Default WARN / EXIT |
   |---|---|---|
   | `top_borrower` | Largest borrower's share of all borrowing (concentration) | above 10% / above 15% |
   | `utilization` | Borrowed ÷ supplied | above 80% / above 92% |
   | `oracle_deviation` | Market oracle's wstETH→WETH price vs DefiLlama spot prices | above 100 / 150 bps |
   | `wsteth_rate` | DefiLlama wstETH/stETH price vs the on-chain `stEthPerToken()` rate (depeg) | above 80 / 150 bps |
   | `exit_liquidity` | Unborrowed WETH vs max(10% of supply, 50 WETH): could you withdraw? | WARN only |
   | `freshness` | Age of the oldest price used | WARN above 900 s. DefiLlama's wstETH/stETH prices update about every 15–17 min, so this WARNs on most runs; see [OPERATING](docs/OPERATING.md) |

4. **Compare with your allowlist.** You list markets you have reviewed, one line
   each (format below). Keel rejects a line unless the market id, LLTV and oracle
   exactly match a market in today's data, the market is eligible, and
   `cap_rel` is within `MARKET_REL_CAP`. Rejections are listed in the report.
5. **Recommend.** Exactly one of:

   | Recommendation | When |
   |---|---|
   | `ALLOCATE_ELIGIBLE` | At least one allowlisted market is ready, `VAULT_ADDRESS` is set, `DEMO_ONLY` is false and `KILL` is false. The report lists those markets. |
   | `IDLE_ALL` | Anything else. The report says why (the blockers). |
   | `HOLD` | Market data could not be fetched. Change nothing until a run succeeds. |
   | `EXIT_PRIORITY` | `DEMO_ONLY` is true but `OPEN_SIZE_WETH` is above 0: the config and your real position disagree. |

6. **Write.** `out/pack.md` (the report), `out/latest.json` (the same data as
   JSON) and one line appended to `out/log.jsonl`. If weekdays were skipped since
   the last run, the report says so.

If any check is `EXIT` on a market named in your allowlist (accepted or
rejected) while `OPEN_SIZE_WETH` is above 0, Keel sets `KILL` to true in
`config.json`. Only you set it back. Markets you have not allowlisted do not
trigger it, so keep the line for any market you are in. `KEEL_KILL=1` in the environment
has the same effect for one run.

## Inputs

| Input | Where | Notes |
|---|---|---|
| Policy thresholds | `config.json` | See `config.example.json`. Warn values must not exceed exit values; Keel refuses a config that breaks this. |
| `DEMO_ONLY` | `config.json` | Default true. While true Keel never recommends allocating. |
| `VAULT_ADDRESS`, `OPEN_SIZE_WETH` | `config.json` | Your vault and current position. Keel only reads them. |
| `POLICY_SHA256` | `config.json` | Optional pin, see below. |
| Allowlist | `allowlist.md` | `ALLOW \| date \| marketId \| lltv_wad \| collateral \| oracle \| cap_rel \| why`. `cap_rel` is the largest share of your book you intend to put in that market; Keel rejects it above `MARKET_REL_CAP` but does not size positions. |
| `RPC_URLS` | `config.json` | Tried in order. Defaults are two public endpoints; use your own node for anything that matters. Reports show only the host, so a key in the URL path stays out of them; `config.json` itself is git-ignored. |

**Pinning the policy.** `python3 -m keel fingerprint` prints a SHA-256 over the
policy thresholds and token addresses. Put it in `POLICY_SHA256` and Keel will stop
with an error if anyone later loosens a threshold without updating the pin. Every
report shows the fingerprint it ran under.

## What a report looks like

[`examples/sample-pack.md`](examples/sample-pack.md) is generated from the
offline snapshot. It shows one healthy market, one market whose collateral token
is *called* wstETH but lives at a different address (rejected), and one market
above the LLTV limit. An excerpt:

```markdown
## Recommendation: IDLE_ALL

1 market(s) meet the filters and pass every check, but: DEMO_ONLY is true; VAULT_ADDRESS is not set.

| Market | LLTV | Eligible | Ready | Utilization | Supply APY | Supply |
|---|---:|:---:|:---:|---:|---:|---:|
| `0xcccccccc…` | 94.5% | no | no | 88.0% | 1.6% | $95,800,000 |
| `0xaaaaaaaa…` | 86.0% | yes | yes | 62.0% | 2.1% | $28,700,000 |
| `0xbbbbbbbb…` | 86.0% | no | no | 40.0% | 3.5% | $7,100,000 |
```

## Running it daily

```cron
# 14:00 New York time, weekdays
CRON_TZ=America/New_York
0 14 * * 1-5  cd /path/to/keel-morpho && python3 -m keel observe >> out/cron.log 2>&1
```

Exit codes: `0` report written, `1` report written but market data was
unavailable (`HOLD`), `2` refused to run (bad config, policy pin mismatch, or a
key in the environment). [docs/OPERATING.md](docs/OPERATING.md) covers what to do
with each result and a checklist before turning `DEMO_ONLY` off.

## Limits and threat model

Keel is a second pair of eyes, not a risk engine. Know what it does not cover:

- **It trusts its data sources.** The Morpho API, DefiLlama and the RPC endpoints
  can be wrong, stale or hostile. The two price checks cross-check sources against
  each other, so one bad source tends to show up as `WARN`/`EXIT` rather than
  `PASS`. A coordinated lie across sources would not be caught. Use an RPC you
  control for real money.
- **It checks one moment.** Utilization, borrower concentration and prices can
  change minutes after a run. Keel does not watch continuously or alert.
- **It does not audit contracts.** It does not review the oracle's construction,
  the interest-rate model, the vault you deposit through, or Morpho itself. Your
  allowlist review is where that happens; the `oracle` field pins the oracle you
  reviewed.
- **Exit liquidity is a snapshot.** Passing `exit_liquidity` today does not
  guarantee you can withdraw during a rush.
- **One asset pair, one chain.** WETH loans against wstETH on Ethereum mainnet.
  Other pairs need code changes, not just config.
- **It cannot stop you.** `KILL` and `DEMO_ONLY` change what Keel recommends; they
  do not block a transaction you sign elsewhere.
- **Key-variable refusal is by name.** It catches common names, not a key stored
  under an innocuous name or in a file. `KEEL_NOT_SIGNING_KEYS` waives exact names
  you vouch for.

## License

[MIT](LICENSE). No warranty. Lending on DeFi protocols can lose all of the funds
involved.
