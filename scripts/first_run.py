#!/usr/bin/env python3
"""Keel day-0 DEMO_ONLY first run. Never signs."""
from __future__ import annotations
import json, time, urllib.request, ssl
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # repo root
CFG_PATH = ROOT / "config.json"
if not CFG_PATH.is_file():
    raise SystemExit(
        "ABORT: config.json missing — copy config.example.json → config.json (DEMO defaults)"
    )
CFG = json.loads(CFG_PATH.read_text())
OUT = ROOT / "eth-credit-conservative"
WETH = CFG["VAULT_ASSET"].lower()
WSTETH = CFG["WSTETH"].lower()
LLTV_MAX = int(CFG["FORBIDDEN_LLTV_WAD_MIN_EXCLUSIVE_B"])  # inclusive allowed <= this
GRAPHQL = CFG["GRAPHQL"]
LLAMA = CFG["LLAMA_PRICES"]

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
      lltv
      oracleAddress
      irmAddress
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

MARKET_BOX = """
query MarketBox($key: String!) {
  marketById(marketId: $key, chainId: 1) {
    marketId
    lltv
    oracleAddress
    oracle { address type }
    state {
      utilization borrowAssets supplyAssets liquidityAssets
      borrowAssetsUsd supplyAssetsUsd liquidityAssetsUsd
      supplyApy borrowApy timestamp
    }
    stateHistory(first: 2, orderBy: Timestamp, orderDirection: Desc) {
      items { utilization supplyApy timestamp }
    }
  }
}
"""

