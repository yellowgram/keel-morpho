"""Where market data comes from: the live public APIs, or a JSON fixture.

Every source call returns (value, error). A failed call never raises, so one
missing input marks a check UNKNOWN instead of stopping the report.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from . import __version__

# Some public endpoints reject urllib's default User-Agent with 403.
HEADERS = {"User-Agent": f"keel/{__version__} (+https://github.com/yellowgram/keel-morpho)"}

STETH_PER_TOKEN = "0x035faf82"  # wstETH.stEthPerToken()
ORACLE_PRICE = "0xa035b1fe"  # Morpho IOracle.price(), scaled by 1e36
MAX_MARKETS = 1000

MARKETS_QUERY = """
query Markets($first: Int!, $skip: Int!, $loan: [String!], $coll: [String!], $chain: [Int!]) {
  markets(first: $first, skip: $skip, orderBy: SupplyAssetsUsd, orderDirection: Desc,
          where: { chainId_in: $chain, loanAssetAddress_in: $loan, collateralAssetAddress_in: $coll }) {
    items {
      marketId
      lltv
      oracle { address }
      loanAsset { address symbol decimals }
      collateralAsset { address symbol decimals }
      state { utilization borrowAssets supplyAssets liquidityAssets supplyAssetsUsd supplyApy timestamp }
    }
    pageInfo { count countTotal }
  }
}
"""

TOP_BORROWER_QUERY = """
query Top($key: String!, $chain: Int!) {
  marketPositions(first: 1, orderBy: BorrowShares, orderDirection: Desc,
                  where: { marketUniqueKey_in: [$key], chainId_in: [$chain] }) {
    items { state { borrowAssets } }
  }
}
"""


def _redact(url: str) -> str:
    """scheme://host only. Provider URLs often embed an API key in the path or query."""
    p = urllib.parse.urlsplit(url)
    return f"{p.scheme}://{p.hostname}" if p.hostname else "<rpc>"


def _post(url: str, payload: dict, timeout: int) -> Any:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Accept": "application/json", **HEADERS},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


class LiveSources:
    """Morpho GraphQL, DefiLlama prices and public Ethereum RPC. Read-only."""

    def __init__(self, cfg: dict[str, Any], retries: int = 2) -> None:
        self.cfg = cfg
        self.retries = retries

    def _gql(self, query: str, variables: dict) -> tuple[Any, str | None]:
        last = "no attempt"
        for i in range(self.retries + 1):
            try:
                data = _post(self.cfg["GRAPHQL"], {"query": query, "variables": variables}, 60)
                if data.get("errors"):
                    return None, f"graphql: {data['errors'][0].get('message', data['errors'])}"
                return data["data"], None
            except Exception as e:  # network, timeout, bad JSON
                last = f"graphql: {e}"
                time.sleep(1.5 * (i + 1))
        return None, last

    def markets(self) -> tuple[list[dict] | None, str | None]:
        """All WETH-loan markets whose collateral is the configured wstETH address."""
        items: list[dict] = []
        skip = 0
        while True:
            data, err = self._gql(MARKETS_QUERY, {
                "first": 100, "skip": skip,
                "loan": [self.cfg["VAULT_ASSET"]], "coll": [self.cfg["WSTETH"]],
                "chain": [int(self.cfg["CHAIN_ID"])],
            })
            if err:
                return None, err
            page = data["markets"]
            batch = page.get("items") or []
            items.extend(batch)
            total = (page.get("pageInfo") or {}).get("countTotal")
            if len(batch) < 100 or (total is not None and len(items) >= int(total)):
                return items, None
            if len(items) >= MAX_MARKETS:
                return None, f"more than {MAX_MARKETS} markets; refusing a partial table"
            skip += 100

    def top_borrower_assets(self, market_id: str) -> tuple[int | None, str | None]:
        data, err = self._gql(TOP_BORROWER_QUERY, {"key": market_id, "chain": int(self.cfg["CHAIN_ID"])})
        if err:
            return None, err
        rows = ((data.get("marketPositions") or {}).get("items")) or []
        if not rows:
            return 0, None
        return int((rows[0].get("state") or {}).get("borrowAssets") or 0), None

    def prices(self) -> tuple[dict | None, str | None]:
        """USD prices for wstETH, WETH and stETH with their timestamps."""
        c = self.cfg
        ids = {k: f"ethereum:{c[k]}" for k in ("WSTETH", "VAULT_ASSET", "STETH")}
        url = c["LLAMA_PRICES"] + ",".join(ids.values())
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=30) as r:
                coins = json.loads(r.read().decode()).get("coins") or {}
        except Exception as e:
            return None, f"prices: {e}"
        lower = {k.lower(): v for k, v in coins.items()}
        out = {}
        for k, cid in ids.items():
            hit = lower.get(cid.lower())
            if not hit or not hit.get("price"):
                return None, f"prices: no price for {k}"
            out[k] = {"usd": float(hit["price"]), "ts": int(hit.get("timestamp") or 0)}
        return out, None

    def _eth_call(self, to: str, data: str) -> tuple[int | None, str | None]:
        payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call", "params": [{"to": to, "data": data}, "latest"]}
        last = "no RPC configured"
        for url in self.cfg.get("RPC_URLS") or []:
            try:
                res = _post(url, payload, 20)
                hexval = res.get("result")
                if res.get("error") or not hexval or hexval == "0x":
                    last = f"rpc {_redact(url)}: {res.get('error') or 'empty result'}"
                    continue
                return int(hexval, 16), None
            except Exception as e:
                last = f"rpc {_redact(url)}: {str(e).replace(url, _redact(url))}"
        return None, last

    def steth_per_wsteth(self) -> tuple[float | None, str | None]:
        v, err = self._eth_call(self.cfg["WSTETH"], STETH_PER_TOKEN)
        return (v / 1e18 if v is not None else None), err

    def oracle_price(self, oracle: str, loan_dec: int, coll_dec: int) -> tuple[float | None, str | None]:
        """Loan-asset units per one collateral unit, as the market's oracle reports it."""
        v, err = self._eth_call(oracle, ORACLE_PRICE)
        if v is None:
            return None, err
        return v / 10 ** (36 + loan_dec - coll_dec), None


class FixtureSources:
    """Replays a JSON snapshot (see examples/fixture.json). No network."""

    def __init__(self, path: Path) -> None:
        self.data = json.loads(path.read_text())
        # A snapshot's prices are only fresh relative to when it was captured.
        self.captured_at = self.data.get("captured_at")

    def _get(self, key: str) -> tuple[Any, str | None]:
        v = self.data.get(key)
        return (None, f"fixture: no {key}") if v is None else (v, None)

    def markets(self):
        return self._get("markets")

    def top_borrower_assets(self, market_id: str):
        v = (self.data.get("top_borrower_assets") or {}).get(market_id)
        return (None, f"fixture: no top borrower for {market_id[:10]}…") if v is None else (int(v), None)

    def prices(self):
        return self._get("prices")

    def steth_per_wsteth(self):
        return self._get("steth_per_wsteth")

    def oracle_price(self, oracle: str, loan_dec: int, coll_dec: int):
        v = (self.data.get("oracle_prices") or {}).get(oracle.lower())
        return (None, f"fixture: no oracle price for {oracle}") if v is None else (float(v), None)
