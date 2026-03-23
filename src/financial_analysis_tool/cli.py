from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .backtest import run_backtest
from .data_loader import load_financial_records, load_price_records
from .metrics import analyze_records, summarize_company_performance
from .reporting import (
    build_backtest_report,
    build_console_report,
    write_backtest_json,
    write_summary_json,
)
from .visualization import generate_trend_chart


DEFAULT_INPUT = Path("data/financials.csv")
DEFAULT_SUMMARY_OUTPUT = Path("output/summary.json")
DEFAULT_CHART_OUTPUT = Path("output/charts.svg")
DEFAULT_PRICES_INPUT = Path("data/prices.csv")
DEFAULT_BACKTEST_OUTPUT = Path("output/backtest.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze company financial performance and run simple quant backtests from structured CSV data."
    )
    subparsers = parser.add_subparsers(dest="command")

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to the input CSV file.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=DEFAULT_SUMMARY_OUTPUT,
        help="Path to write the JSON performance summary.",
    )
    parser.add_argument(
        "--chart-output",
        type=Path,
        default=DEFAULT_CHART_OUTPUT,
        help="Path to write the SVG trend chart.",
    )
    parser.add_argument(
        "--no-chart",
        action="store_true",
        help="Skip chart generation.",
    )

    backtest_parser = subparsers.add_parser(
        "backtest",
        help="Run a simple cross-sectional momentum and volatility backtest.",
    )
    backtest_parser.add_argument(
        "--prices",
        type=Path,
        default=DEFAULT_PRICES_INPUT,
        help="Path to the input price CSV file.",
    )
    backtest_parser.add_argument(
        "--backtest-output",
        type=Path,
        default=DEFAULT_BACKTEST_OUTPUT,
        help="Path to write the JSON backtest report.",
    )
    backtest_parser.add_argument(
        "--lookback-periods",
        type=int,
        default=3,
        help="Trailing periods used for momentum calculation.",
    )
    backtest_parser.add_argument(
        "--volatility-window",
        type=int,
        default=3,
        help="Trailing return periods used for volatility calculation.",
    )
    backtest_parser.add_argument(
        "--top-n",
        type=int,
        default=2,
        help="Number of ranked assets to hold each rebalance period.",
    )
    backtest_parser.add_argument(
        "--periods-per-year",
        type=int,
        default=12,
        help="Used to annualize performance metrics. Use 12 for monthly or 252 for daily data.",
    )
    backtest_parser.add_argument(
        "--benchmark-ticker",
        type=str,
        default=None,
        help="Optional benchmark ticker. If omitted, the benchmark is the equal-weight universe.",
    )
    backtest_parser.add_argument(
        "--momentum-weight",
        type=float,
        default=0.8,
        help="Weight assigned to the momentum rank.",
    )
    backtest_parser.add_argument(
        "--volatility-weight",
        type=float,
        default=0.2,
        help="Weight assigned to the low-volatility rank.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "backtest":
        return _run_backtest(args)

    return _run_fundamentals(args)


def _run_fundamentals(args: argparse.Namespace) -> int:
    try:
        records = load_financial_records(args.input)
        analyses = analyze_records(records)
        summary = summarize_company_performance(analyses)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(build_console_report(summary))

    write_summary_json(summary, args.summary_output)
    print(f"\nJSON summary saved to {args.summary_output}")

    if not args.no_chart:
        generate_trend_chart(analyses, args.chart_output)
        print(f"Chart saved to {args.chart_output}")

    return 0


def _run_backtest(args: argparse.Namespace) -> int:
    try:
        price_records = load_price_records(args.prices)
        result = run_backtest(
            price_records,
            lookback_periods=args.lookback_periods,
            volatility_window=args.volatility_window,
            top_n=args.top_n,
            periods_per_year=args.periods_per_year,
            benchmark_ticker=args.benchmark_ticker,
            momentum_weight=args.momentum_weight,
            volatility_weight=args.volatility_weight,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(build_backtest_report(result))
    write_backtest_json(result, args.backtest_output)
    print(f"\nBacktest report saved to {args.backtest_output}")
    return 0
