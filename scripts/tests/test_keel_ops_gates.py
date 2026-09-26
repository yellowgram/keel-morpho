#!/usr/bin/env python3
"""Local gate unit checks — no network required."""
from __future__ import annotations
import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repo root
sys.path.insert(0, str(ROOT / "scripts"))

from keel_ops_gates import (
    five_way_and,
    paste_check_allow_against_table,
    parse_allow_line,
    o6_flag,
    market_has_pass_score,
    recommendation_from_gates,
    check_forbidden_key_env,
    quiet_idle_fingerprint,
    weekday_miss_note,
    status_color,
    build_observe_gates,
    AllowRow,
    refuse_invent_action,
    refuse_invent_allow,
    refuse_invent_vault,
)


def assert_eq(a, b, msg=""):
    if a != b:
        raise AssertionError(f"{msg}: {a!r} != {b!r}")


def test_five_way_blocks_demo():
    r = five_way_and(
        allow_accepted_nonempty=True,
        market_pass=True,
        vault_set=True,
        demo_only=True,
        kill=False,
    )
    assert_eq(r.ok, False, "DEMO must block")
    r2 = five_way_and(
        allow_accepted_nonempty=True,
        market_pass=True,
        vault_set=True,
        demo_only=False,
        kill=False,
    )
    assert_eq(r2.ok, True, "all true should pass")
    r3 = five_way_and(
        allow_accepted_nonempty=True,
        market_pass=True,
        vault_set=True,
        demo_only=False,
        kill=True,
    )
    assert_eq(r3.ok, False, "KILL must block")


def test_allow_paste_rejects_poison():
    rows = [
        parse_allow_line(
            "ALLOW | 2026-09-26 | 0xabc | 945000000000000000 | wstETH | 0xoracle | 0.25 | bad lltv"
        ),
        parse_allow_line(
            "ALLOW | 2026-09-26 | 0xgood | 860000000000000000 | wstETH | 0xoracle | 0.25 | ok"
        ),
        parse_allow_line(
            "ALLOW | 2026-09-26 | 0xrel | 860000000000000000 | wstETH | 0xoracle | 0.50 | cap too high"
        ),
        parse_allow_line(
            "ALLOW | 2026-09-26 | 0xcoll | 860000000000000000 | weETH | 0xoracle | 0.25 | bad coll"
        ),
    ]
    acc, rej = paste_check_allow_against_table(
        rows,
        lltv_max_wad=860000000000000000,
        market_rel_cap=0.25,
        market_table_keys={"0xgood", "0xrel", "0xcoll", "0xabc"},
        regime_b_eligible_keys={"0xgood", "0xrel", "0xcoll"},  # abc would fail lltv anyway
        forbidden_collateral=["weETH", "rsETH"],
    )
    keys_acc = {r.unique_key for r in acc}
    assert_eq(keys_acc, {"0xgood"}, f"accepted={keys_acc}")
    assert_eq(len(rej), 3, "three rejects")


def test_allow_rejects_ineligible_unique_key():
    row = parse_allow_line(
        "ALLOW | 2026-09-26 | 0xinelig | 860000000000000000 | wstETH | 0xo | 0.1 | poison"
    )
    acc, rej = paste_check_allow_against_table(
        [row],
        lltv_max_wad=860000000000000000,
        market_rel_cap=0.25,
        market_table_keys={"0xinelig"},
        regime_b_eligible_keys=set(),  # in table but not eligible
        forbidden_collateral=[],
    )
    assert_eq(len(acc), 0)
    assert "not Regime-B-eligible" in rej[0].reject_reason


def test_o6_fail():
    assert_eq(o6_flag(901, 900).startswith("O6_FAIL"), True)
    assert_eq(o6_flag(100, 900).startswith("O6_PASS"), True)
    assert_eq(o6_flag(None, 900), "O6_PARTIAL")


