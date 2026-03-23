from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from financial_analysis_tool.financial.loader import load_financial_records
from financial_analysis_tool.financial.metrics import (
    analyze_records,
    summarize_company_performance,
)
from financial_analysis_tool.financial.reporting import build_console_report
from financial_analysis_tool.financial.visualization import generate_trend_chart


class FinancialReportingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_csv = PROJECT_ROOT / "data" / "financials.csv"
        self.temp_root = PROJECT_ROOT / "output"
        self.temp_root.mkdir(exist_ok=True)

    def test_console_report_contains_summary(self) -> None:
        summary = summarize_company_performance(
            analyze_records(load_financial_records(self.sample_csv))
        )

        report = build_console_report(summary)
        self.assertIn("Financial Performance Summary", report)
        self.assertIn("2025-Q4", report)

    def test_chart_generation_writes_svg(self) -> None:
        analyses = analyze_records(load_financial_records(self.sample_csv))
        chart_path = self.temp_root / f"test-chart-{os.getpid()}.svg"
        try:
            generate_trend_chart(analyses, chart_path)

            contents = chart_path.read_text(encoding="utf-8")
            self.assertTrue(chart_path.exists())
            self.assertIn("<svg", contents)
            self.assertIn("Company Financial Trends", contents)
        finally:
            if chart_path.exists():
                chart_path.unlink()


if __name__ == "__main__":
    unittest.main()
