from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from statistics import stdev


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from financial_analysis_tool.backtest import run_backtest
from financial_analysis_tool.data_loader import load_financial_records, load_price_records
from financial_analysis_tool.factors import compute_factor_snapshots
from financial_analysis_tool.metrics import analyze_records, summarize_company_performance
from financial_analysis_tool.strategy import rank_assets
from financial_analysis_tool.visualization import generate_trend_chart


class FinancialAnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_csv = PROJECT_ROOT / "data" / "financials.csv"
        self.sample_prices_csv = PROJECT_ROOT / "data" / "prices.csv"
        self.temp_root = PROJECT_ROOT / "output"
        self.temp_root.mkdir(exist_ok=True)

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

    def test_cli_smoke_test_writes_outputs(self) -> None:
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

    def test_price_loader_reads_sample_price_data(self) -> None:
        records = load_price_records(self.sample_prices_csv)

        self.assertEqual(len(records), 60)
        self.assertEqual(records[0].ticker, "ALP")
        self.assertEqual(records[0].date.isoformat(), "2025-01-31")
        self.assertAlmostEqual(records[-1].close, 111.0)

    def test_factor_snapshots_include_momentum_and_volatility(self) -> None:
        snapshots_by_date = compute_factor_snapshots(load_price_records(self.sample_prices_csv))
        april_snapshots = snapshots_by_date[records_date("2025-04-30")]
        alp_snapshot = next(snapshot for snapshot in april_snapshots if snapshot.ticker == "ALP")
        expected_volatility = stdev(
            [
                0.02,
                (104.0 - 102.0) / 102.0,
                (107.0 - 104.0) / 104.0,
            ]
        )

        self.assertEqual(len(april_snapshots), 5)
        self.assertAlmostEqual(alp_snapshot.momentum, 0.07)
        self.assertAlmostEqual(alp_snapshot.volatility, expected_volatility)
        self.assertAlmostEqual(alp_snapshot.forward_return, (110.0 - 107.0) / 107.0)

    def test_ranking_strategy_prefers_high_momentum_with_low_volatility(self) -> None:
        snapshots_by_date = compute_factor_snapshots(load_price_records(self.sample_prices_csv))
        april_snapshots = snapshots_by_date[records_date("2025-04-30")]
        ranked_assets = rank_assets(april_snapshots)

        self.assertEqual(ranked_assets[0].ticker, "ALP")
        self.assertEqual([asset.ticker for asset in ranked_assets[:2]], ["ALP", "BET"])
        self.assertGreater(ranked_assets[0].score, ranked_assets[-1].score)

    def test_backtest_engine_builds_ranked_strategy_results(self) -> None:
        result = run_backtest(load_price_records(self.sample_prices_csv))

        self.assertEqual(len(result.periods), 8)
        self.assertEqual(result.benchmark_label, "Equal-Weight Universe")
        self.assertGreater(result.total_return, 0)
        self.assertGreater(result.total_return, result.benchmark_total_return)
        self.assertIsNotNone(result.annualized_return)
        self.assertIsNotNone(result.annualized_volatility)
        self.assertEqual(
            [asset.ticker for asset in result.periods[0].selected_assets],
            ["ALP", "BET"],
        )

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


def records_date(raw_value: str):
    from datetime import date

    return date.fromisoformat(raw_value)


if __name__ == "__main__":
    unittest.main()
