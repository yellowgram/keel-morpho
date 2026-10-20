"""Run with `python3 -m unittest` or `pytest`. No network."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from keel import checks, gates, sources
from keel.__main__ import main
from keel.config import ConfigError, check_policy_pin, load_config, policy_fingerprint

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "examples"
NOW = datetime(2026, 10, 19, 14, 0, tzinfo=timezone.utc)
EXAMPLE_FINGERPRINT = "a142f4953aa0447aaecb4ed52248bd86b91cb4a4561a3ec95b22c01524319dbb"  # STALE_S 2100
FINGERPRINT_1800 = "14a87fef4cc524204f9483f6e7474f439eb6067015fb2e01a2472adae41131eb"    # STALE_S 1800 (first R4 proposal, never released)
FINGERPRINT_0_2_0 = "95af7dfcdbfaa3d5a2c8f6d0ebb836ff8d99e5124462666806035c714ad0f4a2"    # STALE_S 900
CLEAN_ENV = {k: v for k, v in os.environ.items() if not any(s in k.upper() for s in gates.FORBIDDEN_KEY_ENV_SUBSTR)}


def cfg(**over):
    c, _ = load_config(ROOT / "config.example.json")
    c.update(over)
    return c


def fixture():
    return json.loads((EX / "fixture.json").read_text())


def market(i="a", **state):
    m = copy.deepcopy(next(x for x in fixture()["markets"] if x["marketId"] == "0x" + i * 64))
    m["state"].update(state)
    return m


def by(cs):
    return {c.name: c.status for c in cs}


def run_market(m, c=None, **kw):
    fx = fixture()
    args = dict(top_borrower_assets=int(fx["top_borrower_assets"][m["marketId"]]),
                oracle_price=fx["oracle_prices"][m["oracle"]["address"]], prices=fx["prices"],
                steth_per_wsteth=fx["steth_per_wsteth"], now_ts=int(NOW.timestamp()))
    args.update(kw)
    return checks.run_checks(m, c or cfg(), **args)


class Eligibility(unittest.TestCase):
    def test_collateral_named_wsteth_at_another_address_is_rejected(self):  # K1
        r = checks.ineligible_reasons(market("b"), cfg())
        self.assertTrue(any("not the wstETH contract" in x for x in r))

    def test_real_wsteth_with_any_symbol_is_accepted(self):
        m = market("a")
        m["collateralAsset"]["symbol"] = "WSTETH-weird"
        m["collateralAsset"]["address"] = m["collateralAsset"]["address"].lower()
        self.assertEqual(checks.ineligible_reasons(m, cfg()), [])

    def test_lltv_boundary(self):
        m = market("a")
        self.assertEqual(checks.ineligible_reasons(m, cfg()), [])
        m["lltv"] = str(860000000000000001)
        self.assertTrue(checks.ineligible_reasons(m, cfg()))

    def test_api_symbols_are_inert_in_the_report(self):  # G3
        m = market("b")
        m["collateralAsset"]["symbol"] = "wstETH](https://evil.example)<img src=x>|"
        r = " ".join(checks.ineligible_reasons(m, cfg()))
        for bad in ("](", "<", ">", "|", "://"):
            self.assertNotIn(bad, r)

    def test_wrong_loan_asset(self):
        m = market("a")
        m["loanAsset"]["address"] = "0x" + "11" * 20
        self.assertTrue(any("loan asset" in x for x in checks.ineligible_reasons(m, cfg())))


class Checks(unittest.TestCase):
    def test_healthy_market_passes_everything(self):
        cs = run_market(market("a"))
        self.assertEqual([c.name for c in cs], list(checks.CHECK_NAMES))
        self.assertTrue(checks.market_ready(True, cs), [c.__dict__ for c in cs])

    def test_top_borrower_bands(self):
        borrow = int(market("a")["state"]["borrowAssets"])
        for share, want in ((0.10, "PASS"), (0.12, "WARN"), (0.151, "EXIT")):
            self.assertEqual(by(run_market(market("a"), top_borrower_assets=int(borrow * share)))["top_borrower"], want)

    def test_utilization_bands(self):
        for u, want in ((0.80, "PASS"), (0.85, "WARN"), (0.93, "EXIT")):
            self.assertEqual(by(run_market(market("a", utilization=u)))["utilization"], want)

    def test_oracle_deviation(self):
        px = fixture()["prices"]
        mkt = px["WSTETH"]["usd"] / px["VAULT_ASSET"]["usd"]
        for bps, want in ((50, "PASS"), (120, "WARN"), (200, "EXIT")):
            got = by(run_market(market("a"), oracle_price=mkt * (1 + bps / 1e4)))["oracle_deviation"]
            self.assertEqual(got, want, bps)

    def test_wsteth_rate_depeg(self):
        self.assertEqual(by(run_market(market("a"), steth_per_wsteth=1.30))["wsteth_rate"], "EXIT")

    def test_exit_liquidity(self):
        self.assertEqual(by(run_market(market("a", liquidityAssets=str(1000 * 10**18))))["exit_liquidity"], "WARN")
        self.assertEqual(by(run_market(market("a", liquidityAssets=str(1200 * 10**18))))["exit_liquidity"], "PASS")

    def test_freshness_uses_oldest_price(self):
        px = copy.deepcopy(fixture()["prices"])
        px["STETH"]["ts"] = int(NOW.timestamp()) - (cfg()["STALE_S"] + 1)
        self.assertEqual(by(run_market(market("a"), prices=px))["freshness"], "WARN")

    def _fresh(self, age):
        px = copy.deepcopy(fixture()["prices"])
        for v in px.values():
            v["ts"] = int(NOW.timestamp()) - age
        return run_market(market("a"), prices=px)

    def test_freshness_boundary_and_measured_cadence(self):  # STALE_S 2100 (0.2.1)
        # DefiLlama stores wstETH/stETH about every 1800 s and serves it 90-150 s later:
        # an on-schedule price is 90 s (just published) up to ~1950 s old (1901 s measured).
        for age in (90, 1790, 1901, 1950):
            self.assertEqual(by(self._fresh(age))["freshness"], "PASS", age)
        self.assertEqual(by(self._fresh(2100))["freshness"], "PASS")   # the limit itself is fresh
        self.assertEqual(by(self._fresh(2101))["freshness"], "WARN")   # one second over is not
        # A missed update (measured stETH gap 2469 s + publish lag) must WARN.
        self.assertEqual(by(self._fresh(2469 + 150))["freshness"], "WARN")

    def test_stale_price_warn_blocks_ready(self):  # K-R4-2: the property the STALE_S change relies on
        fresh = self._fresh(300)
        self.assertTrue(checks.market_ready(True, fresh), [(c.name, c.status) for c in fresh])
        stale = self._fresh(cfg()["STALE_S"] + 1)
        self.assertEqual(by(stale)["freshness"], "WARN")
        self.assertEqual([c.name for c in stale if c.status != "PASS"], ["freshness"])  # nothing else fails
        self.assertFalse(checks.market_ready(True, stale))

    def test_missing_data_is_unknown_and_never_ready(self):
        cs = run_market(market("a"), top_borrower_assets=None, oracle_price=None, prices=None, steth_per_wsteth=None)
        st = by(cs)
        for n in ("top_borrower", "oracle_deviation", "wsteth_rate", "freshness"):
            self.assertEqual(st[n], "UNKNOWN")
        self.assertFalse(checks.market_ready(True, cs))


def table_row(i="a", eligible=True, ready=True):
    m = market(i)
    return {"marketId": m["marketId"], "lltv": int(m["lltv"]), "oracle": m["oracle"]["address"],
            "eligible": eligible, "ineligible_reasons": [] if eligible else ["x"], "ready": ready}


def allow(i="a", lltv="860000000000000000", coll="wstETH", oracle=None, cap="0.25"):
    oracle = oracle or "0x" + (i + "1") * 20
    return gates.parse_allow_line(f"ALLOW | 2026-10-19 | 0x{i * 64} | {lltv} | {coll} | {oracle} | {cap} | ok")


class Allowlist(unittest.TestCase):
    def check(self, row, table=None):
        return gates.check_allow_rows([row], table or [table_row("a")], cfg())

    def test_exact_row_accepted(self):
        acc, rej = self.check(allow())
        self.assertEqual((len(acc), len(rej)), (1, 0))

    def test_poisoned_rows_rejected(self):
        for row, why in ((allow(lltv="945000000000000000"), "lltv_wad"),
                         (allow(oracle="0x" + "99" * 20), "oracle"),
                         (allow(coll="weETH"), "collateral"),
                         (allow(cap="0.5"), "cap_rel"),
                         (allow("e"), "not in today's table"),
                         (gates.parse_allow_line("ALLOW | 0xabc"), "format"),
                         (allow(lltv="lots"), "not a number")):
            acc, rej = self.check(row)
            self.assertEqual(acc, [], why)
            self.assertIn(why, rej[0].reject_reason)

    def test_ineligible_market_rejected(self):
        acc, rej = self.check(allow(), [table_row("a", eligible=False, ready=False)])
        self.assertIn("not eligible", rej[0].reject_reason)

    def test_comments_ignored(self):
        self.assertIsNone(gates.parse_allow_line("# ALLOW | example"))
        self.assertIsNone(gates.parse_allow_line("Format: ALLOW | date"))


def decide(**over):
    a = dict(fetch_ok=True, demo_only=False, kill=False, vault_set=True, open_size=0.0,
             accepted=[allow("a")], ready_ids={"0x" + "a" * 64}, eligible_n=1)
    a.update(over)
    return gates.decide(**a)


class Decision(unittest.TestCase):
    def test_allocate_needs_everything(self):
        self.assertEqual(decide().recommendation, "ALLOCATE_ELIGIBLE")
        for over in (dict(demo_only=True), dict(kill=True), dict(vault_set=False), dict(accepted=[]),
                     dict(ready_ids=set())):
            self.assertEqual(decide(**over).recommendation, "IDLE_ALL", over)

    def test_allowlisted_market_must_itself_be_ready(self):  # K7
        d = decide(accepted=[allow("a")], ready_ids={"0x" + "c" * 64})
        self.assertEqual(d.recommendation, "IDLE_ALL")
        self.assertIn("no allowlisted market passes every check", d.blockers)

    def test_idle_wording(self):
        d = decide(ready_ids=set(), eligible_n=0, accepted=[])
        self.assertEqual(d.rationale, "It is normal for Keel to recommend holding everything idle. "
                                      "That means no market met the safety filters.")

    def test_demo_with_open_position_is_exit_priority(self):
        self.assertEqual(decide(demo_only=True, open_size=5.0).recommendation, "EXIT_PRIORITY")

    def test_fetch_failure_holds(self):
        self.assertEqual(decide(fetch_ok=False).recommendation, "HOLD")

    def test_key_env_detected_by_name(self):
        self.assertEqual(gates.forbidden_key_env({"MY_PRIVATE_KEY": "x", "EMPTY_MNEMONIC": "", "PATH": "/bin"}),
                         ["MY_PRIVATE_KEY"])

    def test_missed_weekdays(self):
        fri = datetime(2026, 10, 16, 14, tzinfo=timezone.utc)
        self.assertEqual(gates.missed_weekdays(fri, NOW), 0)  # Fri -> Mon
        self.assertEqual(gates.missed_weekdays(datetime(2026, 10, 15, 14, tzinfo=timezone.utc), NOW), 1)
        self.assertIsNone(gates.missed_weekdays(None, NOW))


class Config(unittest.TestCase):
    def write(self, d, obj):
        p = Path(d) / "config.json"
        p.write_text(json.dumps(obj))
        return p

    def base(self):
        return json.loads((ROOT / "config.example.json").read_text())

    def test_example_loads_without_warnings(self):
        _, w = load_config(ROOT / "config.example.json")
        self.assertEqual(w, [])

    def test_rejects_bad_values(self):
        with tempfile.TemporaryDirectory() as d:
            for over in ({"UTIL_WARN": 0.95}, {"UTIL_EXIT": "0.9"}, {"KILL": "no"}, {"WSTETH": "wstETH"},
                         {"RPC_URLS": []}, {"STALE_S": -1}):
                with self.assertRaises(ConfigError, msg=over):
                    load_config(self.write(d, {**self.base(), **over}))
            b = self.base()
            del b["MAX_LLTV_WAD"]
            with self.assertRaises(ConfigError):
                load_config(self.write(d, b))

    def test_old_key_name_still_works(self):
        with tempfile.TemporaryDirectory() as d:
            b = self.base()
            b["FORBIDDEN_LLTV_WAD_MIN_EXCLUSIVE_B"] = b.pop("MAX_LLTV_WAD")
            c, w = load_config(self.write(d, b))
            self.assertEqual(c["MAX_LLTV_WAD"], 860000000000000000)
            self.assertTrue(w)

    def test_example_stale_s_and_fingerprint(self):  # 0.2.1 policy change
        c = cfg()
        self.assertEqual(c["STALE_S"], 2100)
        self.assertEqual(policy_fingerprint(cfg(STALE_S=1800)), FINGERPRINT_1800)
        # Pinned literal: a silent change to any policy value in the example must fail here.
        self.assertEqual(policy_fingerprint(c), EXAMPLE_FINGERPRINT)
        self.assertNotEqual(policy_fingerprint(cfg(STALE_S=900)), EXAMPLE_FINGERPRINT)
        self.assertEqual(policy_fingerprint(cfg(STALE_S=900)), FINGERPRINT_0_2_0)

    def test_docs_match_the_example_policy(self):
        c = cfg()
        fp = policy_fingerprint(c)
        pack = (EX / "sample-pack.md").read_text()
        self.assertIn(f"Policy fingerprint: `{fp}`", pack)
        self.assertIn(f"(limit {c['STALE_S']}s)", pack)
        self.assertNotIn("(limit 900s)", pack)
        self.assertIn(f"WARN above {c['STALE_S']} s", (ROOT / "README.md").read_text())
        self.assertIn(f"The example `STALE_S` is {c['STALE_S']} s", (ROOT / "docs" / "OPERATING.md").read_text())
        changelog = (ROOT / "CHANGELOG.md").read_text()
        self.assertIn(fp, changelog)
        # K-R4-1: the rationale is the measured cadence (~1800 s + 90-150 s lag), not the 925-986 s samples.
        latest = changelog.split("\n## ", 2)[1]
        for text in (latest, (ROOT / "README.md").read_text(), (ROOT / "docs" / "OPERATING.md").read_text()):
            self.assertIn("1800 s", text)
            self.assertIn("90–150 s", text)
            self.assertNotIn("925", text)
        import keel
        self.assertTrue(changelog.split("\n## ", 1)[1].startswith(keel.__version__ + " "))

    def test_policy_pin(self):
        c = cfg()
        fp = policy_fingerprint(c)
        self.assertEqual(policy_fingerprint(cfg(WSTETH=c["WSTETH"].upper().replace("0X", "0x"))), fp)
        self.assertEqual(check_policy_pin(cfg(POLICY_SHA256=fp)), fp)
        with self.assertRaises(ConfigError):
            check_policy_pin(cfg(POLICY_SHA256=fp, UTIL_EXIT=0.99))
        self.assertNotEqual(policy_fingerprint(cfg(OPEN_SIZE_WETH=1)), fp + "x")  # non-policy keys ignored
        self.assertEqual(policy_fingerprint(cfg(OPEN_SIZE_WETH=1)), fp)


class LiveSourceRequests(unittest.TestCase):
    """The request shapes that were broken in 0.1.x, checked without the network."""

    def test_top_borrower_uses_market_positions(self):  # K5
        seen = {}

        def fake(url, payload, timeout):
            seen.update(payload)
            return {"data": {"marketPositions": {"items": [{"state": {"borrowAssets": "7"}}]}}}

        with mock.patch.object(sources, "_post", fake):
            self.assertEqual(sources.LiveSources(cfg()).top_borrower_assets("0x" + "a" * 64), (7, None))
        self.assertIn("marketPositions", seen["query"])
        self.assertNotIn("marketByUniqueKey", seen["query"])

    def test_steth_per_token_selector(self):  # K6
        calls = []

        def fake(url, payload, timeout):
            calls.append(payload)
            return {"result": hex(1246696000000000000)}

        with mock.patch.object(sources, "_post", fake):
            v, err = sources.LiveSources(cfg()).steth_per_wsteth()
        self.assertIsNone(err)
        self.assertAlmostEqual(v, 1.246696)
        self.assertEqual(calls[0]["params"][0]["data"], "0x035faf82")

    def test_rpc_falls_back_to_next_url(self):
        calls = []

        def fake(url, payload, timeout):
            calls.append(url)
            if len(calls) == 1:
                raise OSError("down")
            return {"result": hex(10**36)}

        with mock.patch.object(sources, "_post", fake):
            v, err = sources.LiveSources(cfg()).oracle_price("0x" + "a1" * 20, 18, 18)
        self.assertEqual((v, err), (1.0, None))
        self.assertEqual(len(calls), 2)

    def test_refuses_too_many_markets(self):  # K3: no silent truncation
        page = [market("a")] * 100

        def fake(url, payload, timeout):
            return {"data": {"markets": {"items": page, "pageInfo": {"count": 100, "countTotal": 5000}}}}

        with mock.patch.object(sources, "_post", fake):
            v, err = sources.LiveSources(cfg()).markets()
        self.assertIsNone(v)
        self.assertIn("1000", err)

    def test_rpc_errors_never_contain_the_url_path(self):  # G2
        key_url = "https://eth-mainnet.example.com/v2/SECRETKEY123?apikey=SECRETKEY123"

        def fake(url, payload, timeout):
            raise OSError(f"<urlopen error {url} refused>")

        with mock.patch.object(sources, "_post", fake):
            _, err = sources.LiveSources(cfg(RPC_URLS=[key_url])).steth_per_wsteth()
        self.assertNotIn("SECRETKEY123", err)
        self.assertIn("eth-mainnet.example.com", err)

    def test_requests_send_a_user_agent(self):
        self.assertTrue(sources.HEADERS["User-Agent"].startswith("keel/"))


class CommandLine(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.d)
        shutil.copy(ROOT / "config.example.json", self.d / "config.json")
        shutil.copy(EX / "allowlist.md", self.d / "allowlist.md")

    def run_cli(self, *args, env=None):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, env if env is not None else CLEAN_ENV, clear=True), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["observe", "--config", str(self.d / "config.json"), "--fixture", str(EX / "fixture.json"),
                         "--now", "2026-10-19T14:00:00Z", *args])
        return code, out.getvalue(), err.getvalue()

    def edit(self, **over):
        p = self.d / "config.json"
        p.write_text(json.dumps({**json.loads(p.read_text()), **over}))

    def test_sample_pack_is_current(self):
        code, _, _ = self.run_cli()
        self.assertEqual(code, 0)
        self.assertEqual((self.d / "out" / "pack.md").read_text(), (EX / "sample-pack.md").read_text(),
                         "regenerate with: python3 -m keel observe --config config.example.json "
                         "--fixture examples/fixture.json --allowlist examples/allowlist.md --out /tmp/k "
                         "--now 2026-10-19T14:00:00Z && cp /tmp/k/pack.md examples/sample-pack.md")

    def test_demo_without_now_uses_capture_time(self):  # the README quickstart command
        out = io.StringIO()
        with mock.patch.dict(os.environ, CLEAN_ENV, clear=True), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(io.StringIO()):
            code = main(["observe", "--config", str(self.d / "config.json"), "--fixture", str(EX / "fixture.json"),
                         "--allowlist", str(EX / "allowlist.md"), "--out", str(self.d / "demo")])
        self.assertEqual(code, 0)
        self.assertEqual((self.d / "demo" / "pack.md").read_text(), (EX / "sample-pack.md").read_text())

    def test_bad_now_is_a_usage_error(self):
        with contextlib.redirect_stderr(io.StringIO()), mock.patch.dict(os.environ, CLEAN_ENV, clear=True):
            self.assertEqual(main(["observe", "--config", str(self.d / "config.json"), "--now", "2026-10-19"]), 2)
            self.assertEqual(main(["observe", "--config", str(self.d / "config.json"), "--now", "yesterday"]), 2)
            self.assertEqual(main(["observe", "--config", str(self.d / "config.json"), "--fixture", "/nope.json"]), 2)

    def test_live_ready_config_allocates(self):
        self.edit(DEMO_ONLY=False, VAULT_ADDRESS="0x" + "12" * 20)
        code, out, _ = self.run_cli()
        self.assertTrue(out.startswith("ALLOCATE_ELIGIBLE"), out)
        log = (self.d / "out" / "log.jsonl").read_text().splitlines()
        self.assertEqual(json.loads(log[-1])["allocatable"], ["0x" + "a" * 64])

    def test_stale_prices_never_allocate(self):  # K-R4-2 end to end: same live-ready config, stale prices
        self.edit(DEMO_ONLY=False, VAULT_ADDRESS="0x" + "12" * 20)
        fx = fixture()
        for v in fx["prices"].values():
            v["ts"] = int(NOW.timestamp()) - (cfg()["STALE_S"] + 1)
        (self.d / "stale.json").write_text(json.dumps(fx))
        code, out, _ = self.run_cli("--fixture", str(self.d / "stale.json"))
        self.assertEqual(code, 0)
        self.assertFalse(out.startswith("ALLOCATE_ELIGIBLE"), out)
        pack = (self.d / "out" / "pack.md").read_text()
        self.assertNotIn("ALLOCATE_ELIGIBLE", pack)
        self.assertIn("| freshness | WARN |", pack)
        self.assertEqual(json.loads((self.d / "out" / "log.jsonl").read_text().splitlines()[-1])["allocatable"], [])

    def test_refuses_with_key_in_env(self):
        code, _, err = self.run_cli(env={**CLEAN_ENV, "DEPLOYER_PRIVATE_KEY": "secret-value"})
        self.assertEqual(code, 2)
        self.assertIn("DEPLOYER_PRIVATE_KEY", err)
        self.assertNotIn("secret-value", err)
        self.assertFalse((self.d / "out").exists())

    def test_policy_drift_stops_the_run(self):
        self.edit(POLICY_SHA256="0" * 64)
        code, _, err = self.run_cli()
        self.assertEqual(code, 2)
        self.assertIn("policy changed", err)

    def test_exit_with_open_position_sets_kill(self):
        fx = fixture()
        fx["oracle_prices"]["0x" + "a1" * 20] = 1.40
        p = self.d / "fx.json"
        p.write_text(json.dumps(fx))
        self.edit(DEMO_ONLY=False, VAULT_ADDRESS="0x" + "12" * 20, OPEN_SIZE_WETH=10)
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, CLEAN_ENV, clear=True), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(err):
            main(["observe", "--config", str(self.d / "config.json"), "--fixture", str(p), "--now", "2026-10-19T14:00:00Z"])
        self.assertTrue(json.loads((self.d / "config.json").read_text())["KILL"])
        self.assertTrue(out.getvalue().startswith("IDLE_ALL"), out.getvalue())

    def test_exit_on_a_market_you_did_not_allowlist_does_not_kill(self):  # G1
        fx = fixture()
        fx["oracle_prices"]["0x" + "c1" * 20] = 1.40  # market c: not in the allowlist
        p = self.d / "fx.json"
        p.write_text(json.dumps(fx))
        self.edit(DEMO_ONLY=False, VAULT_ADDRESS="0x" + "12" * 20, OPEN_SIZE_WETH=10)
        with mock.patch.dict(os.environ, CLEAN_ENV, clear=True), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            main(["observe", "--config", str(self.d / "config.json"), "--fixture", str(p), "--now", "2026-10-19T14:00:00Z"])
        self.assertFalse(json.loads((self.d / "config.json").read_text())["KILL"])

    def test_env_kill_overrides(self):
        self.edit(DEMO_ONLY=False, VAULT_ADDRESS="0x" + "12" * 20)
        _, out, _ = self.run_cli(env={**CLEAN_ENV, "KEEL_KILL": "1"})
        self.assertTrue(out.startswith("IDLE_ALL"))

    def test_no_market_data_exits_1(self):
        p = self.d / "empty.json"
        p.write_text("{}")
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, CLEAN_ENV, clear=True), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(err):
            code = main(["observe", "--config", str(self.d / "config.json"), "--fixture", str(p)])
        self.assertEqual(code, 1)
        self.assertTrue(out.getvalue().startswith("HOLD"))

    def test_missing_config(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["observe", "--config", str(self.d / "nope.json")]), 2)


if __name__ == "__main__":
    unittest.main()
