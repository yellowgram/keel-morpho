"""Missing or broken data never counts as a pass (KEEL-1), plus config/allowlist hardening."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from keel import checks, gates, sources
from keel.config import ConfigError, load_config
from tests.test_keel import NOW, ROOT, by, cfg, fixture, market, run_market


class MissingDataIsNotPass(unittest.TestCase):
    def test_nan_utilization_is_unknown(self):
        self.assertEqual(by(run_market(market("a", utilization=float("nan"))))["utilization"], "UNKNOWN")

    def test_negative_utilization_is_unknown(self):
        self.assertEqual(by(run_market(market("a", utilization=-0.5)))["utilization"], "UNKNOWN")

    def test_non_numeric_utilization_is_unknown(self):
        self.assertEqual(by(run_market(market("a", utilization="high")))["utilization"], "UNKNOWN")

    def test_nan_oracle_is_unknown(self):
        self.assertEqual(by(run_market(market("a"), oracle_price=float("nan")))["oracle_deviation"], "UNKNOWN")

    def test_zero_or_nan_prices_are_unknown_not_a_crash(self):
        for bad in (0, float("nan"), -1, None):
            p = copy.deepcopy(fixture()["prices"])
            p["VAULT_ASSET"]["usd"] = bad
            r = by(run_market(market("a"), prices=p))
            self.assertEqual(r["oracle_deviation"], "UNKNOWN", bad)
            self.assertEqual(r["wsteth_rate"], "UNKNOWN", bad)
        self.assertEqual(by(run_market(market("a"), steth_per_wsteth=0))["wsteth_rate"], "UNKNOWN")

    def test_no_positions_while_borrowed_is_unknown(self):
        def fake(url, payload, timeout):
            return {"data": {"marketPositions": {"items": []}}}
        with mock.patch.object(sources, "_post", fake):
            top, err = sources.LiveSources(cfg()).top_borrower_assets("0x" + "a" * 64)
        m = market("a")
        self.assertGreater(int(m["state"]["borrowAssets"]), 0)
        self.assertEqual(by(run_market(m, top_borrower_assets=top))["top_borrower"], "UNKNOWN")
        # A market with no borrows still passes with no positions.
        self.assertEqual(by(run_market(market("a", borrowAssets="0"), top_borrower_assets=top))["top_borrower"], "PASS")

    def test_future_price_timestamp_is_unknown(self):
        p = copy.deepcopy(fixture()["prices"])
        for v in p.values():
            v["ts"] = int(NOW.timestamp()) + 10**6
        self.assertEqual(by(run_market(market("a"), prices=p))["freshness"], "UNKNOWN")
        # Within the 60 s skew allowance it is fresh.
        for v in p.values():
            v["ts"] = int(NOW.timestamp()) + 30
        self.assertEqual(by(run_market(market("a"), prices=p))["freshness"], "PASS")

    def test_missing_price_timestamp_is_unknown(self):
        p = copy.deepcopy(fixture()["prices"])
        del p["STETH"]["ts"]
        self.assertEqual(by(run_market(market("a"), prices=p))["freshness"], "UNKNOWN")

    def test_missing_or_invalid_lltv_is_ineligible(self):
        for bad in (None, "", "abc", 0, -1, str(10**18)):
            m = market("a")
            m["lltv"] = bad
            self.assertIn("LLTV is missing or invalid", checks.ineligible_reasons(m, cfg()), bad)
        self.assertEqual(checks.ineligible_reasons(market("a"), cfg()), [])

    def test_unknown_blocks_readiness(self):
        cs = run_market(market("a", utilization=float("nan")))
        self.assertFalse(checks.market_ready(True, cs))


class ConfigAndAllowlist(unittest.TestCase):
    def test_nan_cap_rel_is_rejected(self):
        for bad in ("nan", "inf", "-0.1", "0"):
            row = gates.parse_allow_line(f"ALLOW | 2026-10-19 | 0x{'a' * 64} | 860000000000000000 | wstETH | 0x{'b' * 40} | {bad} | test")
            self.assertIn("cap_rel", row.reject_reason, bad)

    def test_nan_policy_value_is_refused(self):
        raw = json.loads((ROOT / "config.example.json").read_text())
        raw["UTIL_EXIT"] = float("nan")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "c.json"
            p.write_text(json.dumps(raw))  # writes NaN, which json.loads accepts
            with self.assertRaises(ConfigError):
                load_config(p)

    def test_key_env_override_waives_only_named_variables(self):
        env = {"GITHUB_APP_PRIVATE_KEY": "x", "ETH_PRIVATE_KEY": "y"}
        self.assertEqual(gates.forbidden_key_env(env), ["ETH_PRIVATE_KEY", "GITHUB_APP_PRIVATE_KEY"])
        env[gates.KEY_ENV_OVERRIDE] = "GITHUB_APP_PRIVATE_KEY"
        self.assertEqual(gates.forbidden_key_env(env), ["ETH_PRIVATE_KEY"])
        env[gates.KEY_ENV_OVERRIDE] = "*"
        self.assertEqual(gates.forbidden_key_env(env), ["ETH_PRIVATE_KEY", "GITHUB_APP_PRIVATE_KEY"])


if __name__ == "__main__":
    unittest.main()
