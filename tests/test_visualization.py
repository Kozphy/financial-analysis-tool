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

from financial_analysis_tool.loader import load_financial_statements
from financial_analysis_tool.metrics import calculate_period_metrics
from financial_analysis_tool.visualization import (
    generate_financial_position_chart,
    generate_profitability_chart,
)


class VisualizationTests(unittest.TestCase):
    def test_generate_svg_charts(self) -> None:
        records = load_financial_statements(PROJECT_ROOT / "data" / "financials.csv")
        period_metrics = calculate_period_metrics(records)
        temp_path = PROJECT_ROOT / "output" / "test-artifacts" / uuid.uuid4().hex
        temp_path.mkdir(parents=True, exist_ok=False)

        try:
            profitability_path = temp_path / "profitability.svg"
            financial_position_path = temp_path / "financial_position.svg"

            generate_profitability_chart(
                period_metrics,
                profitability_path,
                company_name="Test Company",
            )
            generate_financial_position_chart(
                period_metrics,
                financial_position_path,
                company_name="Test Company",
            )

            self.assertTrue(profitability_path.exists())
            self.assertTrue(financial_position_path.exists())
            self.assertIn("Profitability Trends", profitability_path.read_text(encoding="utf-8"))
            self.assertIn("Financial Position", financial_position_path.read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(temp_path, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
