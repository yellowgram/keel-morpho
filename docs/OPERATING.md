# Operating Keel

## Who does what

| Keel | You |
|---|---|
| Fetches data, runs the checks, writes the report, sets `KILL` on an EXIT with an open position | Reviews markets and writes allowlist lines, sets `VAULT_ADDRESS` and `OPEN_SIZE_WETH`, turns `DEMO_ONLY` off, clears `KILL`, signs every transaction |

## Reading a result

1. **Exit code 2.** Keel refused to run. The message says why:
   - missing or invalid config;
   - `POLICY_SHA256` mismatch (someone changed a threshold; review the change, then update the pin);
   - a key-like environment variable.
2. **`HOLD`.** Market data failed. Do not change positions based on this run. Run again later; if it persists, check the "Data problems" section of the report.
3. **`EXIT_PRIORITY`.** `DEMO_ONLY` is true but you report an open position. Reduce exposure first, then fix the config so it matches reality.
4. **Any `EXIT` on a market you are in.** Keel has set `KILL`. Decide whether to withdraw. Clear `KILL` only once you understand the cause.
5. **`UNKNOWN` checks.** Data for that check was missing. The market is not ready. Repeated `UNKNOWN` on `oracle_deviation` or `wsteth_rate` usually means the RPC endpoints are failing; set your own in `RPC_URLS`.
6. **`freshness` WARN.** DefiLlama's wstETH and stETH prices were 925–986 s old in 3 samples on 2026-10-19 (WETH 46–87 s). With the example `STALE_S` of 900 s, `freshness` therefore WARNs on most runs and the allocate recommendation is usually unreachable. That is deliberate in the example; if you accept older prices, raise `STALE_S` to the age you are willing to act on, then re-pin the policy. A timestamp more than 60 s in the future is `UNKNOWN`.
7. **`IDLE_ALL` with no eligible markets.** This is the normal result. Loosening `MAX_LLTV_WAD` to get an eligible market is a policy decision about how much risk you accept, not a fix.
8. **Rejected allowlist lines.** The report gives the reason. Common causes: a market's oracle changed or the id was mistyped.

## Before turning `DEMO_ONLY` off

- [ ] `POLICY_SHA256` is set and the report shows the same fingerprint.
- [ ] `RPC_URLS` points to an endpoint you control or trust.
- [ ] At least one allowlist line is accepted in the latest report, for a market you reviewed (oracle, interest-rate model, curator if using a vault).
- [ ] No check on that market has been `UNKNOWN` for the last several runs.
- [ ] `VAULT_ADDRESS` and `OPEN_SIZE_WETH` are correct.
- [ ] You can simulate a transaction before signing it (for example with a Safe or Tenderly simulation).
- [ ] You know how you will withdraw if a check turns `EXIT`.
- [ ] The daily run is scheduled and you read the report.
