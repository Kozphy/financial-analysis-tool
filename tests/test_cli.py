from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CLITests(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_csv = PROJECT_ROOT / "data" / "financials.csv"
        self.sample_prices_csv = PROJECT_ROOT / "data" / "prices.csv"
        self.temp_root = PROJECT_ROOT / "output"
        self.temp_root.mkdir(exist_ok=True)

    def test_financial_cli_smoke_test_writes_outputs(self) -> None:
        summary_output = self.temp_root / f"test-summary-{os.getpid()}.json"
        chart_output = self.temp_root / f"test-chart-cli-{os.getpid()}.svg"
        try:
            command = [
                sys.executable,
                "main.py",
                "--input",
                str(self.sample_csv),
                "--summary-output",
                str(summary_output),
                "--chart-output",
                str(chart_output),
            ]

            completed = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("Financial Performance Summary", completed.stdout)
            self.assertTrue(summary_output.exists())
            self.assertTrue(chart_output.exists())

            payload = json.loads(summary_output.read_text(encoding="utf-8"))
            self.assertEqual(payload["latest_period"]["period"], "2025-Q4")
        finally:
            if summary_output.exists():
                summary_output.unlink()
            if chart_output.exists():
                chart_output.unlink()

    def test_backtest_cli_smoke_test_writes_output(self) -> None:
        backtest_output = self.temp_root / f"test-backtest-{os.getpid()}.json"
        try:
            command = [
                sys.executable,
                "main.py",
                "backtest",
                "--prices",
                str(self.sample_prices_csv),
                "--backtest-output",
                str(backtest_output),
            ]

            completed = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("Quant Backtest Summary", completed.stdout)
            self.assertTrue(backtest_output.exists())

            payload = json.loads(backtest_output.read_text(encoding="utf-8"))
            self.assertEqual(payload["benchmark_label"], "Equal-Weight Universe")
            self.assertEqual(len(payload["periods"]), 8)
        finally:
            if backtest_output.exists():
                backtest_output.unlink()


if __name__ == "__main__":
    unittest.main()
