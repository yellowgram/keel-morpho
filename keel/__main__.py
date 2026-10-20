"""Command line: python3 -m keel observe | fingerprint."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .config import ConfigError, check_policy_pin, load_config, policy_fingerprint
from .gates import forbidden_key_env, load_allowlist, missed_weekdays, set_kill
from .observe import observe
from .report import log_entry, render_pack
from .sources import FixtureSources, LiveSources

EXIT_OK, EXIT_NO_DATA, EXIT_CONFIG = 0, 1, 2


def _err(msg: str) -> None:
    print(f"keel: {msg}", file=sys.stderr)


def _last_run(log: Path) -> datetime | None:
    if not log.is_file():
        return None
    lines = [l for l in log.read_text().splitlines() if l.strip()]
    for line in reversed(lines):
        try:
            return datetime.strptime(json.loads(line)["time_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except (ValueError, KeyError):
            continue
    return None


def cmd_observe(a: argparse.Namespace) -> int:
    cfg_path = Path(a.config)
    try:
        cfg, warnings = load_config(cfg_path)
        fp = check_policy_pin(cfg)
    except ConfigError as e:
        _err(str(e))
        return EXIT_CONFIG
    bad = forbidden_key_env()
    if bad:
        _err("refusing to run: signing-key environment variables are set (" + ", ".join(bad) +
             "). Keel never needs a key; unset them.")
        return EXIT_CONFIG
    for w in warnings:
        _err("warning: " + w)

    base = cfg_path.resolve().parent
    allow_path = Path(a.allowlist) if a.allowlist else base / cfg["ALLOWLIST_PATH"]
    out = Path(a.out) if a.out else base / cfg["OUT_DIR"]
    try:
        sources = FixtureSources(Path(a.fixture)) if a.fixture else LiveSources(cfg)
    except (OSError, ValueError) as e:
        _err(f"cannot read fixture: {e}")
        return EXIT_CONFIG
    when = a.now or getattr(sources, "captured_at", None)
    try:
        now = datetime.fromisoformat(when.replace("Z", "+00:00")) if when else datetime.now(timezone.utc)
    except ValueError:
        now = None
    if now is None or now.tzinfo is None:
        _err("--now / captured_at must be ISO 8601 with a timezone, e.g. 2026-10-19T14:00:00Z")
        return EXIT_CONFIG
    kill = cfg["KILL"] or os.environ.get("KEEL_KILL", "").strip().lower() in ("1", "true", "yes")

    result = observe(cfg, sources, now, load_allowlist(allow_path), kill=kill, policy_sha256=fp)
    if result["exit_seen"] and float(cfg.get("OPEN_SIZE_WETH") or 0) > 0 and not kill:
        set_kill(cfg_path)
        _err("an EXIT threshold was crossed with an open position: KILL set to true in " + str(cfg_path))
        result = observe(cfg, sources, now, load_allowlist(allow_path), kill=True, policy_sha256=fp)

    out.mkdir(parents=True, exist_ok=True)
    log = out / "log.jsonl"
    missed = missed_weekdays(_last_run(log), now)
    if missed:
        result["errors"].insert(0, f"{missed} weekday(s) passed with no run")
    (out / "pack.md").write_text(render_pack(result))
    (out / "latest.json").write_text(json.dumps(result, indent=2) + "\n")
    with log.open("a") as f:
        f.write(log_entry(result))
    print(f"{result['recommendation']}: {result['rationale']}")
    print(f"report: {out / 'pack.md'}")
    return EXIT_OK if result["fetch_ok"] else EXIT_NO_DATA


def cmd_fingerprint(a: argparse.Namespace) -> int:
    try:
        cfg, _ = load_config(Path(a.config))
    except ConfigError as e:
        _err(str(e))
        return EXIT_CONFIG
    print(policy_fingerprint(cfg))
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python3 -m keel", description="Read-only Morpho market filter for WETH lent against wstETH.")
    p.add_argument("--version", action="version", version=f"keel {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("observe", help="fetch markets, run the checks, write out/pack.md")
    o.add_argument("--config", default="config.json")
    o.add_argument("--allowlist", help="default: ALLOWLIST_PATH next to the config")
    o.add_argument("--out", help="default: OUT_DIR next to the config")
    o.add_argument("--fixture", help="read a saved snapshot instead of the network (offline demo, tests)")
    o.add_argument("--now", help="override the clock, ISO 8601 with timezone")
    o.set_defaults(func=cmd_observe)
    f = sub.add_parser("fingerprint", help="print the policy fingerprint to pin as POLICY_SHA256")
    f.add_argument("--config", default="config.json")
    f.set_defaults(func=cmd_fingerprint)
    a = p.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
