from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from financial_analysis_tool.financial.loader import fetch_mops_financial_records, load_financial_records
from financial_analysis_tool.financial.metrics import (
    analyze_records,
    summarize_company_performance,
)


class FinancialMetricsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_csv = PROJECT_ROOT / "data" / "financials.csv"
        self.fixtures_root = PROJECT_ROOT / "tests" / "fixtures"

    def test_loader_reads_sample_data(self) -> None:
        records = load_financial_records(self.sample_csv)

        self.assertEqual(len(records), 8)
        self.assertEqual(records[0].period, "2024-Q1")
        self.assertAlmostEqual(records[-1].revenue, 1_840_000.0)

    def test_metrics_are_calculated_for_each_period(self) -> None:
        records = load_financial_records(self.sample_csv)
        analyses = analyze_records(records)
        latest = analyses[-1]

        self.assertEqual(len(analyses), 8)
        self.assertAlmostEqual(latest.gross_profit, 1_150_000.0)
        self.assertAlmostEqual(latest.operating_income, 670_000.0)
        self.assertAlmostEqual(latest.net_margin, 372_000.0 / 1_840_000.0)
        self.assertAlmostEqual(analyses[1].revenue_growth, 0.056)

    def test_summary_highlights_latest_and_best_periods(self) -> None:
        summary = summarize_company_performance(
            analyze_records(load_financial_records(self.sample_csv))
        )

        self.assertEqual(summary.latest_period.period, "2025-Q4")
        self.assertEqual(summary.best_growth_period.period, "2024-Q3")
        self.assertEqual(summary.highest_net_margin_period.period, "2025-Q4")
        self.assertAlmostEqual(summary.overall_revenue_growth, 0.472)

    @patch("financial_analysis_tool.financial.sources.mops_source.request_text")
    def test_fetch_mops_financial_records_parses_company_quarter(self, mocked_request_text) -> None:
        mocked_request_text.return_value = (
            self.fixtures_root / "mops_company_quarter.html"
        ).read_text(encoding="utf-8")

        records = fetch_mops_financial_records(
            "2330",
            start_year=2025,
            end_year=2025,
            seasons=(1,),
            base_url="https://mops.twse.com.tw",
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].period, "2025-Q1")
        self.assertAlmostEqual(records[0].revenue, 2_000_000.0)
        self.assertAlmostEqual(records[0].cost_of_revenue, 800_000.0)
        self.assertAlmostEqual(records[0].operating_expenses, 450_000.0)
        self.assertAlmostEqual(records[0].net_income, 520_000.0)


if __name__ == "__main__":
    unittest.main()
