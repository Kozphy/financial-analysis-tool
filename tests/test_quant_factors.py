from __future__ import annotations

import json
import sys
import unittest
from datetime import date
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
    fetch_tej_price_records,
    fetch_twse_price_records,
    load_price_records,
)
from financial_analysis_tool.quant.models import PriceRecord


class QuantFactorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_prices_csv = PROJECT_ROOT / "data" / "prices.csv"
        self.fixtures_root = PROJECT_ROOT / "tests" / "fixtures"

    def test_price_loader_reads_sample_price_data(self) -> None:
        records = load_price_records(self.sample_prices_csv)

        self.assertEqual(len(records), 60)
        self.assertEqual(records[0].ticker, "ALP")
        self.assertEqual(records[0].date.isoformat(), "2025-01-31")
        self.assertAlmostEqual(records[-1].close, 111.0)

    def test_factor_snapshots_include_momentum_and_volatility(self) -> None:
        snapshots_by_date = compute_factor_snapshots(load_price_records(self.sample_prices_csv))
        april_snapshots = snapshots_by_date[_records_date("2025-04-30")]
        may_snapshots = snapshots_by_date[_records_date("2025-05-31")]
        alp_snapshot = next(snapshot for snapshot in may_snapshots if snapshot.ticker == "ALP")
        expected_volatility = stdev(
            [
                (110.0 - 107.0) / 107.0,
                (107.0 - 104.0) / 104.0,
            ]
        )

        self.assertEqual(len(april_snapshots), 5)
        self.assertEqual(len(may_snapshots), 5)
        self.assertAlmostEqual(alp_snapshot.momentum, (110.0 - 104.0) / 104.0)
        self.assertAlmostEqual(alp_snapshot.volatility, expected_volatility)
        self.assertAlmostEqual(alp_snapshot.close, 110.0)

    def test_factor_windows_use_trailing_calendar_window_instead_of_row_count(self) -> None:
        records = [
            PriceRecord(date=date(2025, 1, 1), ticker="AAA", open=100, high=100, low=100, close=100, volume=1),
            PriceRecord(date=date(2025, 1, 10), ticker="AAA", open=105, high=105, low=105, close=105, volume=1),
            PriceRecord(date=date(2025, 1, 20), ticker="AAA", open=110, high=110, low=110, close=110, volume=1),
            PriceRecord(date=date(2025, 2, 1), ticker="AAA", open=120, high=120, low=120, close=120, volume=1),
        ]

        snapshots_by_date = compute_factor_snapshots(
            records,
            momentum_lookback_days=15,
            volatility_lookback_days=25,
        )
        snapshot = snapshots_by_date[date(2025, 2, 1)][0]
        expected_volatility = stdev(
            [
                (110.0 - 105.0) / 105.0,
                (120.0 - 110.0) / 110.0,
            ]
        )

        self.assertAlmostEqual(snapshot.momentum, (120.0 - 110.0) / 110.0)
        self.assertAlmostEqual(snapshot.volatility, expected_volatility)

    @patch("financial_analysis_tool.quant.sources.binance_source.request_json")
    def test_fetch_binance_price_records_parses_klines(self, mocked_request_json) -> None:
        mocked_request_json.return_value = [
            [
                1735689600000,
                "100.0",
                "110.0",
                "95.0",
                "105.0",
                "2500.0",
            ]
        ]

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

    @patch("financial_analysis_tool.quant.sources.twse_source.request_json")
    def test_fetch_twse_price_records_parses_monthly_json(self, mocked_request_json) -> None:
        mocked_request_json.return_value = json.loads(
            (self.fixtures_root / "twse_stock_day.json").read_text(encoding="utf-8")
        )

        records = fetch_twse_price_records(
            ["2330"],
            base_url="https://www.twse.com.tw",
            start_date=_records_date("2025-01-01"),
            end_date=_records_date("2025-01-31"),
            parallelism=1,
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].ticker, "2330")
        self.assertEqual(records[0].date.isoformat(), "2025-01-02")
        self.assertAlmostEqual(records[0].open, 1080.0)
        self.assertAlmostEqual(records[0].close, 1090.0)
        self.assertAlmostEqual(records[0].volume, 35_001_234.0)

    @patch("financial_analysis_tool.quant.sources.tej_source.request_json")
    def test_fetch_tej_price_records_parses_datatable_payload(self, mocked_request_json) -> None:
        mocked_request_json.return_value = json.loads(
            (self.fixtures_root / "tej_prices.json").read_text(encoding="utf-8")
        )

        records = fetch_tej_price_records(
            ["2330"],
            api_key="demo-key",
            table_code="TWN/APRCD",
            base_url="https://api.tej.com.tw",
            start_date=_records_date("2025-01-01"),
            end_date=_records_date("2025-01-31"),
            parallelism=1,
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].ticker, "2330")
        self.assertEqual(records[0].date.isoformat(), "2025-01-02")
        self.assertAlmostEqual(records[0].high, 1095.0)
        self.assertAlmostEqual(records[0].close, 1090.0)


def _records_date(raw_value: str):
    return date.fromisoformat(raw_value)


if __name__ == "__main__":
    unittest.main()
