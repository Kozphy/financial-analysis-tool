from __future__ import annotations

import importlib.util
import shutil
import sys
import unittest
import uuid
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

HAS_ESG_STACK = all(
    importlib.util.find_spec(module_name) is not None
    for module_name in ("numpy", "pandas", "matplotlib", "seaborn")
)

from financial_analysis_tool.config import EsgAnalysisConfig
from financial_analysis_tool.esg_pipeline import analyze_esg_dataset, run_esg_analysis_pipeline


@unittest.skipUnless(HAS_ESG_STACK, "ESG dependencies are not installed in this environment.")
class EsgPipelineTests(unittest.TestCase):
    def test_analyze_esg_dataset_returns_summary_and_insights(self) -> None:
        artifacts = analyze_esg_dataset(
            PROJECT_ROOT / "data" / "esg_metrics.csv",
            audience_name="Cathay Financial Holdings",
        )

        self.assertEqual(artifacts.summary.company_count, 6)
        self.assertEqual(len(artifacts.summary.insights), 3)
        self.assertGreater(len(artifacts.risk_signal_frame), 0)

    def test_run_esg_analysis_pipeline_writes_outputs(self) -> None:
        temp_path = PROJECT_ROOT / "output" / "test-artifacts" / uuid.uuid4().hex
        temp_path.mkdir(parents=True, exist_ok=False)

        try:
            config = EsgAnalysisConfig(
                input_path=PROJECT_ROOT / "data" / "esg_metrics.csv",
                audience_name="Cathay Financial Holdings",
                summary_output=temp_path / "reports" / "esg_summary.json",
                report_output=temp_path / "reports" / "esg_report.md",
                trend_chart_output=temp_path / "charts" / "trend.png",
                correlation_chart_output=temp_path / "charts" / "heatmap.png",
                risk_chart_output=temp_path / "charts" / "risk.png",
            )

            summary = run_esg_analysis_pipeline(config)

            self.assertEqual(summary.audience_name, "Cathay Financial Holdings")
            self.assertTrue(config.summary_output.exists())
            self.assertTrue(config.report_output.exists())
            self.assertTrue(config.trend_chart_output.exists())
            self.assertTrue(config.correlation_chart_output.exists())
            self.assertTrue(config.risk_chart_output.exists())
        finally:
            shutil.rmtree(temp_path, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
