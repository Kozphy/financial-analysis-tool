from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from statistics import stdev
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from financial_analysis_tool.quant.factors import compute_factor_snapshots
from financial_analysis_tool.quant.loader import (
    fetch_binance_price_records,
    load_price_records,
)


class _MockResponse:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class QuantFactorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_prices_csv = PROJECT_ROOT / "data" / "prices.csv"

    def test_price_loader_reads_sample_price_data(self) -> None:
        records = load_price_records(self.sample_prices_csv)

        self.assertEqual(len(records), 60)
        self.assertEqual(records[0].ticker, "ALP")
        self.assertEqual(records[0].date.isoformat(), "2025-01-31")
        self.assertAlmostEqual(records[-1].close, 111.0)

    def test_factor_snapshots_include_momentum_and_volatility(self) -> None:
        snapshots_by_date = compute_factor_snapshots(load_price_records(self.sample_prices_csv))
        april_snapshots = snapshots_by_date[_records_date("2025-04-30")]
        alp_snapshot = next(snapshot for snapshot in april_snapshots if snapshot.ticker == "ALP")
        expected_volatility = stdev(
            [
                0.02,
                (104.0 - 102.0) / 102.0,
                (107.0 - 104.0) / 104.0,
            ]
        )

        self.assertEqual(len(april_snapshots), 5)
        self.assertAlmostEqual(alp_snapshot.momentum, 0.07)
        self.assertAlmostEqual(alp_snapshot.volatility, expected_volatility)
        self.assertAlmostEqual(alp_snapshot.forward_return, (110.0 - 107.0) / 107.0)

    @patch("financial_analysis_tool.quant.loader.urlopen")
    def test_fetch_binance_price_records_parses_klines(self, mocked_urlopen) -> None:
        mocked_urlopen.return_value = _MockResponse(
            [
                [
                    1735689600000,
                    "100.0",
                    "110.0",
                    "95.0",
                    "105.0",
                    "2500.0",
                ]
            ]
        )

        records = fetch_binance_price_records(
            ["BTCUSDT"],
            interval="1d",
            limit=1,
            base_url="https://api.binance.com",
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].ticker, "BTCUSDT")
        self.assertEqual(records[0].date.isoformat(), "2025-01-01")
        self.assertAlmostEqual(records[0].close, 105.0)


def _records_date(raw_value: str):
    from datetime import date

    return date.fromisoformat(raw_value)


if __name__ == "__main__":
    unittest.main()
