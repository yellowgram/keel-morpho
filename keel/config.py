"""Config loading and the policy fingerprint."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

# Keys that decide which markets are eligible and how they are scored.
# Their fingerprint is printed in every report; pin it with POLICY_SHA256 so
# that a loosened threshold stops the run instead of silently changing advice.
POLICY_KEYS = (
    "CHAIN_ID",
    "VAULT_ASSET",
    "WSTETH",
    "STETH",
    "MAX_LLTV_WAD",
    "MARKET_REL_CAP",
    "BORROWER_WARN",
    "BORROWER_EXIT",
    "UTIL_WARN",
    "UTIL_EXIT",
    "ORACLE_WARN_BPS",
    "ORACLE_EXIT_BPS",
    "WST_WARN_BPS",
    "WST_EXIT_BPS",
    "EXIT_LIQ_PCT",
    "EXIT_LIQ_FLOOR_WETH",
    "STALE_S",
)

DEFAULTS: dict[str, Any] = {
    "DEMO_ONLY": True,
    "KILL": False,
    "VAULT_ADDRESS": None,
    "OPEN_SIZE_WETH": 0,
    "GRAPHQL": "https://api.morpho.org/graphql",
    "LLAMA_PRICES": "https://coins.llama.fi/prices/current/",
    "RPC_URLS": ["https://ethereum.publicnode.com", "https://eth.drpc.org"],
    "ALLOWLIST_PATH": "allowlist.md",
    "OUT_DIR": "out",
    "POLICY_SHA256": None,
}

# Renamed in 0.2.0. Old configs keep working.
RENAMED = {"FORBIDDEN_LLTV_WAD_MIN_EXCLUSIVE_B": "MAX_LLTV_WAD"}


class ConfigError(Exception):
    """The config is unusable. The run stops before any report is written."""


def load_config(path: Path) -> tuple[dict[str, Any], list[str]]:
    """Return (config, warnings). Raises ConfigError on missing or invalid input."""
    if not path.is_file():
        raise ConfigError(f"{path} not found. Copy config.example.json to {path.name} first.")
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise ConfigError(f"{path} is not valid JSON: {e}") from e
    if not isinstance(raw, dict):
        raise ConfigError(f"{path} must hold a JSON object")
    warnings: list[str] = []
    cfg: dict[str, Any] = dict(DEFAULTS)
    if "DEMO_ONLY" not in raw:
        warnings.append("DEMO_ONLY missing from config; treated as true")
    for old, new in RENAMED.items():
        if old in raw and new not in raw:
            raw[new] = raw.pop(old)
            warnings.append(f"config key {old} is now {new}")
    cfg.update(raw)
    missing = [k for k in POLICY_KEYS if k not in cfg]
    if missing:
        raise ConfigError(f"config is missing policy keys: {', '.join(missing)}")
    if not isinstance(cfg["DEMO_ONLY"], bool) or not isinstance(cfg["KILL"], bool):
        raise ConfigError("DEMO_ONLY and KILL must be true or false")
    for k in POLICY_KEYS:
        if k in ("VAULT_ASSET", "WSTETH", "STETH"):
            if not (isinstance(cfg[k], str) and len(cfg[k]) == 42 and cfg[k].startswith("0x")):
                raise ConfigError(f"{k} must be a 0x address")
        elif isinstance(cfg[k], bool) or not isinstance(cfg[k], (int, float)) or cfg[k] < 0:
            raise ConfigError(f"{k} must be a non-negative number")
    for warn, exit_ in (("BORROWER_WARN", "BORROWER_EXIT"), ("UTIL_WARN", "UTIL_EXIT"),
                        ("ORACLE_WARN_BPS", "ORACLE_EXIT_BPS"), ("WST_WARN_BPS", "WST_EXIT_BPS")):
        if cfg[warn] > cfg[exit_]:
            raise ConfigError(f"{warn} ({cfg[warn]}) must not exceed {exit_} ({cfg[exit_]})")
    if not isinstance(cfg.get("RPC_URLS"), list) or not cfg["RPC_URLS"]:
        raise ConfigError("RPC_URLS must be a non-empty list")
    return cfg, warnings


def policy_fingerprint(cfg: dict[str, Any]) -> str:
    """sha256 over the policy keys, as compact sorted JSON. Addresses are lower-cased."""
    policy = {}
    for k in POLICY_KEYS:
        v = cfg[k]
        policy[k] = v.lower() if isinstance(v, str) and v.startswith("0x") else v
    blob = json.dumps(policy, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()


def check_policy_pin(cfg: dict[str, Any]) -> str:
    """Return the fingerprint, or raise ConfigError if POLICY_SHA256 is set and differs."""
    fp = policy_fingerprint(cfg)
    pin = cfg.get("POLICY_SHA256")
    if pin and pin != fp:
        raise ConfigError(
            f"policy changed: POLICY_SHA256 is {pin[:12]}… but the config's policy is {fp[:12]}…. "
            "If you meant to change a threshold, review it and set POLICY_SHA256 to the new value "
            "(python3 -m keel fingerprint)."
        )
    return fp
