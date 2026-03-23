from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from financial_analysis_tool.quant.backtest import run_backtest
from financial_analysis_tool.quant.loader import load_price_records


class BacktestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_prices_csv = PROJECT_ROOT / "data" / "prices.csv"

    def test_backtest_engine_builds_ranked_strategy_results(self) -> None:
        result = run_backtest(load_price_records(self.sample_prices_csv))

        self.assertEqual(len(result.periods), 8)
        self.assertEqual(result.benchmark_label, "Equal-Weight Universe")
        self.assertGreater(result.total_return, 0)
        self.assertGreater(result.total_return, result.benchmark_total_return)
        self.assertIsNotNone(result.annualized_return)
        self.assertIsNotNone(result.annualized_volatility)
        self.assertEqual(
            [position.ticker for position in result.periods[0].positions],
            ["ALP", "BET"],
        )


if __name__ == "__main__":
    unittest.main()
