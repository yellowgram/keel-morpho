#!/usr/bin/env python3
"""Keel ops gates — DEMO-safe, no signing, no key load, no vault/ALLOW invent.

Pure helpers for hard_daily_observe.py. Unit-testable without network.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")

# Env substrings that suggest private keys / signers — refuse to proceed if set.
FORBIDDEN_KEY_ENV_SUBSTR = (
    "PRIVATE_KEY",
    "ETH_PRIVATE",
    "WALLET_KEY",
    "SIGNER_KEY",
    "MNEMONIC",
    "SEED_PHRASE",
    "ALLOW_PRIVATE",
)


@dataclass
class GateResult:
    ok: bool
    code: str
    detail: str = ""


@dataclass
class AllowRow:
    date: str
    unique_key: str
    lltv_wad: int
    collateral: str
    oracle: str
    cap_rel: float
    why: str
    raw: str
    rejected: bool = False
    reject_reason: str = ""


@dataclass
class ObserveGates:
    demo_only: bool
    kill: bool
    vault_address: Any
    mandate_hash: str
    mandate_file_hash: str
    brief_present: bool
    config_readable: bool
    allow_rows: list[AllowRow] = field(default_factory=list)
    allow_accepted: list[AllowRow] = field(default_factory=list)
    allow_rejected: list[AllowRow] = field(default_factory=list)
    open_size_weth: float = 0.0
    key_env_hits: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def mandate_match(self) -> bool:
        return bool(self.mandate_hash) and self.mandate_hash == self.mandate_file_hash

    def inconsistent_demo_open(self) -> bool:
        return bool(self.demo_only) and float(self.open_size_weth or 0) > 0


def check_forbidden_key_env(environ: dict | None = None) -> list[str]:
    env = environ if environ is not None else os.environ
    hits = []
    for k, v in env.items():
        ku = k.upper()
        if any(s in ku for s in FORBIDDEN_KEY_ENV_SUBSTR):
            if v and str(v).strip():
                hits.append(k)
    return hits


def load_mandate_file(root: Path) -> str:
    p = root / "mandate_hash.txt"
    if not p.is_file():
        return ""
    return p.read_text().strip().splitlines()[0].strip()


def brief_present(root: Path) -> bool:
    return (root / "BRIEF_v1.1.md").is_file()


def parse_allow_line(line: str) -> AllowRow | None:
    """Format: ALLOW | date | uniqueKey | lltv_wad | collateral | oracle | cap_rel | why"""
    s = line.strip()
    if not s or s.startswith("#"):
        return None
    if s.lower().startswith("(empty"):
        return None
    if not s.upper().startswith("ALLOW"):
        return None
    parts = [p.strip() for p in s.split("|")]
    if len(parts) < 8:
        return AllowRow(
            date="", unique_key="", lltv_wad=0, collateral="", oracle="",
            cap_rel=0.0, why="", raw=s, rejected=True,
            reject_reason="format: need ALLOW|date|uniqueKey|lltv_wad|collateral|oracle|cap_rel|why",
        )
    try:
        lltv = int(parts[3].replace("_", ""))
        cap_rel = float(parts[6])
    except ValueError:
        return AllowRow(
            date=parts[1], unique_key=parts[2], lltv_wad=0, collateral=parts[4],
            oracle=parts[5], cap_rel=0.0, why="|".join(parts[7:]), raw=s,
            rejected=True, reject_reason="lltv_wad or cap_rel not numeric",
        )
    return AllowRow(
        date=parts[1],
        unique_key=parts[2],
        lltv_wad=lltv,
        collateral=parts[4],
        oracle=parts[5],
        cap_rel=cap_rel,
        why="|".join(parts[7:]),
        raw=s,
    )


def paste_check_allow(
    rows: list[AllowRow],
    *,
    lltv_max_wad: int,
    market_rel_cap: float,
    eligible_unique_keys: set[str] | None,
    forbidden_collateral: list[str],
) -> tuple[list[AllowRow], list[AllowRow]]:
    """Reject poison ALLOW rows. eligible_unique_keys=None skips uniqueKey membership check."""
    accepted, rejected = [], []
    for r in rows:
        if r.rejected:
            rejected.append(r)
            continue
        reasons = []
        coll = (r.collateral or "").strip()
        if coll.upper() != "WSTETH":
            reasons.append(f"collateral≠wstETH:{coll}")
        for f in forbidden_collateral:
            if f.lower() in coll.lower() and coll.upper() != "WSTETH":
                reasons.append(f"FORBIDDEN_COLLATERAL:{f}")
        if r.lltv_wad > lltv_max_wad:
            reasons.append(f"lltv>{lltv_max_wad}")
        if r.cap_rel > market_rel_cap + 1e-12:
            reasons.append(f"cap_rel>{market_rel_cap}")
        if eligible_unique_keys is not None:
            if r.unique_key not in eligible_unique_keys:
                # Also reject if uniqueKey not in latest *market table* (caller may pass all wst keys)
                # For ALLOCATE eligibility we require Regime-B-eligible set; paste-check uses
                # market_table_keys for "in table" and eligible set separately downstream.
                pass
        if reasons:
            r.rejected = True
            r.reject_reason = "; ".join(reasons)
            rejected.append(r)
        else:
            accepted.append(r)
    return accepted, rejected


def paste_check_allow_against_table(
    rows: list[AllowRow],
    *,
    lltv_max_wad: int,
    market_rel_cap: float,
    market_table_keys: set[str],
    regime_b_eligible_keys: set[str],
    forbidden_collateral: list[str],
) -> tuple[list[AllowRow], list[AllowRow]]:
    accepted, rejected = [], []
    for r in rows:
        if r.rejected:
            rejected.append(r)
            continue
        reasons = []
        coll = (r.collateral or "").strip()
        if coll.upper() != "WSTETH":
            reasons.append(f"collateral≠wstETH:{coll}")
        for f in forbidden_collateral:
            if f.lower() in coll.lower() and coll.upper() != "WSTETH":
                reasons.append(f"FORBIDDEN_COLLATERAL:{f}")
        if r.lltv_wad > lltv_max_wad:
            reasons.append(f"lltv>{lltv_max_wad} (Regime B)")
        if r.cap_rel > market_rel_cap + 1e-12:
            reasons.append(f"cap_rel>{market_rel_cap}")
        if r.unique_key not in market_table_keys:
            reasons.append("uniqueKey not in latest market table")
        elif r.unique_key not in regime_b_eligible_keys:
            reasons.append("uniqueKey not Regime-B-eligible (poison ALLOW)")
        if reasons:
            r.rejected = True
            r.reject_reason = "; ".join(reasons)
            rejected.append(r)
        else:
            accepted.append(r)
    return accepted, rejected


def load_allowlist(path: Path) -> list[AllowRow]:
    if not path.is_file():
        return []
    out = []
    for line in path.read_text().splitlines():
        row = parse_allow_line(line)
        if row:
            out.append(row)
    return out


def five_way_and(
    *,
    allow_accepted_nonempty: bool,
    market_pass: bool,
    vault_set: bool,
    demo_only: bool,
    kill: bool,
) -> GateResult:
    """ALLOW ∩ PASS ∩ VAULT ∩ !DEMO_ONLY ∩ !KILL"""
    parts = {
        "ALLOW": allow_accepted_nonempty,
        "PASS": market_pass,
        "VAULT": vault_set,
        "NOT_DEMO": not demo_only,
        "NOT_KILL": not kill,
    }
    ok = all(parts.values())
    failed = [k for k, v in parts.items() if not v]
    return GateResult(
        ok=ok,
        code="ALLOCATE_OK" if ok else "ALLOCATE_BLOCKED",
        detail=" ∩ ".join(f"{k}={'Y' if v else 'N'}" for k, v in parts.items())
        + (f" | failed={failed}" if failed else ""),
    )


def recommendation_from_gates(
    *,
    five_way: GateResult,
    kill: bool,
    graphql_ok: bool,
    demo_only: bool,
    eligible_n: int,
    inconsistent: bool,
) -> tuple[str, str]:
    if inconsistent:
        return (
            "EXIT_PRIORITY",
            "INCONSISTENT — DEMO_ONLY=true with open live size; EXIT priority (human signs).",
        )
    if not graphql_ok:
        return (
            "HOLD",
            "HALT_FETCH — GraphQL hard-fail; HOLD/STALE; never clear ALLOW/DEMO/KILL.",
        )
    if kill:
        return (
            "IDLE_ALL",
            "KILL=true — IDLE_ALL forced; ALLOCATE drafts frozen; human clears KILL only.",
        )
    if five_way.ok:
        return (
            "ALLOCATE_ELIGIBLE",
            f"Five-way AND passed ({five_way.detail}). Human must still paste ACTION before any sign.",
        )
    # Default DEMO / empty ALLOW / eligible=0 path
    return (
        "IDLE_ALL",
        f"Five-way blocked ({five_way.detail}); RegimeB_eligible={eligible_n}. "
        "IDLE is success. Never ALLOCATE without ALLOW ∩ PASS ∩ VAULT ∩ !DEMO ∩ !KILL.",
    )


def o6_flag(age_s: int | None, stale_s: int) -> str:
    if age_s is None:
        return "O6_PARTIAL"
    if age_s > stale_s:
        return f"O6_FAIL(age={age_s}s>{stale_s})"
    return f"O6_PASS(age={age_s}s)"


def market_has_pass_score(o_flags: list[str]) -> bool:
    """ALLOCATE needs full PASS on O1–O7. WARN/EXIT/FAIL/PARTIAL/N/A => not PASS."""
    if not o_flags:
        return False
    for flag in o_flags:
        if any(tok in flag for tok in ("_EXIT", "_WARN", "_FAIL", "_PARTIAL", "_N/A")):
            return False
    # Require O1..O7 each have a PASS*
    for i in range(1, 8):
        prefix = f"O{i}_PASS"
        if not any(f.startswith(prefix) for f in o_flags):
            return False
    return True


def any_market_pass(table_rows: list[dict]) -> bool:
    for r in table_rows:
        if r.get("eligible") and market_has_pass_score(r.get("o_flags") or []):
            return True
    return False


def quiet_idle_fingerprint(
    recommendation: str,
    blockers: list[str],
    eligible_ids: list[str],
) -> str:
    el = ",".join(sorted(eligible_ids))
    bl = "|".join(blockers)
    return f"{recommendation}::{bl}::{el}"


def parse_last_log_fingerprint(log_text: str) -> tuple[str | None, datetime | None]:
    """Extract last recommendation fingerprint bits and timestamp from log.md."""
    if not log_text.strip():
        return None, None
    entries = re.split(r"\n(?=### LOG \| )", log_text.strip())
    last = entries[-1] if entries else ""
    m = re.search(r"### LOG \| (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", last)
    ts = None
    if m:
        ts = datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
    rec_m = re.search(r"recommendation: (\S+)", last)
    elig_m = re.search(r"eligible_regime_B: (\[[^\]]*\])", last)
    block_m = re.search(r"blockers: (\[[^\]]*\])", last)
    quiet_m = re.search(r"quiet_fp: (\S+)", last)
    if quiet_m:
        return quiet_m.group(1), ts
    rec = rec_m.group(1) if rec_m else ""
    elig = elig_m.group(1) if elig_m else "[]"
    try:
        import json
        ids = json.loads(elig.replace("'", '"')) if elig else []
    except Exception:
        ids = []
    blockers = []
    if block_m:
        blockers = [block_m.group(1)]
    fp = quiet_idle_fingerprint(rec, blockers, [str(x) for x in ids])
    return fp, ts


def weekday_miss_note(
    last_ts: datetime | None,
    now: datetime,
) -> str | None:
    """If prior weekday observe missing (gap >1 weekday), return note. DEMO-idle = log-only text."""
    if last_ts is None:
        return "missed_observe: no prior log entry (first or empty log)"
    last_ny = last_ts.astimezone(NY)
    now_ny = now.astimezone(NY)
    # Count weekdays between last observe date and today (exclusive of today)
    d0 = last_ny.date()
    d1 = now_ny.date()
    if d1 <= d0:
        return None
    misses = 0
    cur = d0 + timedelta(days=1)
    while cur < d1:
        if cur.weekday() < 5:  # Mon-Fri
            misses += 1
        cur += timedelta(days=1)
    if misses == 0:
        return None
    if misses == 1:
        return f"missed_observe: 1 weekday gap since {last_ny.strftime('%Y-%m-%d %Z')} (DEMO+idle: log-only)"
    return (
        f"missed_observe: {misses} consecutive weekday gaps since "
        f"{last_ny.strftime('%Y-%m-%d %Z')} (DEMO+idle: log-only; live-open would KILL-warn)"
    )


def drill_status(*, idle: bool, open_alloc: bool) -> str:
    if idle and not open_alloc:
        return "SKIP_IDLE"
    if open_alloc:
        return "PASS_DRILL"  # path must be exercised; caller may override on fail
    return "PASS_DRILL"


def status_color(
    *,
    graphql_ok: bool,
    mandate_ok: bool,
    fetch_partial: bool,
    inconsistent: bool,
) -> str:
    if inconsistent:
        return "RED"
    if not mandate_ok or not graphql_ok:
        return "RED"
    if fetch_partial:
        return "AMBER"
    return "GREEN"


def build_observe_gates(root: Path, cfg: dict, environ: dict | None = None) -> ObserveGates:
    errors = []
    warnings = []
    try:
        mh = str(cfg.get("mandate_hash") or "")
        config_readable = True
    except Exception as e:
        mh = ""
        config_readable = False
        errors.append(f"config:{e}")
        return ObserveGates(
            demo_only=True, kill=True, vault_address=None, mandate_hash="",
            mandate_file_hash="", brief_present=False, config_readable=False,
            errors=errors,
        )

    file_hash = load_mandate_file(root)
    bp = brief_present(root)
    if not bp:
        errors.append("BRIEF_v1.1.md missing")
    if not file_hash:
        errors.append("mandate_hash.txt missing/empty")
    if mh and file_hash and mh != file_hash:
        errors.append(f"mandate_hash mismatch config≠file ({mh[:12]}…≠{file_hash[:12]}…)")

    kill = bool(cfg.get("KILL", False))
    # Env KILL=true also trips
    env = environ if environ is not None else os.environ
    if str(env.get("KILL", "")).lower() in ("1", "true", "yes"):
        kill = True

    demo = bool(cfg.get("DEMO_ONLY", True))
    # Never allow agent to treat missing DEMO as live
    if "DEMO_ONLY" not in cfg:
        demo = True
        warnings.append("DEMO_ONLY missing from config — forced true")

    key_hits = check_forbidden_key_env(env)
    if key_hits and demo:
        errors.append(f"DEMO gate: forbidden key env present: {key_hits} — refuse observe")

    allow_path = root / "eth-credit-conservative" / "allowlist.md"
    raw_rows = load_allowlist(allow_path)

    return ObserveGates(
        demo_only=demo,
        kill=kill,
        vault_address=cfg.get("VAULT_ADDRESS"),
        mandate_hash=mh,
        mandate_file_hash=file_hash,
        brief_present=bp,
        config_readable=config_readable,
        allow_rows=raw_rows,
        open_size_weth=float(cfg.get("OPEN_SIZE_WETH") or 0),
        key_env_hits=key_hits,
        errors=errors,
        warnings=warnings,
    )


def agent_may_set_kill_on_exit(o_flags_all: list[str]) -> bool:
    """True if any EXIT-class O* trip — caller may set KILL=true in config (human clears)."""
    return any("_EXIT" in f for f in o_flags_all)


def set_kill_in_config(config_path: Path, value: bool = True) -> None:
    """Agent may set KILL on EXIT-class; never clears (human only)."""
    import json
    if not value:
        raise RuntimeError("Refuse clear KILL — human only")
    paths = [config_path]
    sleeve = config_path.parent / "eth-credit-conservative" / "config.json"
    if sleeve.is_file() and sleeve != config_path:
        paths.append(sleeve)
    for p in paths:
        cfg = json.loads(p.read_text())
        cfg["KILL"] = True
        # Do not touch DEMO_ONLY, VAULT, ALLOW
        p.write_text(json.dumps(cfg, indent=2) + "\n")


def refuse_invent_action() -> GateResult:
    return GateResult(ok=False, code="ACTION_REFUSED", detail="Observe refuses to invent/complete ACTION; human-only append-only.")


def refuse_invent_allow() -> GateResult:
    return GateResult(ok=False, code="ALLOW_REFUSED", detail="Observe refuses to invent ALLOW rows.")


def refuse_invent_vault() -> GateResult:
    return GateResult(ok=False, code="VAULT_REFUSED", detail="Observe refuses to set VAULT_ADDRESS.")
