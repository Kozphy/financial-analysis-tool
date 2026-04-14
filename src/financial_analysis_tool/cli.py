"""Command-line entrypoint for the financial analysis pipeline."""

from __future__ import annotations

import argparse

from .config import (
    DEFAULT_COMPANY_NAME,
    DEFAULT_FINANCIAL_POSITION_CHART,
    DEFAULT_INPUT_PATH,
    DEFAULT_PROFITABILITY_CHART,
    DEFAULT_REPORT_OUTPUT,
    DEFAULT_SUMMARY_OUTPUT,
    AnalysisConfig,
)
from .pipeline import run_analysis_pipeline
from .reporting import build_console_summary


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for batch financial analysis runs."""
    parser = argparse.ArgumentParser(
        description="Load company financial statement data, calculate core metrics, and generate presentation-ready outputs."
    )
    parser.add_argument(
        "--input",
        type=_path_type,
        default=DEFAULT_INPUT_PATH,
        help="Path to the financial statement CSV file.",
    )
    parser.add_argument(
        "--company-name",
        type=str,
        default=DEFAULT_COMPANY_NAME,
        help="Company name used in reports and chart titles.",
    )
    parser.add_argument(
        "--summary-output",
        type=_path_type,
        default=DEFAULT_SUMMARY_OUTPUT,
        help="Path to write the JSON summary output.",
    )
    parser.add_argument(
        "--report-output",
        type=_path_type,
        default=DEFAULT_REPORT_OUTPUT,
        help="Path to write the Markdown executive summary.",
    )
    parser.add_argument(
        "--profitability-chart-output",
        type=_path_type,
        default=DEFAULT_PROFITABILITY_CHART,
        help="Path to write the profitability trend chart.",
    )
    parser.add_argument(
        "--financial-position-chart-output",
        type=_path_type,
        default=DEFAULT_FINANCIAL_POSITION_CHART,
        help="Path to write the liquidity and leverage chart.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments, run the pipeline, and print a terminal summary."""
    parser = build_parser()
    args = parser.parse_args(argv)

    config = AnalysisConfig(
        input_path=args.input,
        company_name=args.company_name,
        summary_output=args.summary_output,
        report_output=args.report_output,
        profitability_chart_output=args.profitability_chart_output,
        financial_position_chart_output=args.financial_position_chart_output,
    )
    summary = run_analysis_pipeline(config)
    print(build_console_summary(summary))
    print(f"\nJSON summary saved to {config.summary_output}")
    print(f"Markdown summary saved to {config.report_output}")
    print(f"Profitability chart saved to {config.profitability_chart_output}")
    print(f"Financial position chart saved to {config.financial_position_chart_output}")
    return 0


def _path_type(raw_value: str):
    """Convert a raw CLI path argument into a Path instance."""
    from pathlib import Path

    return Path(raw_value)
