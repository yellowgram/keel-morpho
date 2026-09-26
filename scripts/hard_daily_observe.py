#!/usr/bin/env python3
"""Keel DEMO_ONLY hard daily observe — eth-credit-conservative. Never signs."""
from __future__ import annotations
import json, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import sys

ROOT = Path(__file__).resolve().parents[1]  # repo root
sys.path.insert(0, str(ROOT / "scripts"))
from keel_ops_gates import (  # noqa: E402
    build_observe_gates,
    paste_check_allow_against_table,
    five_way_and,
    recommendation_from_gates,
    o6_flag,
    any_market_pass,
    quiet_idle_fingerprint,
    parse_last_log_fingerprint,
    weekday_miss_note,
    drill_status,
    status_color,
    agent_may_set_kill_on_exit,
    set_kill_in_config,
    refuse_invent_action,
    refuse_invent_allow,
    refuse_invent_vault,
)

CFG_PATH = ROOT / "config.json"
if not CFG_PATH.is_file():
    raise SystemExit(
        "ABORT: config.json missing — copy config.example.json → config.json (DEMO defaults)"
    )
CFG = json.loads(CFG_PATH.read_text())
OUT = ROOT / "eth-credit-conservative"
WETH = CFG["VAULT_ASSET"].lower()
WSTETH = CFG["WSTETH"].lower()
LLTV_MAX = int(CFG["FORBIDDEN_LLTV_WAD_MIN_EXCLUSIVE_B"])
GRAPHQL = CFG["GRAPHQL"]
LLAMA = CFG["LLAMA_PRICES"]
FORBIDDEN_BUCKETS = {
    915000000000000000,
    945000000000000000,
    965000000000000000,
    980000000000000000,
}
NY = ZoneInfo("America/New_York")

WATCHLIST = """
query Watchlist($first: Int!, $skip: Int!) {
  markets(
    first: $first
    skip: $skip
    orderBy: SupplyAssetsUsd
    orderDirection: Desc
    where: { chainId_in: [1], loanAssetAddress_in: ["%s"] }
  ) {
    items {
      marketId
      uniqueKey
      lltv
      oracle { address }
      loanAsset { address symbol decimals }
      collateralAsset { address symbol decimals }
      state {
        utilization borrowAssets supplyAssets liquidityAssets
        borrowAssetsUsd supplyAssetsUsd liquidityAssetsUsd
        supplyApy borrowApy timestamp
      }
    }
    pageInfo { count countTotal }
  }
}
""" % CFG["VAULT_ASSET"]

WATCHLIST_FALLBACK = """
query Watchlist($first: Int!, $skip: Int!) {
  markets(
    first: $first
    skip: $skip
    orderBy: SupplyAssetsUsd
    orderDirection: Desc
    where: { chainId_in: [1], loanAssetAddress_in: ["%s"] }
  ) {
    items {
      marketId
      lltv
      oracle { address }
      loanAsset { address symbol decimals }
      collateralAsset { address symbol decimals }
      state {
        utilization borrowAssets supplyAssets liquidityAssets
        borrowAssetsUsd supplyAssetsUsd liquidityAssetsUsd
        supplyApy borrowApy timestamp
      }
    }
    pageInfo { count countTotal }
  }
}
""" % CFG["VAULT_ASSET"]

POSITIONS = """
query Borrowers($id: String!) {
  marketByUniqueKey(uniqueKey: $id, chainId: 1) {
    uniqueKey
    state { borrowAssets }
    positions(first: 20, orderBy: BorrowShares, orderDirection: Desc, where: { borrowShares_gte: "1" }) {
      items {
        user { address }
        state { borrowAssets borrowShares }
      }
    }
  }
}
"""


def post_gql(query: str, variables: dict | None = None, retries=3):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    last = None
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(
                GRAPHQL, data=body,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode())
            if "errors" in data:
                return None, data["errors"]
            return data["data"], None
        except Exception as e:
            last = e
            time.sleep(1.2 * (i + 1))
    return None, last