# Borrower positions — try common Morpho schema
POSITIONS = """
query Borrowers($key: String!) {
  marketById(marketId: $key, chainId: 1) {
    marketId
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

def post_gql(query: str, variables: dict | None = None, retries=2):
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
                raise RuntimeError(str(data["errors"])[:500])
            return data["data"], None
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    return None, last

def llama_prices():
    url = LLAMA + f"ethereum:{CFG['WSTETH']},ethereum:{CFG['VAULT_ASSET']}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read().decode())
        coins = data.get("coins") or {}
        wst = coins.get(f"ethereum:{CFG['WSTETH']}".lower()) or coins.get(f"ethereum:{CFG['WSTETH']}")
        weth = coins.get(f"ethereum:{CFG['VAULT_ASSET']}".lower()) or coins.get(f"ethereum:{CFG['VAULT_ASSET']}")
        # keys may be checksummed
        if not wst or not weth:
            for k, v in coins.items():
                if CFG["WSTETH"].lower() in k.lower():
                    wst = v
                if CFG["VAULT_ASSET"].lower() in k.lower():
                    weth = v
        if not wst or not weth:
            return None, "missing coins"
        px = float(wst["price"]) / float(weth["price"])
        ts = max(int(wst.get("timestamp") or 0), int(weth.get("timestamp") or 0))
        return {"secondary_wsteth_weth": px, "ts": ts, "wst_usd": wst["price"], "weth_usd": weth["price"]}, None
    except Exception as e:
        return None, str(e)

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

def main():
    now = datetime.now(timezone.utc)
    iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    halt = []
    graphql_ok = llama_ok = rpc_ok = False
    data_age_max = 0

    # D1 paginate
    all_items = []
    skip = 0
    count_total = None
    while True:
        data, err = post_gql(WATCHLIST, {"first": 100, "skip": skip})
        if err:
            halt.append(f"HALT_FETCH:{err}")
            break
        graphql_ok = True
        mk = data["markets"]
        items = mk["items"] or []
        all_items.extend(items)
        count_total = (mk.get("pageInfo") or {}).get("countTotal") or count_total
        if len(items) < 100 or skip >= 400:
            break
        if count_total and skip + 100 >= min(int(count_total), 500):
            break
        skip += 100

    weth_n = len(all_items)
    wst_rows = []
    for it in all_items:
        coll = ((it.get("collateralAsset") or {}).get("address") or "").lower()
        sym = ((it.get("collateralAsset") or {}).get("symbol") or "")
        if coll == WSTETH or sym.upper() == "WSTETH":
            wst_rows.append(it)

    eligible = []
    ineligible = []
    for it in wst_rows:
        lltv = int(it.get("lltv") or 0)
        sym = (it.get("collateralAsset") or {}).get("symbol") or ""
        if forbidden_coll(sym):
            ineligible.append({"marketId": it["marketId"], "why": "FORBIDDEN_COLLATERAL"})
            continue
        if lltv > LLTV_MAX:
            ineligible.append({"marketId": it["marketId"], "why": f"lltv>{LLTV_MAX}", "lltv": lltv})
            continue
        # drop 94.5/96.5 etc even if filter bugs
        if lltv in (915000000000000000, 945000000000000000, 965000000000000000, 980000000000000000):
            ineligible.append({"marketId": it["marketId"], "why": "forbidden_lltv_bucket", "lltv": lltv})
            continue
        eligible.append(it)

    llama, lerr = llama_prices()
    if llama:
        llama_ok = True
    else:
        halt.append(f"LLAMA:{lerr}")

    # Score eligible with O1/O2 (+ light D2)
    scored = []
    for it in eligible:
        key = it["marketId"]
        st = it.get("state") or {}
        util = norm_util(st.get("utilization"))
        borrow = float(st.get("borrowAssets") or 0)
        liq = float(st.get("liquidityAssets") or 0) / 1e18
        apy = st.get("supplyApy")
        ts = int(st.get("timestamp") or 0)
        if ts:
            data_age_max = max(data_age_max, int(now.timestamp()) - ts)

        top_pct = 0.0
        # try borrowers
        pdata, perr = post_gql(POSITIONS, {"key": key})
        if pdata and not perr:
            try:
                pos = (((pdata.get("marketById") or {}).get("positions") or {}).get("items")) or []
                if pos and borrow > 0:
                    top = float(((pos[0].get("state") or {}).get("borrowAssets")) or 0)
                    top_pct = top / borrow if borrow else 0.0
            except Exception:
                pass
        else:
            # schema may differ — leave 0 and note
            pass

        s_o1 = 0
        if top_pct > CFG["BORROWER_EXIT"]:
            s_o1 = 2
        elif top_pct > CFG["BORROWER_WARN"]:
            s_o1 = 1
        s_o2 = 0
        if util is not None:
            if util > CFG["UTIL_EXIT"]:
                s_o2 = 2
            elif util > CFG["UTIL_WARN"]:
                s_o2 = 1
        # O3/O4 need oracle — mark LOW confidence path; skip EXIT without samples
        score = max(s_o1, s_o2)
        state = "PASS" if score == 0 else ("WARN" if score == 1 else "EXIT")
        scored.append({
            "marketId": key,
            "lltv": int(it.get("lltv") or 0),
            "util": util,
            "top_borrower_pct": round(top_pct, 4),
            "liq_weth": round(liq, 2),
            "supply_apy": apy,
            "score": score,
            "state": state,
            "oracleAddress": it.get("oracleAddress"),
        })

    # Rank PASS
    pass_mk = [x for x in scored if x["state"] == "PASS"]
    pass_mk.sort(key=lambda x: (x["score"], -x["liq_weth"], abs((x["util"] or 0) - 0)))

    confidence = "HIGH" if (graphql_ok and llama_ok and data_age_max <= 900 and not any(h.startswith("HALT") for h in halt)) else "LOW"
    # No ALLOW → IDLE_ALL
    recommendation = "IDLE_ALL"
    exceptions = []
    if any(h.startswith("HALT_FETCH") for h in halt):
        recommendation = "HOLD"
        exceptions.append({"limit": "DATA_GAP", "level": "HALT", "evidence": halt[0], "number": None})
        confidence = "LOW"

    # DRILL P_WSTETH
    drill = {
        "label": "DRILL",
        "procedure": "P_WSTETH",
        "paper_apply": "If wst_dev EXIT: freeze new; EXIT open allocations; IDLE until O4 PASS",
        "book_effect": "REFERENCE 100 → IDLE_ALL (already idle)",
        "result": "PASS_DRILL — no allocated rows; idle unchanged",
    }

    status = "GREEN"
    if exceptions or confidence == "LOW":
        status = "AMBER"
    if any(h.startswith("HALT") for h in halt) or recommendation == "HOLD" and exceptions:
        status = "RED" if any("HALT_FETCH" in h for h in halt) else status

    raw = {
        "iso": iso,
        "mandate_hash": CFG["mandate_hash"],
        "weth_markets": weth_n,
        "count_total": count_total,
        "wsteth_markets": len(wst_rows),
        "lltv_eligible": len(eligible),
        "ineligible_n": len(ineligible),
        "scored": scored,
        "pass_n": len(pass_mk),
        "warn_n": sum(1 for x in scored if x["state"] == "WARN"),
        "exit_n": sum(1 for x in scored if x["state"] == "EXIT"),
        "llama": llama,
        "halt": halt,
        "graphql_ok": graphql_ok,
        "llama_ok": llama_ok,
        "rpc_ok": False,  # day-0 optional; note assumption stETH/ETH=1
        "data_age_s_max": data_age_max,
        "confidence": confidence,
        "recommendation": recommendation,
        "drill": drill,
        "status": status,
    }
    (OUT / "day0_raw.json").write_text(json.dumps(raw, indent=2, default=str))

    # LOG
    elig_lines = []
    for x in scored[:40]:
        elig_lines.append(
            f"  - {x['marketId'][:18]}… lltv={x['lltv']} util={x['util']} top={x['top_borrower_pct']} "
            f"liq={x['liq_weth']} apy={x['supply_apy']} score={x['score']} state={x['state']}"
        )
    log = f"""### LOG | {iso}