def test_market_pass_requires_full():
    flags = [
        "O1_PASS", "O2_PASS", "O3_PASS", "O4_PASS(1bps)",
        "O5_PASS", "O6_PASS(age=10s)", "O7_PASS",
    ]
    assert_eq(market_has_pass_score(flags), True)
    flags2 = flags[:-1] + ["O7_N/A"]
    assert_eq(market_has_pass_score(flags2), False)
    flags3 = ["O1_PARTIAL", "O2_PASS", "O3_PARTIAL", "O4_PARTIAL", "O5_N/A", "O6_PASS(age=1s)", "O7_N/A"]
    assert_eq(market_has_pass_score(flags3), False)


def test_recommendation_kill_and_idle():
    five = five_way_and(
        allow_accepted_nonempty=False, market_pass=False, vault_set=False,
        demo_only=True, kill=False,
    )
    rec, _ = recommendation_from_gates(
        five_way=five, kill=False, graphql_ok=True, demo_only=True,
        eligible_n=0, inconsistent=False,
    )
    assert_eq(rec, "IDLE_ALL")
    rec2, rat2 = recommendation_from_gates(
        five_way=five, kill=True, graphql_ok=True, demo_only=True,
        eligible_n=0, inconsistent=False,
    )
    assert_eq(rec2, "IDLE_ALL")
    assert "KILL" in rat2
    rec3, _ = recommendation_from_gates(
        five_way=five, kill=False, graphql_ok=False, demo_only=True,
        eligible_n=0, inconsistent=False,
    )
    assert_eq(rec3, "HOLD")


def test_key_env_refuse():
    hits = check_forbidden_key_env({"PRIVATE_KEY": "0xdead", "PATH": "/bin"})
    assert_eq(hits, ["PRIVATE_KEY"])
    hits2 = check_forbidden_key_env({"PATH": "/bin", "HOME": "/tmp"})
    assert_eq(hits2, [])


def test_quiet_and_miss():
    fp1 = quiet_idle_fingerprint("IDLE_ALL", ["DEMO_ONLY=true"], [])
    fp2 = quiet_idle_fingerprint("IDLE_ALL", ["DEMO_ONLY=true"], [])
    assert_eq(fp1, fp2)
    now = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)  # Friday
    last = datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc)  # Wednesday → Thu miss
    note = weekday_miss_note(last, now)
    assert note and "1 weekday" in note


def test_status_colors():
    assert_eq(status_color(graphql_ok=True, mandate_ok=True, fetch_partial=False, inconsistent=False), "GREEN")
    assert_eq(status_color(graphql_ok=True, mandate_ok=True, fetch_partial=True, inconsistent=False), "AMBER")
    assert_eq(status_color(graphql_ok=False, mandate_ok=True, fetch_partial=True, inconsistent=False), "RED")
    assert_eq(status_color(graphql_ok=True, mandate_ok=False, fetch_partial=False, inconsistent=False), "RED")


def test_refuse_invent():
    assert_eq(refuse_invent_action().ok, False)
    assert_eq(refuse_invent_allow().ok, False)
    assert_eq(refuse_invent_vault().ok, False)


def test_build_gates_live_tree():
    g = build_observe_gates(ROOT, json.loads((ROOT / "config.json").read_text()))
    assert_eq(g.demo_only, True)
    assert_eq(g.kill, False)
    assert_eq(g.mandate_match(), True)
    assert_eq(g.brief_present, True)
    assert_eq(g.vault_address, None)


def test_mandate_mismatch_abort_signal():
    cfg = json.loads((ROOT / "config.json").read_text())
    cfg = dict(cfg)
    cfg["mandate_hash"] = "0" * 64
    g = build_observe_gates(ROOT, cfg)
    assert_eq(g.mandate_match(), False)


def main():
    tests = [
        test_five_way_blocks_demo,
        test_allow_paste_rejects_poison,
        test_allow_rejects_ineligible_unique_key,
        test_o6_fail,
        test_market_pass_requires_full,
        test_recommendation_kill_and_idle,
        test_key_env_refuse,
        test_quiet_and_miss,
        test_status_colors,
        test_refuse_invent,
        test_build_gates_live_tree,
        test_mandate_mismatch_abort_signal,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
    print(f"\n{len(tests)-failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
