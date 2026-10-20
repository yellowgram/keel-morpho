"""Operator inputs (allowlist, KILL, DEMO_ONLY) and the final recommendation."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")

# Env var names that look like signing material. Keel refuses to run next to them.
FORBIDDEN_KEY_ENV_SUBSTR = ("PRIVATE_KEY", "ETH_PRIVATE", "WALLET_KEY", "SIGNER_KEY", "MNEMONIC", "SEED_PHRASE")

ALLOW_FORMAT = "ALLOW | date | marketId | lltv_wad | collateral | oracle | cap_rel | why"


@dataclass
class AllowRow:
    raw: str
    date: str = ""
    market_id: str = ""
    lltv_wad: int = 0
    collateral: str = ""
    oracle: str = ""
    cap_rel: float = 0.0
    why: str = ""
    reject_reason: str = ""


def forbidden_key_env(environ: dict | None = None) -> list[str]:
    env = os.environ if environ is None else environ
    return sorted(k for k, v in env.items()
                  if v and str(v).strip() and any(s in k.upper() for s in FORBIDDEN_KEY_ENV_SUBSTR))


def parse_allow_line(line: str) -> AllowRow | None:
    s = line.strip()
    if not s or s.startswith("#") or not s.upper().startswith("ALLOW"):
        return None
    parts = [p.strip() for p in s.split("|")]
    if len(parts) < 8:
        return AllowRow(raw=s, reject_reason=f"format: expected {ALLOW_FORMAT}")
    try:
        lltv = int(parts[3].replace("_", ""))
        cap_rel = float(parts[6])
    except ValueError:
        return AllowRow(raw=s, market_id=parts[2], reject_reason="lltv_wad or cap_rel is not a number")
    return AllowRow(raw=s, date=parts[1], market_id=parts[2], lltv_wad=lltv, collateral=parts[4],
                    oracle=parts[5], cap_rel=cap_rel, why="|".join(parts[7:]))


def load_allowlist(path: Path) -> list[AllowRow]:
    if not path.is_file():
        return []
    return [r for r in (parse_allow_line(l) for l in path.read_text().splitlines()) if r]


def check_allow_rows(rows: list[AllowRow], table: list[dict], cfg: dict) -> tuple[list[AllowRow], list[AllowRow]]:
    """An ALLOW row must match a market in today's table exactly and that market must be eligible."""
    by_id = {r["marketId"].lower(): r for r in table}
    accepted, rejected = [], []
    for row in rows:
        reasons = [row.reject_reason] if row.reject_reason else []
        if not reasons:
            m = by_id.get(row.market_id.lower())
            if m is None:
                reasons.append("marketId not in today's table")
            else:
                if not m["eligible"]:
                    reasons.append("market is not eligible: " + "; ".join(m["ineligible_reasons"]))
                if row.lltv_wad != m["lltv"]:
                    reasons.append(f"lltv_wad {row.lltv_wad} does not match the market ({m['lltv']})")
                if row.oracle.lower() != (m["oracle"] or "").lower():
                    reasons.append("oracle does not match the market")
            if row.collateral.lower() not in ("wsteth", cfg["WSTETH"].lower()):
                reasons.append(f"collateral {row.collateral!r} is not wstETH")
            if row.cap_rel > float(cfg["MARKET_REL_CAP"]) + 1e-12:
                reasons.append(f"cap_rel {row.cap_rel} > MARKET_REL_CAP {cfg['MARKET_REL_CAP']}")
        if reasons:
            row.reject_reason = "; ".join(reasons)
            rejected.append(row)
        else:
            accepted.append(row)
    return accepted, rejected


@dataclass
class Decision:
    recommendation: str
    rationale: str
    allocatable: list[str]
    blockers: list[str]


def decide(*, fetch_ok: bool, demo_only: bool, kill: bool, vault_set: bool, open_size: float,
           accepted: list[AllowRow], ready_ids: set[str], eligible_n: int) -> Decision:
    """The recommendation. Keel only ever recommends; a person signs."""
    allocatable = sorted(r.market_id for r in accepted if r.market_id.lower() in ready_ids)
    blockers = []
    if demo_only:
        blockers.append("DEMO_ONLY is true")
    if kill:
        blockers.append("KILL is true")
    if not vault_set:
        blockers.append("VAULT_ADDRESS is not set")
    if not accepted:
        blockers.append("no accepted ALLOW rows")
    if eligible_n == 0:
        blockers.append("no market meets the filters")
    if accepted and not allocatable:
        blockers.append("no allowlisted market passes every check")

    if demo_only and open_size > 0:
        return Decision("EXIT_PRIORITY", "DEMO_ONLY is true but OPEN_SIZE_WETH > 0. The config and the book disagree; "
                        "reduce exposure first and fix the config.", [], blockers)
    if not fetch_ok:
        return Decision("HOLD", "Market data could not be fetched. Change nothing until a run succeeds.", [], blockers)
    if kill:
        return Decision("IDLE_ALL", "KILL is set. Only a person clears it, in config.json.", [], blockers)
    if allocatable and vault_set and not demo_only:
        return Decision("ALLOCATE_ELIGIBLE", "These allowlisted markets meet the filters and pass every check. "
                        "A person decides and signs.", allocatable, blockers)
    if not ready_ids:
        return Decision("IDLE_ALL", "It is normal for Keel to recommend holding everything idle. "
                        "That means no market met the safety filters.", [], blockers)
    return Decision("IDLE_ALL", f"{len(ready_ids)} market(s) meet the filters and pass every check, but: "
                    + "; ".join(blockers) + ".", [], blockers)


def set_kill(config_path: Path) -> None:
    """Set KILL=true in config.json. Keel never clears it."""
    cfg = json.loads(config_path.read_text())
    cfg["KILL"] = True
    config_path.write_text(json.dumps(cfg, indent=2) + "\n")


def missed_weekdays(last_ts: datetime | None, now: datetime) -> int | None:
    """Weekdays (New York) with no run between the last run and today. None if there was no run."""
    if last_ts is None:
        return None
    d0, d1 = last_ts.astimezone(NY).date(), now.astimezone(NY).date()
    n, cur = 0, d0 + timedelta(days=1)
    while cur < d1:
        n += cur.weekday() < 5
        cur += timedelta(days=1)
    return n
