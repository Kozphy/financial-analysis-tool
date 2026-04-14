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
from financial_analysis_tool.reporting import build_console_summary, build_markdown_report


class ReportingTests(unittest.TestCase):
    def test_reports_include_profitability_and_balance_sheet_metrics(self) -> None:
        records = load_financial_statements(PROJECT_ROOT / "data" / "financials.csv")
        period_metrics = calculate_period_metrics(records)
        summary = build_analysis_summary(period_metrics, company_name="Test Company")

        console_text = build_console_summary(summary)
        markdown_text = build_markdown_report(summary)

        self.assertIn("Latest current ratio", console_text)
        self.assertIn("Latest debt ratio", console_text)
        self.assertIn("| Current Ratio | Debt Ratio |", markdown_text)
        self.assertIn("Liquidity and leverage remained controlled", markdown_text)


if __name__ == "__main__":
    unittest.main()
