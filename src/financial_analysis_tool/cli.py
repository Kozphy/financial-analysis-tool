from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .data_loader import load_financial_records
from .metrics import analyze_records, summarize_company_performance
from .reporting import build_console_report, write_summary_json
from .visualization import generate_trend_chart


DEFAULT_INPUT = Path("data/financials.csv")
DEFAULT_SUMMARY_OUTPUT = Path("output/summary.json")
DEFAULT_CHART_OUTPUT = Path("output/charts.svg")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze company financial performance from structured CSV data."
    )
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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

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
