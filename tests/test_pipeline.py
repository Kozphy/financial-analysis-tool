"""Financial pipeline tests for in-memory analysis and artifact writing."""

from __future__ import annotations

import shutil
import sys
import unittest
import uuid
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from financial_analysis_tool.config import AnalysisConfig
from financial_analysis_tool.pipeline import analyze_financial_statements, run_analysis_pipeline


class PipelineTests(unittest.TestCase):
    """Validate the financial statement pipeline end to end."""

    def test_analyze_financial_statements_returns_period_metrics(self) -> None:
        """Verify in-memory financial analysis returns records, metrics, and summary."""
        artifacts = analyze_financial_statements(
            PROJECT_ROOT / "data" / "financials.csv",
            company_name="Test Company",
        )

        self.assertEqual(len(artifacts.records), 8)
        self.assertEqual(len(artifacts.period_metrics), 8)
        self.assertEqual(artifacts.summary.latest_period.period, "2025-Q4")

    def test_run_analysis_pipeline_writes_outputs(self) -> None:
        """Verify the full financial pipeline writes JSON, Markdown, and charts."""
        temp_path = PROJECT_ROOT / "output" / "test-artifacts" / uuid.uuid4().hex
        temp_path.mkdir(parents=True, exist_ok=False)

        try:
            config = AnalysisConfig(
                input_path=PROJECT_ROOT / "data" / "financials.csv",
                company_name="Test Company",
                summary_output=temp_path / "reports" / "summary.json",
                report_output=temp_path / "reports" / "summary.md",
                profitability_chart_output=temp_path / "charts" / "profitability.svg",
                financial_position_chart_output=temp_path / "charts" / "position.svg",
            )

            summary = run_analysis_pipeline(config)

            self.assertEqual(summary.latest_period.period, "2025-Q4")
            self.assertTrue(config.summary_output.exists())
            self.assertTrue(config.report_output.exists())
            self.assertTrue(config.profitability_chart_output.exists())
            self.assertTrue(config.financial_position_chart_output.exists())
        finally:
            shutil.rmtree(temp_path, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
