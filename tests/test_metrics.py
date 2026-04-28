"""Metric tests for financial ratios and summary aggregation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from financial_analysis_tool.loader import load_financial_statements
from financial_analysis_tool.metrics import build_analysis_summary, calculate_period_metrics


class MetricsTests(unittest.TestCase):
    """Validate profitability, liquidity, and leverage calculations."""

    def setUp(self) -> None:
        """Load reusable sample financial metrics for each test."""
        records = load_financial_statements(PROJECT_ROOT / "data" / "financials.csv")
        self.period_metrics = calculate_period_metrics(records)

    def test_calculate_period_metrics_includes_required_ratios(self) -> None:
        """Verify period metrics include expected latest-period ratios."""
        latest = self.period_metrics[-1]

        self.assertAlmostEqual(latest.gross_margin or 0.0, 0.625)
        self.assertAlmostEqual(latest.operating_margin or 0.0, 0.3641304348)
        self.assertAlmostEqual(latest.net_margin or 0.0, 0.2021739130)
        self.assertAlmostEqual(latest.current_ratio or 0.0, 2.1214788732)
        self.assertAlmostEqual(latest.debt_ratio or 0.0, 0.3600682594)

    def test_build_analysis_summary_aggregates_latest_period(self) -> None:
        """Verify the summary surfaces latest-period and aggregate highlights."""
        summary = build_analysis_summary(self.period_metrics, company_name="Test Company")

        self.assertEqual(summary.company_name, "Test Company")
        self.assertEqual(summary.latest_period.period, "2025-Q4")
        self.assertEqual(summary.best_growth_period.period, "2024-Q3")
        self.assertEqual(summary.strongest_liquidity_period.period, "2025-Q4")
        self.assertEqual(summary.lowest_debt_period.period, "2025-Q4")


if __name__ == "__main__":
    unittest.main()
