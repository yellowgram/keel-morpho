"""Market eligibility and the six risk checks.

Each check returns PASS, WARN, EXIT or UNKNOWN. A market is ready only when
it is eligible and every check is PASS. UNKNOWN (missing data) is never PASS.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

PASS, WARN, EXIT, UNKNOWN = "PASS", "WARN", "EXIT", "UNKNOWN"

CHECK_NAMES = (
    "top_borrower",
    "utilization",
    "oracle_deviation",
    "wsteth_rate",
    "exit_liquidity",
    "freshness",
)


@dataclass
class Check:
    name: str
    status: str
    detail: str


def _sym(s) -> str:
    """Token symbols come from the API; keep them inert in the markdown report."""
    clean = re.sub(r"[^A-Za-z0-9._-]", "", str(s or ""))[:20]
    return clean or "?"


def _addr(s) -> str:
    s = str(s or "")
    return s if re.fullmatch(r"0x[0-9a-fA-F]{40}", s) else "?"


def ineligible_reasons(market: dict, cfg: dict) -> list[str]:
    """Why a market fails the filters. Matching is by address, never by symbol."""
    reasons = []
    coll = (market.get("collateralAsset") or {})
    loan = (market.get("loanAsset") or {})
    if (coll.get("address") or "").lower() != cfg["WSTETH"].lower():
        reasons.append(f"collateral {_sym(coll.get('symbol'))} at {_addr(coll.get('address'))} is not the wstETH contract")
    if (loan.get("address") or "").lower() != cfg["VAULT_ASSET"].lower():
        reasons.append(f"loan asset {_sym(loan.get('symbol'))} is not WETH")
    lltv = int(market.get("lltv") or 0)
    if lltv > int(cfg["MAX_LLTV_WAD"]):
        reasons.append(f"LLTV {lltv / 1e16:.1f}% is above {int(cfg['MAX_LLTV_WAD']) / 1e16:.1f}%")
    return reasons


def _band(value: float, warn: float, exit_: float, fmt: str) -> tuple[str, str]:
    s = fmt.format(value)
    if value > exit_:
        return EXIT, f"{s} > exit {fmt.format(exit_)}"
    if value > warn:
        return WARN, f"{s} > warn {fmt.format(warn)}"
    return PASS, s


def run_checks(market: dict, cfg: dict, *, top_borrower_assets: int | None,
               oracle_price: float | None, prices: dict | None,
               steth_per_wsteth: float | None, now_ts: int) -> list[Check]:
    st = market.get("state") or {}
    loan_dec = int((market.get("loanAsset") or {}).get("decimals") or 18)
    out: list[Check] = []

    borrow = int(st.get("borrowAssets") or 0)
    if top_borrower_assets is None:
        out.append(Check("top_borrower", UNKNOWN, "positions unavailable"))
    elif borrow == 0:
        out.append(Check("top_borrower", PASS, "no borrowers"))
    else:
        out.append(Check("top_borrower", *_band(top_borrower_assets / borrow, cfg["BORROWER_WARN"], cfg["BORROWER_EXIT"], "{:.1%}")))

    util = st.get("utilization")
    if util is None:
        out.append(Check("utilization", UNKNOWN, "utilization unavailable"))
    else:
        out.append(Check("utilization", *_band(float(util), cfg["UTIL_WARN"], cfg["UTIL_EXIT"], "{:.1%}")))

    market_px = None
    if prices:
        market_px = prices["WSTETH"]["usd"] / prices["VAULT_ASSET"]["usd"]
    if oracle_price is None or market_px is None:
        out.append(Check("oracle_deviation", UNKNOWN, "oracle or market price unavailable"))
    else:
        bps = abs(oracle_price - market_px) / market_px * 1e4
        status, d = _band(bps, cfg["ORACLE_WARN_BPS"], cfg["ORACLE_EXIT_BPS"], "{:.0f} bps")
        out.append(Check("oracle_deviation", status, f"oracle {oracle_price:.5f} vs market {market_px:.5f} WETH/wstETH: {d}"))

    if steth_per_wsteth is None or not prices:
        out.append(Check("wsteth_rate", UNKNOWN, "stEthPerToken or prices unavailable"))
    else:
        mkt = prices["WSTETH"]["usd"] / prices["STETH"]["usd"]
        bps = abs(mkt - steth_per_wsteth) / steth_per_wsteth * 1e4
        status, d = _band(bps, cfg["WST_WARN_BPS"], cfg["WST_EXIT_BPS"], "{:.0f} bps")
        out.append(Check("wsteth_rate", status, f"market {mkt:.5f} vs on-chain {steth_per_wsteth:.5f} stETH/wstETH: {d}"))

    liq, supply = st.get("liquidityAssets"), st.get("supplyAssets")
    if liq is None or supply is None:
        out.append(Check("exit_liquidity", UNKNOWN, "liquidity unavailable"))
    else:
        liq_w, sup_w = int(liq) / 10 ** loan_dec, int(supply) / 10 ** loan_dec
        need = max(cfg["EXIT_LIQ_PCT"] * sup_w, cfg["EXIT_LIQ_FLOOR_WETH"])
        status = PASS if liq_w >= need else WARN
        out.append(Check("exit_liquidity", status, f"{liq_w:,.1f} WETH idle, need {need:,.1f}"))

    # Price data age. (Morpho's state timestamp is the market's last interaction,
    # which is old for quiet markets and says nothing about data quality.)
    if not prices:
        out.append(Check("freshness", UNKNOWN, "no price timestamps"))
    else:
        age = max(0, now_ts - min(int(v["ts"]) for v in prices.values()))
        out.append(Check("freshness", PASS if age <= cfg["STALE_S"] else WARN,
                         f"prices {age}s old (limit {cfg['STALE_S']}s)"))
    return out


def market_ready(eligible: bool, checks: list[Check]) -> bool:
    return eligible and len(checks) == len(CHECK_NAMES) and all(c.status == PASS for c in checks)


def any_exit(checks_by_market: list[list[Check]]) -> bool:
    return any(c.status == EXIT for cs in checks_by_market for c in cs)
