"""One observe run: fetch, filter, check, decide. No side effects here."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any

from .checks import CHECK_NAMES, EXIT, any_exit, ineligible_reasons, market_ready, run_checks
from .gates import AllowRow, check_allow_rows, decide


def observe(cfg: dict, sources: Any, now: datetime, allow_rows: list[AllowRow], *,
            kill: bool, policy_sha256: str) -> dict:
    errors: list[str] = []
    markets, err = sources.markets()
    fetch_ok = markets is not None
    if err:
        errors.append(err)
    markets = markets or []

    prices, err = sources.prices()
    if err:
        errors.append(err)
    steth_rate, err = sources.steth_per_wsteth()
    if err:
        errors.append(err)

    now_ts = int(now.timestamp())
    table = []
    for m in markets:
        mid = m.get("marketId") or ""
        oracle = (m.get("oracle") or {}).get("address")
        reasons = ineligible_reasons(m, cfg)
        top, e1 = sources.top_borrower_assets(mid)
        opx, e2 = (None, "no oracle address") if not oracle else sources.oracle_price(
            oracle, int(m["loanAsset"].get("decimals") or 18), int(m["collateralAsset"].get("decimals") or 18))
        errors.extend(f"market {mid[:10]}…: {e}" for e in (e1, e2) if e)
        checks = run_checks(m, cfg, top_borrower_assets=top, oracle_price=opx, prices=prices,
                            steth_per_wsteth=steth_rate, now_ts=now_ts)
        st = m.get("state") or {}
        table.append({
            "marketId": mid,
            "lltv": int(m.get("lltv") or 0),
            "oracle": oracle,
            "eligible": not reasons,
            "ineligible_reasons": reasons,
            "utilization": st.get("utilization"),
            "supplyApy": st.get("supplyApy"),
            "supplyUsd": st.get("supplyAssetsUsd"),
            "checks": [asdict(c) for c in checks],
            "ready": market_ready(not reasons, checks),
            "_checks": checks,
        })
    table.sort(key=lambda r: float(r["supplyUsd"] or 0), reverse=True)

    accepted, rejected = check_allow_rows(allow_rows, table, cfg)
    ready_ids = {r["marketId"].lower() for r in table if r["ready"]}
    open_size = float(cfg.get("OPEN_SIZE_WETH") or 0)
    # Markets you could be in: every market named in an ALLOW line, accepted or not
    # (a market that just became ineligible is exactly the one to watch).
    watched = {r.market_id.lower() for r in allow_rows if r.market_id}
    exit_seen = any_exit([r["_checks"] for r in table if r["marketId"].lower() in watched])
    decision = decide(fetch_ok=fetch_ok, demo_only=bool(cfg["DEMO_ONLY"]), kill=kill,
                      vault_set=bool(cfg.get("VAULT_ADDRESS")), open_size=open_size,
                      accepted=accepted, ready_ids=ready_ids,
                      eligible_n=sum(r["eligible"] for r in table))
    for r in table:
        del r["_checks"]
    return {
        "time_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "policy_sha256": policy_sha256,
        "demo_only": bool(cfg["DEMO_ONLY"]),
        "kill": kill,
        "vault_address": cfg.get("VAULT_ADDRESS"),
        "open_size_weth": open_size,
        "fetch_ok": fetch_ok,
        "errors": errors,
        "prices": prices,
        "steth_per_wsteth": steth_rate,
        "markets": table,
        "allow_accepted": [asdict(r) for r in accepted],
        "allow_rejected": [asdict(r) for r in rejected],
        "exit_seen": exit_seen,
        "recommendation": decision.recommendation,
        "rationale": decision.rationale,
        "allocatable": decision.allocatable,
        "blockers": decision.blockers,
        "check_names": list(CHECK_NAMES),
        "exit_status": EXIT,
    }