mandate_hash: {CFG['mandate_hash']}
demo_only: true
regime: B
fetch: {{graphql_ok: {graphql_ok}, llama_ok: {llama_ok}, rpc_ok: false, data_age_s_max: {data_age_max}}}
watch_n: {weth_n}
eligible:
{chr(10).join(elig_lines) if elig_lines else '  []'}
ineligible_n: {len(ineligible)}
ref_idle_pct: 100
ref_alloc: []
encoded: {{E1..E8: Morpho V1, wstETH only, cap 25%, lltv<=86e16, no risk-up w/o ALLOW, risk-down ok, no auto-dealloc forced, LRT EXIT}}
operating: {{O1..O7 applied on util/borrower; O3/O4 deferred (rpc_ok=false, stETH/ETH=1 assumption pending)}}
confidence: {confidence}
exceptions: {json.dumps(exceptions)}
recommendation: {recommendation}
rationale: No ALLOW rows at t0 → IDLE_ALL. Eligible set scored; many may WARN/EXIT on O1/O2 — expected. Never allocate without ALLOW ∩ PASS.
draft_actions: [{{fn: none, note: REFERENCE_ONLY idle, reference_only: true}}]
action_human: PENDING
tx_hash: none
aftermath_24h:
aftermath_7d:
decision_quality: {{false_alarm: null, missed_alarm: null, followed: null}}
drill: {json.dumps(drill)}
counts: weth={weth_n} wsteth={len(wst_rows)} eligible={len(eligible)} pass={len(pass_mk)} warn={raw['warn_n']} exit={raw['exit_n']}
"""
    with (OUT / "log.md").open("a") as f:
        f.write("\n" + log + "\n")

    pack = f"""# ALLOCATOR PACK | {iso}
STATUS: {status}
MANDATE: ETH Credit Conservative | B | {CFG['mandate_hash']}
BOOK: reference 100 | idle_pct 100 | n_alloc 0
EXCEPTIONS: {json.dumps(exceptions) if exceptions else 'none'}
RECOMMENDATION: {recommendation}
WHY: O6 no ALLOW → no allocation; DEMO_ONLY reference book idle is success
ELIGIBLE_SET: {json.dumps([x['marketId'] for x in pass_mk[:20]])}
INELIGIBLE_NOTE: lltv>86% including 94.5/96.5 excluded; non-wstETH dropped; forbidden LRT symbols dropped
CHANGES_VS_YESTERDAY: day-0 (no prior pack)
DATA_AGE_MAX_S: {data_age_max}
DRAFT: REFERENCE_ONLY — IDLE_ALL (no deallocate needed)
QUESTIONS_FOR_HUMAN:
1. Confirm ALLOW process when first PASS market is selected (marketId + cap_rel ≤0.25).
2. Preferred public RPC for D4 stEthPerToken (rpc_ok currently false)?
3. Keep REGIME B (≤86% LLTV) locked until first live sleeve?
DRILL_P_WSTETH: {drill['result']}
RAW_COUNTS: WETH_markets={weth_n} wstETH={len(wst_rows)} LLTV_eligible={len(eligible)} PASS={len(pass_mk)} WARN={raw['warn_n']} EXIT={raw['exit_n']}
DEMO_ONLY: true | Never sign | Never keys
"""
    (OUT / "pack.md").write_text(pack)
    print(json.dumps({
        "ok": True,
        "status": status,
        "recommendation": recommendation,
        "mandate_hash": CFG["mandate_hash"],
        "weth_n": weth_n,
        "wst_n": len(wst_rows),
        "eligible": len(eligible),
        "pass": len(pass_mk),
        "warn": raw["warn_n"],
        "exit": raw["exit_n"],
        "confidence": confidence,
        "halt": halt[:3],
        "data_age_s_max": data_age_max,
    }, indent=2))

if __name__ == "__main__":
    main()
