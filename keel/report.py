"""Render a run as the markdown report ("pack") and a one-line JSON log entry."""
from __future__ import annotations

import json
from datetime import datetime
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")


def _pct(x) -> str:
    return "—" if x is None else f"{float(x):.1%}"


def _usd(x) -> str:
    return "—" if x is None else f"${float(x):,.0f}"


def _cell(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def render_pack(r: dict) -> str:
    t = datetime.strptime(r["time_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=ZoneInfo("UTC"))
    ny = t.astimezone(NY).strftime("%Y-%m-%d %H:%M %Z")
    L = [
        f"# Keel report — {r['time_utc']} ({ny})",
        "",
        f"## Recommendation: {r['recommendation']}",
        "",
        r["rationale"],
    ]
    if r["allocatable"]:
        L += ["", "Allowlisted markets that pass every check:", *[f"- `{m}`" for m in r["allocatable"]]]
    L += ["", "Keel does not sign or move funds. Any transaction is yours to make.", ""]
    if r["blockers"]:
        L += ["### Blockers", *[f"- {b}" for b in r["blockers"]], ""]

    L += [
        "## Markets (WETH loans against wstETH, Ethereum mainnet)",
        "",
        "| Market | LLTV | Eligible | Ready | Utilization | Supply APY | Supply |",
        "|---|---:|:---:|:---:|---:|---:|---:|",
    ]
    for m in r["markets"]:
        L.append(f"| `{m['marketId'][:10]}…` | {m['lltv'] / 1e16:.1f}% | {'yes' if m['eligible'] else 'no'} | "
                 f"{'yes' if m['ready'] else 'no'} | {_pct(m['utilization'])} | {_pct(m['supplyApy'])} | {_usd(m['supplyUsd'])} |")
    if not r["markets"]:
        L.append("| (no data) | | | | | | |")
    L.append("")
    for m in r["markets"]:
        L += [f"### `{m['marketId']}`", ""]
        if m["ineligible_reasons"]:
            L.append("Not eligible: " + "; ".join(m["ineligible_reasons"]) + ".")
            L.append("")
        L += ["| Check | Result | Detail |", "|---|---|---|"]
        L += [f"| {c['name']} | {c['status']} | {_cell(c['detail'])} |" for c in m["checks"]]
        L.append("")

    p = r["prices"]
    L += ["## Inputs", ""]
    if p:
        L.append(f"- Prices (DefiLlama): wstETH {_usd(p['WSTETH']['usd'])}, WETH {_usd(p['VAULT_ASSET']['usd'])}, "
                 f"stETH {_usd(p['STETH']['usd'])}")
    else:
        L.append("- Prices: unavailable")
    L.append(f"- stETH per wstETH (on-chain): {r['steth_per_wsteth']:.6f}" if r["steth_per_wsteth"] else
             "- stETH per wstETH (on-chain): unavailable")
    L += [
        f"- DEMO_ONLY: {str(r['demo_only']).lower()} · KILL: {str(r['kill']).lower()} · "
        f"VAULT_ADDRESS: {r['vault_address'] or 'not set'} · OPEN_SIZE_WETH: {r['open_size_weth']}",
        f"- Allowlist: {len(r['allow_accepted'])} accepted, {len(r['allow_rejected'])} rejected",
    ]
    for a in r["allow_rejected"]:
        L.append(f"  - rejected `{_cell(a['raw'])[:80]}`: {_cell(a['reject_reason'])}")
    L.append(f"- Policy fingerprint: `{r['policy_sha256']}`")
    if r["errors"]:
        L += ["", "### Data problems", *[f"- {_cell(e)[:300]}" for e in r["errors"]]]
    return "\n".join(L) + "\n"


def log_entry(r: dict) -> str:
    keep = {k: r[k] for k in ("time_utc", "recommendation", "allocatable", "blockers", "policy_sha256",
                              "demo_only", "kill", "fetch_ok", "errors")}
    keep["markets"] = [{"marketId": m["marketId"], "eligible": m["eligible"], "ready": m["ready"],
                        "checks": {c["name"]: c["status"] for c in m["checks"]}} for m in r["markets"]]
    return json.dumps(keep, separators=(",", ":")) + "\n"
