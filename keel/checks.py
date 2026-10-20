"""Market eligibility and the six risk checks.

Each check returns PASS, WARN, EXIT or UNKNOWN. A market is ready only when
it is eligible and every check is PASS. UNKNOWN (missing data) is never PASS.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

PASS, WARN, EXIT, UNKNOWN = "PASS", "WARN", "EXIT", "UNKNOWN"

# Clock skew tolerated on price timestamps before they count as broken.
FUTURE_SKEW_S = 60

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
    try:
        lltv = int(str(market.get("lltv")))
    except (TypeError, ValueError):
        lltv = None
    if lltv is None or lltv <= 0 or lltv >= 10**18:
        # Missing or nonsense LLTV is not "low enough": fail the filter.
        reasons.append("LLTV is missing or invalid")
    elif lltv > int(cfg["MAX_LLTV_WAD"]):
        reasons.append(f"LLTV {lltv / 1e16:.1f}% is above {int(cfg['MAX_LLTV_WAD']) / 1e16:.1f}%")
    return reasons


def _finite_pos(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v > 0


def _band(value: float, warn: float, exit_: float, fmt: str) -> tuple[str, str]:
    # NaN or a negative reading is broken data, never a pass (json.loads accepts NaN).
    if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        return UNKNOWN, f"invalid value {value!r}"
    s = fmt.format(value)
    if value > exit_:
        return EXIT, f"{s} > exit {fmt.format(exit_)}"
    if value > warn:
        return WARN, f"{s} > warn {fmt.format(warn)}"
    return PASS, s


def _nonneg_int(v) -> int | None:
    """A non-negative integer amount (int or decimal string), or None if missing or broken."""
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, int):
        return v if v >= 0 else None
    if isinstance(v, float):
        return int(v) if math.isfinite(v) and v >= 0 and v == int(v) else None
    # ASCII digits only. str.isdigit() also accepts '²' (int() then raises) and other scripts' digits.
    if isinstance(v, str) and re.fullmatch(r"[0-9]+", v):
        return int(v)
    return None


def run_checks(market: dict, cfg: dict, *, top_borrower_assets: int | None,
               oracle_price: float | None, prices: dict | None,
               steth_per_wsteth: float | None, now_ts: int) -> list[Check]:
    st = market.get("state") or {}
    loan_dec = int((market.get("loanAsset") or {}).get("decimals") or 18)
    out: list[Check] = []

    borrow = _nonneg_int(st.get("borrowAssets"))
    supply = _nonneg_int(st.get("supplyAssets"))
    if borrow is None:
        out.append(Check("top_borrower", UNKNOWN, "borrowAssets missing or invalid"))
    elif supply is not None and borrow > supply:
        # Impossible data. A huge borrow figure would also hide top-borrower concentration.
        out.append(Check("top_borrower", UNKNOWN, "borrow is above supply, which is impossible"))
    elif top_borrower_assets is None:
        out.append(Check("top_borrower", UNKNOWN, "positions unavailable"))
    elif borrow == 0:
        out.append(Check("top_borrower", PASS, "no borrowers"))
    elif top_borrower_assets <= 0:
        # The market reports borrows but the positions query returned none: missing data.
        out.append(Check("top_borrower", UNKNOWN, "market has borrows but no positions were returned"))
    elif top_borrower_assets > borrow:
        out.append(Check("top_borrower", UNKNOWN, "one position borrows more than the whole market, which is impossible"))
    else:
        out.append(Check("top_borrower", *_band(top_borrower_assets / borrow, cfg["BORROWER_WARN"], cfg["BORROWER_EXIT"], "{:.1%}")))

    util = st.get("utilization")
    try:
        util = None if util is None else float(util)
    except (TypeError, ValueError):
        util = float("nan")
    if util is None:
        out.append(Check("utilization", UNKNOWN, "utilization unavailable"))
    else:
        out.append(Check("utilization", *_band(util, cfg["UTIL_WARN"], cfg["UTIL_EXIT"], "{:.1%}")))

    prices_ok = bool(prices) and all(_finite_pos((prices.get(k) or {}).get("usd")) for k in ("WSTETH", "VAULT_ASSET", "STETH"))
    market_px = None
    if prices_ok:
        market_px = prices["WSTETH"]["usd"] / prices["VAULT_ASSET"]["usd"]
    if not _finite_pos(oracle_price) or market_px is None:
        out.append(Check("oracle_deviation", UNKNOWN, "oracle or market price unavailable"))
    else:
        bps = abs(oracle_price - market_px) / market_px * 1e4
        status, d = _band(bps, cfg["ORACLE_WARN_BPS"], cfg["ORACLE_EXIT_BPS"], "{:.0f} bps")
        out.append(Check("oracle_deviation", status, f"oracle {oracle_price:.5f} vs market {market_px:.5f} WETH/wstETH: {d}"))

    if not _finite_pos(steth_per_wsteth) or not prices_ok:
        out.append(Check("wsteth_rate", UNKNOWN, "stEthPerToken or prices unavailable"))
    else:
        mkt = prices["WSTETH"]["usd"] / prices["STETH"]["usd"]
        bps = abs(mkt - steth_per_wsteth) / steth_per_wsteth * 1e4
        status, d = _band(bps, cfg["WST_WARN_BPS"], cfg["WST_EXIT_BPS"], "{:.0f} bps")
        out.append(Check("wsteth_rate", status, f"market {mkt:.5f} vs on-chain {steth_per_wsteth:.5f} stETH/wstETH: {d}"))

    liq = _nonneg_int(st.get("liquidityAssets"))
    if liq is None or supply is None:
        out.append(Check("exit_liquidity", UNKNOWN, "liquidity or supply missing or invalid"))
    elif borrow is not None and borrow > supply:
        out.append(Check("exit_liquidity", UNKNOWN, "borrow is above supply, which is impossible"))
    elif liq > supply:
        out.append(Check("exit_liquidity", UNKNOWN, "liquidity is above supply, which is impossible"))
    else:
        liq_w, sup_w = liq / 10 ** loan_dec, supply / 10 ** loan_dec
        need = max(cfg["EXIT_LIQ_PCT"] * sup_w, cfg["EXIT_LIQ_FLOOR_WETH"])
        status = PASS if liq_w >= need else WARN
        out.append(Check("exit_liquidity", status, f"{liq_w:,.1f} WETH idle, need {need:,.1f}"))

    # Price data age. (Morpho's state timestamp is the market's last interaction,
    # which is old for quiet markets and says nothing about data quality.)
    stamps = []
    for v in (prices or {}).values():
        ts = (v or {}).get("ts") if isinstance(v, dict) else None
        stamps.append(ts if isinstance(ts, (int, float)) and not isinstance(ts, bool) and math.isfinite(ts) else None)
    if not stamps or None in stamps:
        out.append(Check("freshness", UNKNOWN, "no price timestamps"))
    elif max(stamps) > now_ts + FUTURE_SKEW_S:
        # A timestamp from the future is broken data, not a fresh price.
        out.append(Check("freshness", UNKNOWN, f"price timestamp {int(max(stamps)) - now_ts}s in the future"))
    else:
        age = max(0, now_ts - int(min(stamps)))
        out.append(Check("freshness", PASS if age <= cfg["STALE_S"] else WARN,
                         f"prices {age}s old (limit {cfg['STALE_S']}s)"))
    return out


def market_ready(eligible: bool, checks: list[Check]) -> bool:
    return eligible and len(checks) == len(CHECK_NAMES) and all(c.status == PASS for c in checks)


def any_exit(checks_by_market: list[list[Check]]) -> bool:
    return any(c.status == EXIT for cs in checks_by_market for c in cs)