def llama_prices():
    url = LLAMA + f"ethereum:{CFG['WSTETH']},ethereum:{CFG['VAULT_ASSET']},ethereum:{CFG['STETH']}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read().decode())
        coins = data.get("coins") or {}
        out = {}
        for label, addr in [("wsteth", CFG["WSTETH"]), ("weth", CFG["VAULT_ASSET"]), ("steth", CFG["STETH"])]:
            hit = None
            for k, v in coins.items():
                if addr.lower() in k.lower():
                    hit = v
                    break
            if not hit:
                return None, f"missing {label}"
            out[label] = hit
        ts = max(int(out[x].get("timestamp") or 0) for x in out)
        return {
            "weth_usd": float(out["weth"]["price"]),
            "wsteth_usd": float(out["wsteth"]["price"]),
            "steth_usd": float(out["steth"]["price"]),
            "wsteth_weth": float(out["wsteth"]["price"]) / float(out["weth"]["price"]),
            "steth_weth": float(out["steth"]["price"]) / float(out["weth"]["price"]),
            "ts": ts,
        }, None
    except Exception as e:
        return None, str(e)


def rpc_steth_per_token():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_call",
        "params": [
            {"to": CFG["WSTETH"], "data": "0xd5391393"},
            "latest",
        ],
    }
    providers = [
        "https://ethereum.publicnode.com",
        "https://eth.drpc.org",
    ]
    last = None
    for url in providers:
        try:
            body = json.dumps(payload).encode()
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read().decode())
            result = data.get("result")
            if not result or result == "0x":
                continue
            bn_payload = {"jsonrpc": "2.0", "id": 2, "method": "eth_blockNumber", "params": []}
            req2 = urllib.request.Request(
                url, data=json.dumps(bn_payload).encode(),
                headers={"Content-Type": "application/json"}, method="POST",
            )
            with urllib.request.urlopen(req2, timeout=15) as r2:
                bn_data = json.loads(r2.read().decode())
            block = int(bn_data.get("result") or "0x0", 16)
            val = int(result, 16) / 1e18
            return {"stEthPerToken": val, "block": block, "provider": url.replace("https://", "")}, None
        except Exception as e:
            last = e
            continue
    return None, str(last) if last else "rpc failed"


def norm_util(u):
    if u is None:
        return None
    u = float(u)
    if u > 1.5:
        u = u / 100.0
    return u


def forbidden_coll(sym: str) -> bool:
    s = sym or ""
    for f in CFG["FORBIDDEN_COLLATERAL"]:
        if f.lower() in s.lower():
            return True
    return False


def mid_of(it):
    return it.get("marketId") or it.get("uniqueKey") or ""


def oracle_of(it):
    o = it.get("oracle") or {}
    if isinstance(o, dict) and o.get("address"):
        return o["address"]
    return it.get("oracleAddress") or "—"


def ineligible_reason(it) -> str | None:
    reasons = []
    sym = (it.get("collateralAsset") or {}).get("symbol") or ""
    coll = ((it.get("collateralAsset") or {}).get("address") or "").lower()
    lltv = int(it.get("lltv") or 0)
    if coll != WSTETH and sym.upper() != "WSTETH":
        reasons.append(f"forbidden_collateral:{sym or coll}")
    if forbidden_coll(sym) and sym.upper() != "WSTETH":
        reasons.append(f"FORBIDDEN_COLLATERAL:{sym}")
    if lltv > LLTV_MAX:
        reasons.append(f"lltv>{LLTV_MAX} (Regime B max 86%)")
    if lltv in FORBIDDEN_BUCKETS:
        reasons.append("forbidden_lltv_bucket")
    return "; ".join(reasons) if reasons else None


def paginate(query):
    all_items = []
    skip = 0
    count_total = None
    last_err = None
    while True:
        data, err = post_gql(query, {"first": 100, "skip": skip})
        if err:
            last_err = err
            return None, last_err, count_total
        mk = data["markets"]
        items = mk["items"] or []
        all_items.extend(items)
        count_total = (mk.get("pageInfo") or {}).get("countTotal") or count_total
        if len(items) < 100 or skip >= 500:
            break
        if count_total and skip + 100 >= min(int(count_total), 600):
            break
        skip += 100
    return all_items, None, count_total


def fmt_util(u):
    return f"{u:.4f}" if u is not None else "—"


