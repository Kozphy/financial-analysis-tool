from __future__ import annotations

import os
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_package_module_help_renders(self) -> None:
        env = dict(**os.environ)
        env["PYTHONPATH"] = str(PROJECT_ROOT / "src")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "financial_analysis_tool",
                "--help",
            ],
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Run financial statement analysis or ESG portfolio analysis", result.stdout)

    def test_main_entrypoint_runs_end_to_end(self) -> None:
        temp_path = PROJECT_ROOT / "output" / "test-artifacts" / uuid.uuid4().hex
        temp_path.mkdir(parents=True, exist_ok=False)

        try:
            summary_output = temp_path / "reports" / "summary.json"
            report_output = temp_path / "reports" / "summary.md"
            profitability_output = temp_path / "charts" / "profitability.svg"
            financial_position_output = temp_path / "charts" / "position.svg"

            result = subprocess.run(
                [
                    sys.executable,
                    "main.py",
                    "--company-name",
                    "CLI Test Company",
                    "--summary-output",
                    str(summary_output),
                    "--report-output",
                    str(report_output),
                    "--profitability-chart-output",
                    str(profitability_output),
                    "--financial-position-chart-output",
                    str(financial_position_output),
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("Financial Analysis Summary", result.stdout)
            self.assertTrue(summary_output.exists())
            self.assertTrue(report_output.exists())
            self.assertTrue(profitability_output.exists())
            self.assertTrue(financial_position_output.exists())
        finally:
            shutil.rmtree(temp_path, ignore_errors=True)

    def test_esg_subcommand_help_renders(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "main.py",
                "esg",
                "--help",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Load ESG portfolio data", result.stdout)


if __name__ == "__main__":
    unittest.main()
