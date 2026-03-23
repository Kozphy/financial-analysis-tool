from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from financial_analysis_tool.quant.factors import compute_factor_snapshots
from financial_analysis_tool.quant.loader import load_price_records
from financial_analysis_tool.quant.portfolio import build_equal_weight_portfolio
from financial_analysis_tool.quant.strategy import rank_assets


class QuantStrategyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_prices_csv = PROJECT_ROOT / "data" / "prices.csv"

    def test_ranking_strategy_prefers_high_momentum_with_low_volatility(self) -> None:
        snapshots_by_date = compute_factor_snapshots(load_price_records(self.sample_prices_csv))
        april_snapshots = snapshots_by_date[_records_date("2025-04-30")]
        ranked_assets = rank_assets(april_snapshots)

        self.assertEqual(ranked_assets[0].ticker, "ALP")
        self.assertEqual([asset.ticker for asset in ranked_assets[:2]], ["ALP", "BET"])
        self.assertGreater(ranked_assets[0].score, ranked_assets[-1].score)

    def test_portfolio_builder_creates_equal_weight_positions(self) -> None:
        snapshots_by_date = compute_factor_snapshots(load_price_records(self.sample_prices_csv))
        ranked_assets = rank_assets(snapshots_by_date[_records_date("2025-04-30")])

        positions = build_equal_weight_portfolio(ranked_assets, top_n=2)

        self.assertEqual([position.ticker for position in positions], ["ALP", "BET"])
        self.assertAlmostEqual(positions[0].weight, 0.5)
        self.assertAlmostEqual(positions[1].weight, 0.5)


def _records_date(raw_value: str):
    from datetime import date

    return date.fromisoformat(raw_value)


if __name__ == "__main__":
    unittest.main()
