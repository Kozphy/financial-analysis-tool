from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from financial_analysis_tool.core.exceptions import DataAlignmentError
from financial_analysis_tool.quant.backtest import _select_rebalance_dates, run_backtest
from financial_analysis_tool.quant.loader import load_price_records
from financial_analysis_tool.quant.models import PriceRecord


class BacktestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_prices_csv = PROJECT_ROOT / "data" / "prices.csv"

    def test_backtest_engine_builds_ranked_strategy_results(self) -> None:
        result = run_backtest(load_price_records(self.sample_prices_csv))
        elapsed_days = (result.periods[-1].next_date - result.periods[0].rebalance_date).days
        expected_annualized_return = (result.periods[-1].strategy_equity ** (365 / elapsed_days)) - 1

        self.assertEqual(len(result.periods), 9)
        self.assertEqual(result.benchmark_label, "Equal-Weight Universe")
        self.assertGreater(result.total_return, 0)
        self.assertEqual(result.rebalance_frequency, "monthly")
        self.assertEqual(result.benchmark_alignment, "strict")
        self.assertEqual(result.periods[0].rebalance_date, date(2025, 3, 31))
        self.assertIsNotNone(result.annualized_return)
        self.assertIsNotNone(result.annualized_volatility)
        self.assertAlmostEqual(result.annualized_return, expected_annualized_return)
        self.assertEqual(
            [position.ticker for position in result.periods[0].positions],
            ["BET", "ALP"],
        )

    def test_backtest_raises_when_benchmark_is_missing_in_strict_mode(self) -> None:
        records = [
            record
            for record in load_price_records(self.sample_prices_csv)
            if not (record.ticker == "SPY" and record.date.isoformat() == "2025-12-31")
        ]

        with self.assertRaises(DataAlignmentError):
            run_backtest(
                records,
                benchmark_ticker="SPY",
                benchmark_alignment="strict",
            )

    def test_backtest_intersect_alignment_builds_schedule_from_shared_dates(self) -> None:
        records = _build_daily_records(include_benchmark_day_four=False)

        result = run_backtest(
            records,
            momentum_lookback_days=1,
            volatility_lookback_days=2,
            rebalance_frequency="daily",
            benchmark_ticker="SPY",
            benchmark_alignment="intersect",
            periods_per_year=252,
        )

        self.assertEqual(len(result.periods), 1)
        self.assertEqual(result.periods[0].rebalance_date, date(2025, 1, 3))
        self.assertEqual(result.periods[0].next_date, date(2025, 1, 5))

    def test_rebalance_dates_use_last_available_date_in_each_bucket(self) -> None:
        candidate_dates = [
            date(2025, 1, 3),
            date(2025, 1, 31),
            date(2025, 2, 14),
            date(2025, 2, 28),
            date(2025, 3, 31),
        ]

        self.assertEqual(
            _select_rebalance_dates(candidate_dates, frequency="monthly"),
            [date(2025, 1, 31), date(2025, 2, 28), date(2025, 3, 31)],
        )
        self.assertEqual(
            _select_rebalance_dates(candidate_dates, frequency="daily"),
            candidate_dates,
        )


def _build_daily_records(*, include_benchmark_day_four: bool) -> list[PriceRecord]:
    dates = [
        date(2025, 1, 1),
        date(2025, 1, 2),
        date(2025, 1, 3),
        date(2025, 1, 4),
        date(2025, 1, 5),
    ]
    closes_by_ticker = {
        "AAA": [100.0, 102.0, 104.0, 108.0, 110.0],
        "BBB": [100.0, 101.0, 103.0, 104.0, 107.0],
        "SPY": [100.0, 101.0, 102.0, 103.0, 104.0],
    }
    records: list[PriceRecord] = []
    for ticker, closes in closes_by_ticker.items():
        for record_date, close in zip(dates, closes):
            if ticker == "SPY" and record_date == date(2025, 1, 4) and not include_benchmark_day_four:
                continue
            records.append(
                PriceRecord(
                    date=record_date,
                    ticker=ticker,
                    open=close,
                    high=close,
                    low=close,
                    close=close,
                    volume=1.0,
                )
            )
    return records


if __name__ == "__main__":
    unittest.main()
