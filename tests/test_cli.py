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
        self.output_root = PROJECT_ROOT / "output"
        self.financial_output_root = self.output_root / "financial"
        self.chart_output_root = self.output_root / "charts"
        self.backtest_output_root = self.output_root / "backtests"
        self.financial_output_root.mkdir(parents=True, exist_ok=True)
        self.chart_output_root.mkdir(parents=True, exist_ok=True)
        self.backtest_output_root.mkdir(parents=True, exist_ok=True)

    def test_financial_cli_smoke_test_writes_outputs(self) -> None:
        summary_output = self.financial_output_root / f"test-summary-{os.getpid()}.json"
        chart_output = self.chart_output_root / f"test-chart-cli-{os.getpid()}.svg"
        try:
            completed = _run_command(
                sys.executable,
                "main.py",
                "--input",
                str(self.sample_csv),
                "--summary-output",
                str(summary_output),
                "--chart-output",
                str(chart_output),
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
        backtest_output = self.backtest_output_root / f"test-backtest-{os.getpid()}.json"
        try:
            completed = _run_command(
                sys.executable,
                "main.py",
                "backtest",
                "--prices",
                str(self.sample_prices_csv),
                "--backtest-output",
                str(backtest_output),
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("Quant Backtest Summary", completed.stdout)
            self.assertTrue(backtest_output.exists())

            payload = json.loads(backtest_output.read_text(encoding="utf-8"))
            self.assertEqual(payload["benchmark_label"], "Equal-Weight Universe")
            self.assertEqual(payload["rebalance_frequency"], "monthly")
            self.assertEqual(len(payload["periods"]), 9)
        finally:
            if backtest_output.exists():
                backtest_output.unlink()

    def test_module_entrypoint_help_lists_subcommands(self) -> None:
        completed = _run_command(
            sys.executable,
            "-m",
            "financial_analysis_tool",
            "--help",
            pythonpath=PROJECT_ROOT / "src",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("backtest", completed.stdout)
        self.assertIn("--log-level", completed.stdout)


def _run_command(*args: str, pythonpath: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if pythonpath is not None:
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            f"{pythonpath}{os.pathsep}{existing_pythonpath}"
            if existing_pythonpath
            else str(pythonpath)
        )

    return subprocess.run(
        list(args),
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


if __name__ == "__main__":
    unittest.main()