def fmt_apy(a):
    if a is None:
        return "—"
    a = float(a)
    if a < 1:
        return f"{a*100:.3f}"
    return f"{a:.3f}"


def fmt_usd(u):
    if u is None:
        return "—"
    try:
        return f"{float(u):,.0f}"
    except Exception:
        return str(u)


def main():
    now = datetime.now(timezone.utc)
    iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    ny = now.astimezone(NY)
    ny_label = ny.strftime("%Y-%m-%d %H:%M %Z")
    fetch_errors = []
    graphql_ok = llama_ok = rpc_ok = False

    # --- Entry gates: brief/config/mandate/DEMO/KILL/keys ---
    gates = build_observe_gates(ROOT, CFG)
    print(f"DEMO_ONLY: {gates.demo_only}")
    print(f"KILL: {gates.kill}")
    print(f"mandate_hash: {gates.mandate_hash}")
    if not gates.config_readable:
        raise SystemExit("ABORT: config.json unreadable")
    if not gates.brief_present:
        raise SystemExit("ABORT: BRIEF_v1.1.md missing — refuse observe")
    if not gates.mandate_match():
        raise SystemExit(
            f"ABORT: mandate_hash mismatch config={gates.mandate_hash!r} "
            f"file={gates.mandate_file_hash!r} — no pack overwrite"
        )
    if gates.key_env_hits:
        raise SystemExit(
            f"ABORT: DEMO_ONLY process gate — refuse keys in env: {gates.key_env_hits}"
        )
    if gates.errors and any("mismatch" in e or "missing" in e for e in gates.errors):
        # mismatch already aborted; other hard errors
        hard = [e for e in gates.errors if "key env" in e]
        if hard:
            raise SystemExit("ABORT: " + "; ".join(hard))

    # Quiet-if-IDLE / missed-observe vs prior log
    log_path = OUT / "log.md"
    prior_fp, prior_ts = (None, None)
    if log_path.is_file():
        prior_fp, prior_ts = parse_last_log_fingerprint(log_path.read_text())
    miss_note = weekday_miss_note(prior_ts, now)

    all_items, gql_err, count_total = paginate(WATCHLIST)
    stale_from_cache = False
    if all_items is None:
        all_items, gql_err2, count_total = paginate(WATCHLIST_FALLBACK)
        if all_items is None:
            fetch_errors.append(f"graphql:{gql_err}")
            fetch_errors.append(f"graphql_fallback:{gql_err2}")
            # HOLD/STALE: reuse last observe_raw markets if present — never invent, never clear ALLOW
            raw_path = OUT / "observe_raw.json"
            all_items = []
            if raw_path.is_file():
                try:
                    prev = json.loads(raw_path.read_text())
                    # Cannot perfectly rebuild GraphQL items; mark stale and keep eligible count from prev
                    stale_from_cache = True
                    fetch_errors.append("graphql:using_last_observe_raw_STALE_marker")
                    # Carry prior counts into recommendation path via empty items + note
                    count_total = prev.get("count_total")
                except Exception as e:
                    fetch_errors.append(f"stale_cache:{e}")
            all_items = []
        else:
            graphql_ok = True
    else:
        graphql_ok = True

    weth_n = len(all_items)
    wst_rows = []
    for it in all_items:
        coll = ((it.get("collateralAsset") or {}).get("address") or "").lower()
        sym = ((it.get("collateralAsset") or {}).get("symbol") or "")
        if coll == WSTETH or sym.upper() == "WSTETH":
            wst_rows.append(it)

    llama, lerr = llama_prices()
    if llama:
        llama_ok = True
        data_age_llama = int(now.timestamp()) - int(llama["ts"])
    else:
        fetch_errors.append(f"llama:{lerr}")
        data_age_llama = None
        llama = {
            "weth_usd": None, "wsteth_usd": None, "steth_usd": None,
            "wsteth_weth": None, "steth_weth": None, "ts": 0,
        }

    rpc, rerr = rpc_steth_per_token()
    if rpc:
        rpc_ok = True
    else:
        fetch_errors.append(f"rpc:{rerr}")
        rpc = {"stEthPerToken": None, "block": None, "provider": None}

    table_rows = []
    eligible = []
    for it in wst_rows:
        lltv = int(it.get("lltv") or 0)
        lltv_pct = lltv / 1e16
        reason = ineligible_reason(it)
        st = it.get("state") or {}
        util = norm_util(st.get("utilization"))
        supply_apy = st.get("supplyApy")
        supply_usd = st.get("supplyAssetsUsd")
        ora = oracle_of(it)
        mid = mid_of(it)
        eligible_flag = reason is None
        row = {
            "marketId": mid,
            "lltv": lltv,
            "lltv_pct": lltv_pct,
            "eligible": eligible_flag,
            "ineligible_reason": reason or "—",
            "util": util,
            "supplyApy": supply_apy,
            "supplyUsd": supply_usd,
            "oracle": ora,
        }
        o_flags = []
        if util is not None:
            if util > CFG["UTIL_EXIT"]:
                o_flags.append("O2_EXIT")
            elif util > CFG["UTIL_WARN"]:
                o_flags.append("O2_WARN")
            else:
                o_flags.append("O2_PASS")
        else:
            o_flags.append("O2_PARTIAL")

        top_pct = None
        pdata, perr = post_gql(POSITIONS, {"id": mid})
        if pdata and not perr:
            try:
                m = pdata.get("marketByUniqueKey") or {}
                borrow = float((m.get("state") or {}).get("borrowAssets") or 0)
                pos = ((m.get("positions") or {}).get("items")) or []
                if pos and borrow > 0:
                    top = float(((pos[0].get("state") or {}).get("borrowAssets")) or 0)
                    top_pct = top / borrow
            except Exception:
                pass
        if top_pct is None:
            o_flags.append("O1_PARTIAL")
        else:
            if top_pct > CFG["BORROWER_EXIT"]:
                o_flags.append("O1_EXIT")
            elif top_pct > CFG["BORROWER_WARN"]:
                o_flags.append("O1_WARN")
            else:
                o_flags.append("O1_PASS")

        o_flags.append("O3_PARTIAL")
        if rpc_ok and llama.get("wsteth_usd") and llama.get("steth_usd"):
            implied = llama["wsteth_usd"] / llama["steth_usd"]
            rpc_v = rpc["stEthPerToken"]
            if rpc_v and implied:
                bps = abs(implied - rpc_v) / rpc_v * 10000
                if bps > CFG["WST_EXIT_BPS"]:
                    o_flags.append(f"O4_EXIT({bps:.1f}bps)")
                elif bps > CFG["WST_WARN_BPS"]:
                    o_flags.append(f"O4_WARN({bps:.1f}bps)")
                else:
                    o_flags.append(f"O4_PASS({bps:.1f}bps)")
            else:
                o_flags.append("O4_PARTIAL")
        else:
            o_flags.append("O4_PARTIAL")
        o_flags.append("O5_N/A")
        ts = int(st.get("timestamp") or 0)
        if ts:
            age = max(0, int(now.timestamp()) - ts)  # clamp clock skew
            o_flags.append(o6_flag(age, int(CFG["STALE_S"])))
        else:
            o_flags.append(o6_flag(None, int(CFG["STALE_S"])))
        o_flags.append("O7_N/A")
        row["o_flags"] = o_flags
        row["top_borrower_pct"] = top_pct
        table_rows.append(row)
        if eligible_flag:
            eligible.append(row)

    amendments = CFG.get("AMENDMENTS") or []
    table_rows.sort(key=lambda r: float(r["supplyUsd"] or 0), reverse=True)

    # --- ALLOW paste-check against latest table ---
    market_keys = {r["marketId"] for r in table_rows}
    eligible_keys = {r["marketId"] for r in eligible}
    allow_accepted, allow_rejected = paste_check_allow_against_table(
        list(gates.allow_rows),
        lltv_max_wad=LLTV_MAX,
        market_rel_cap=float(CFG["MARKET_REL_CAP"]),
        market_table_keys=market_keys,
        regime_b_eligible_keys=eligible_keys,
        forbidden_collateral=list(CFG.get("FORBIDDEN_COLLATERAL") or []),
    )
    gates.allow_accepted = allow_accepted
    gates.allow_rejected = allow_rejected

    market_pass = any_market_pass(table_rows)
    vault_set = bool(gates.vault_address)
    five = five_way_and(
        allow_accepted_nonempty=len(allow_accepted) > 0,
        market_pass=market_pass,
        vault_set=vault_set,
        demo_only=gates.demo_only,
        kill=gates.kill,
    )
    # DEMO gate: never invent ACTION / ALLOW / vault
    _ = refuse_invent_action()
    _ = refuse_invent_allow()
    _ = refuse_invent_vault()

    inconsistent = gates.inconsistent_demo_open()
    recommendation, rationale = recommendation_from_gates(
        five_way=five,
        kill=gates.kill,
        graphql_ok=graphql_ok,
        demo_only=gates.demo_only,
        eligible_n=len(eligible),
        inconsistent=inconsistent,
    )
    # Under DEMO_ONLY, never emit ALLOCATE_* even if somehow five-way true
    if gates.demo_only and recommendation.startswith("ALLOCATE"):
        recommendation = "IDLE_ALL"
        rationale = "DEMO_ONLY hard gate — ALLOCATE frozen; " + rationale

    # Agent may set KILL on EXIT-class trips (never clear)
    all_flags = []
    for r in table_rows:
        all_flags.extend(r.get("o_flags") or [])
    if agent_may_set_kill_on_exit(all_flags) and not gates.kill:
        # Only auto-set KILL if there is open size (live); under DEMO idle, note only
        if float(gates.open_size_weth or 0) > 0:
            set_kill_in_config(ROOT / "config.json", True)
            gates.kill = True
            recommendation, rationale = recommendation_from_gates(
                five_way=five, kill=True, graphql_ok=graphql_ok,
                demo_only=gates.demo_only, eligible_n=len(eligible),
                inconsistent=inconsistent,
            )
        else:
            gates.warnings.append("EXIT-class O* seen while idle/DEMO — KILL not auto-set (no open size)")

    idle = recommendation in ("IDLE_ALL", "HOLD")
    drill = drill_status(idle=idle and float(gates.open_size_weth or 0) == 0,
                         open_alloc=float(gates.open_size_weth or 0) > 0)
    # Checklist: while idle still record PASS_DRILL/SKIP_IDLE — use SKIP_IDLE when no open alloc
    if float(gates.open_size_weth or 0) == 0:
        drill = "SKIP_IDLE"

    blockers = []
    if gates.demo_only:
        blockers.append("DEMO_ONLY=true")
    if gates.kill:
        blockers.append("KILL=true")
    if not vault_set:
        blockers.append("VAULT_ADDRESS null")
    if len(allow_accepted) == 0:
        blockers.append("ALLOW empty/rejected")
    if len(eligible) == 0:
        blockers.append(f"RegimeB_eligible=0")
    if not market_pass:
        blockers.append("no market PASS score")
    if allow_rejected:
        blockers.append(f"ALLOW_rejected={len(allow_rejected)}")
    if inconsistent:
        blockers.append("INCONSISTENT DEMO+open_size")


    lines = []
    for r in table_rows:
        lines.append(
            "| `{mid}` | {lltv} | {pct:.2f} | {elig} | {reason} | {util} | {apy} | {usd} | `{ora}` |".format(
                mid=r["marketId"],
                lltv=r["lltv"],
                pct=r["lltv_pct"],
                elig="YES" if r["eligible"] else "NO",
                reason=r["ineligible_reason"],
                util=fmt_util(r["util"]),
                apy=fmt_apy(r["supplyApy"]),
                usd=fmt_usd(r["supplyUsd"]),
                ora=r["oracle"],
            )
        )

    scoreboard_lines = []
    for r in table_rows:
        if r["top_borrower_pct"] is None:
            top_s = "—"
        else:
            top_s = f"{r['top_borrower_pct']:.4f}"
        scoreboard_lines.append(
            "| `{mid}…` | {flags} | {top} |".format(
                mid=r["marketId"][:18],
                flags="; ".join(r["o_flags"]),
                top=top_s,
            )
        )

    status = status_color(
        graphql_ok=graphql_ok,
        mandate_ok=gates.mandate_match() and gates.brief_present,
        fetch_partial=bool(fetch_errors),
        inconsistent=inconsistent,
    )
    if not graphql_ok:
        recommendation = "HOLD"
        rationale = (
            "HALT_FETCH — GraphQL failed; HOLD/STALE last-known; never clear ALLOW/DEMO/KILL."
            + (" (stale_cache_marker=true)" if stale_from_cache else "")
        )

    px_weth = f"{llama['weth_usd']:.4f}" if llama.get("weth_usd") else "—"
    px_wst = f"{llama['wsteth_usd']:.4f}" if llama.get("wsteth_usd") else "—"
    px_st = f"{llama['steth_usd']:.4f}" if llama.get("steth_usd") else "—"
    wst_weth = f"{llama['wsteth_weth']:.8f}" if llama.get("wsteth_weth") else "—"
    st_weth = f"{llama['steth_weth']:.8f}" if llama.get("steth_weth") else "—"
    st_per = f"{rpc['stEthPerToken']:.10f}" if rpc.get("stEthPerToken") else "—"

    market_table = "\n".join(lines) if lines else "| — | — | — | — | NO_DATA | — | — | — | — |"
    score_table = "\n".join(scoreboard_lines) if scoreboard_lines else "| — | NO_DATA | — |"

    allow_n = len(allow_accepted)
    allow_rej_n = len(allow_rejected)
    allow_rej_note = "; ".join(f"{r.unique_key[:10]}…:{r.reject_reason}" for r in allow_rejected[:5]) or "none"
    vault_disp = gates.vault_address if gates.vault_address else "null"
    brief_disp = "present" if gates.brief_present else "MISSING"
    demo_disp = "true" if gates.demo_only else "false"
    kill_disp = "true" if gates.kill else "false"
    five_disp = five.detail
    blockers_md = "\n".join(f"{i+1}. {b}" for i, b in enumerate(blockers)) or "1. (none)"
    miss_disp = miss_note or "none"
    quiet_fp = quiet_idle_fingerprint(
        recommendation, blockers, [r["marketId"] for r in eligible]
    )
    quiet = bool(prior_fp and prior_fp == quiet_fp and recommendation == "IDLE_ALL")
    caps = (
        f"BOOK={CFG.get('BOOK_NOTIONAL_CAP_WETH')} PER_MKT={CFG.get('PER_MARKET_CAP_WETH')} "
        f"MAX_OPEN={CFG.get('MAX_MARKETS_OPEN')} DUST={CFG.get('DUST_CAP_WETH')}"
    )
    inconsistent_banner = (
        "\n**INCONSISTENT — EXIT PRIORITY** (DEMO_ONLY with open live size)\n"
        if inconsistent else ""
    )

    pack = f"""# ALLOCATOR PACK | {iso} ({ny_label})
STATUS: {status} — BRIEF_v1.1.md {brief_disp}; DEMO_ONLY={demo_disp}; KILL={kill_disp}
MANDATE: ETH Credit Conservative | Regime B | `{CFG['mandate_hash']}`
DEMO_ONLY: {demo_disp} | KILL: {kill_disp} | Never sign | Never keys | Never auto-ALLOW | Never invent ACTION | Never price BMNR/BMNU/CoinDCX
{inconsistent_banner}
## Book / vault
- REFERENCE_BOOK_ID: `{CFG['REFERENCE_BOOK_ID']}` | REFERENCE_UNITS: {CFG['REFERENCE_UNITS']} | open_size_weth: {gates.open_size_weth} | idle_pct: **{"100" if gates.open_size_weth == 0 else "n/a"}**
- VAULT_ADDRESS: **{vault_disp}** | ALLOW accepted: **{allow_n}** | ALLOW rejected: **{allow_rej_n}** | AMENDMENTS: {amendments if amendments else 'none'} | B2: none
- BRIEF_v1.1.md: **{brief_disp}** | REGIME: **B** locked | size_caps: {caps}
- five_way_AND: `{five_disp}`
- drill: **{drill}** (P_WSTETH path) | quiet_if_IDLE: {quiet} | missed_observe: {miss_disp}

## Prices (Llama + optional RPC)
| WETH | wstETH | stETH | wstETH/WETH | stETH/WETH | stEthPerToken (RPC) | block |
|---:|---:|---:|---:|---:|---:|---:|
| {px_weth} | {px_wst} | {px_st} | {wst_weth} | {st_weth} | {st_per} | {rpc.get('block') or '—'} |

- Llama age_s: {data_age_llama if data_age_llama is not None else '—'} | RPC provider: {rpc.get('provider') or '—'}
- fetch: graphql_ok={graphql_ok} llama_ok={llama_ok} rpc_ok={rpc_ok}
- fetch_errors: {fetch_errors if fetch_errors else 'none'}

## All wstETH–WETH markets (mandatory table)
| marketId (Morpho uniqueKey) | lltv (wad) | lltv% | RegimeB eligible | ineligible_reason | util | supplyApy% | supplyUsd | oracle |
|---|---:|---:|:---:|---|---:|---:|---:|---|
{market_table}

**Counts:** WETH_loan_markets={weth_n} | wstETH–WETH={len(wst_rows)} | RegimeB_eligible={len(eligible)} | ALLOW_accepted={allow_n} | ALLOW_rejected={allow_rej_n} | countTotal={count_total}
ALLOW_rejected_detail: {allow_rej_note}

## Scoreboard O1–O7 (PARTIAL where data missing)
| marketId | flags | top_borrower_pct |
|---|---|---:|
{score_table}

Score aggregate: ALLOCATE only if five-way AND (ALLOW ∩ PASS ∩ VAULT ∩ !DEMO_ONLY ∩ !KILL). O6 age>STALE_S → FAIL. Flag **PARTIAL** on O1/O3/O4 as needed; O5/O7 N/A while idle.

## Recommendation
# **{recommendation}**
Rationale: {rationale}
ACTION: human-only — observe refuses invent (`action_human: PENDING`). REFERENCE_ONLY deallocate drafts only; ALLOCATE drafts frozen while DEMO or KILL.

## Blockers
{blockers_md}

## Next human actions
- Paste B2 amendment only if Regime B / idle default should change
- Paste ALLOW rows (format in allowlist.md) when a ≤86% LLTV Regime-B-eligible market exists
- Set VAULT_ADDRESS only after control proven; flip DEMO only via live-exit tick-sheet (`ops/LIVE_EXIT_GATE_TICKSHEET.md`)
- Clear KILL only as human (agent may set on EXIT-class with open size)

## Schedule
Weekday observe 08:00 America/New_York (`keel_daily_observe_once.sh`). Quiet-if-IDLE when rec+blockers+eligible unchanged. SLA: `ops/SLAS.md`.
"""
    (OUT / "pack.md").write_text(pack)

    ineligible_dump = [
        {
            "marketId": r["marketId"],
            "lltv": r["lltv"],
            "lltv_pct": r["lltv_pct"],
            "reason": r["ineligible_reason"],
        }
        for r in table_rows
        if not r["eligible"]
    ]

    # Quiet-if-IDLE: still append, but short line when unchanged
    if quiet:
        log = f"""
### LOG | {iso} ({ny_label})
quiet_if_IDLE: true
quiet_fp: {quiet_fp}
mandate_hash: {CFG['mandate_hash']}
demo_only: {str(gates.demo_only).lower()}
kill: {str(gates.kill).lower()}
recommendation: {recommendation}
eligible_regime_B: {json.dumps([r['marketId'] for r in eligible])}
blockers: {json.dumps(blockers)}
drill: {drill}
missed_observe: {miss_disp}
fetch: {{graphql_ok: {str(graphql_ok).lower()}, llama_ok: {str(llama_ok).lower()}, rpc_ok: {str(rpc_ok).lower()}}}
note: unchanged vs prior weekday fingerprint — not progress; IDLE is success
"""
    else:
        log = f"""
### LOG | {iso} ({ny_label})
mandate_hash: {CFG['mandate_hash']}
demo_only: {str(gates.demo_only).lower()}
kill: {str(gates.kill).lower()}
regime: B
brief: BRIEF_v1.1.md {brief_disp}
five_way: {five_disp}
quiet_fp: {quiet_fp}
missed_observe: {miss_disp}
fetch: {{graphql_ok: {str(graphql_ok).lower()}, llama_ok: {str(llama_ok).lower()}, rpc_ok: {str(rpc_ok).lower()}, rpc_provider: {rpc.get('provider')}, data_age_s_llama: {data_age_llama}}}
fetch_errors: {json.dumps([str(e) for e in fetch_errors])}
weth_loan_markets: {weth_n}
wsteth_weth_markets: {len(wst_rows)}
eligible_regime_B: {json.dumps([r['marketId'] for r in eligible])}
ineligible_n: {len(ineligible_dump)}
ineligible: {json.dumps(ineligible_dump)}
allow_accepted: {allow_n}
allow_rejected: {json.dumps([{"key": r.unique_key, "reason": r.reject_reason} for r in allow_rejected])}
prices: {{weth_usd: {llama.get('weth_usd')}, wsteth_usd: {llama.get('wsteth_usd')}, steth_usd: {llama.get('steth_usd')}, wsteth_weth: {llama.get('wsteth_weth')}, steth_weth: {llama.get('steth_weth')}, stEthPerToken: {rpc.get('stEthPerToken')}, block: {rpc.get('block')}}}
scoreboard: O1–O7 as pack; STALE_S={CFG['STALE_S']} → O6_FAIL blocks PASS
ref_idle_pct: 100
ref_alloc: []
recommendation: {recommendation}
rationale: {rationale}
draft_actions: [{{fn: none, note: REFERENCE_ONLY — ALLOCATE frozen under DEMO/KILL, reference_only: true}}]
action_human: PENDING
tx_hash: none
blockers: {json.dumps(blockers)}
drill: {drill}
counts: weth={weth_n} wsteth={len(wst_rows)} eligible={len(eligible)} pass={1 if market_pass else 0} allow_ok={allow_n}
warnings: {json.dumps(gates.warnings)}
"""

    with (OUT / "log.md").open("a") as f:
        f.write(log)

    raw = {
        "iso": iso,
        "ny_label": ny_label,
        "mandate_hash": CFG["mandate_hash"],
        "demo_only": gates.demo_only,
        "kill": gates.kill,
        "five_way": five.detail,
        "drill": drill,
        "quiet_if_IDLE": quiet,
        "missed_observe": miss_disp,
        "weth_markets": weth_n,
        "count_total": count_total,
        "wsteth_markets": len(wst_rows),
        "eligible": len(eligible),
        "ineligible": ineligible_dump,
        "allow_accepted": allow_n,
        "allow_rejected": [{"key": r.unique_key, "reason": r.reject_reason} for r in allow_rejected],
        "table_rows": table_rows,
        "llama": llama,
        "rpc": rpc,
        "graphql_ok": graphql_ok,
        "llama_ok": llama_ok,
        "rpc_ok": rpc_ok,
        "fetch_errors": [str(e) for e in fetch_errors],
        "recommendation": recommendation,
        "status": status,
        "all_items_sample_keys": list(all_items[0].keys()) if all_items else [],
    }
    (OUT / "observe_raw.json").write_text(json.dumps(raw, indent=2, default=str))

    print(json.dumps({
        "ok": True,
        "iso": iso,
        "ny_label": ny_label,
        "DEMO_ONLY": gates.demo_only,
        "KILL": gates.kill,
        "status": status,
        "recommendation": recommendation,
        "five_way": five.detail,
        "drill": drill,
        "quiet_if_IDLE": quiet,
        "weth_n": weth_n,
        "wst_n": len(wst_rows),
        "eligible": len(eligible),
        "prices": {
            "weth": llama.get("weth_usd"),
            "wsteth": llama.get("wsteth_usd"),
            "steth": llama.get("steth_usd"),
        },
        "rpc_ok": rpc_ok,
        "graphql_ok": graphql_ok,
        "llama_ok": llama_ok,
        "fetch_errors": [str(e)[:300] for e in fetch_errors],
        "paths": [str(OUT / "pack.md"), str(OUT / "log.md"), str(OUT / "observe_raw.json")],
    }, indent=2))


if __name__ == "__main__":
    main()
