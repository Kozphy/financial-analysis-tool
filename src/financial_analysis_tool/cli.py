"""Command-line entrypoint for the financial and ESG analysis workflows."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import (
    DEFAULT_COMPANY_NAME,
    DEFAULT_ESG_AUDIENCE,
    DEFAULT_ESG_CORRELATION_CHART,
    DEFAULT_ESG_INPUT_PATH,
    DEFAULT_ESG_REPORT_OUTPUT,
    DEFAULT_ESG_RISK_CHART,
    DEFAULT_ESG_SUMMARY_OUTPUT,
    DEFAULT_ESG_TREND_CHART,
    DEFAULT_FINANCIAL_POSITION_CHART,
    DEFAULT_INPUT_PATH,
    DEFAULT_PROFITABILITY_CHART,
    DEFAULT_REPORT_OUTPUT,
    DEFAULT_SUMMARY_OUTPUT,
    AnalysisConfig,
    EsgAnalysisConfig,
)
from .esg_pipeline import run_esg_analysis_pipeline
from .esg_reporting import build_esg_console_summary
from .pipeline import run_analysis_pipeline
from .reporting import build_console_summary


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for financial analysis and ESG analysis runs."""
    parser = argparse.ArgumentParser(
        description="Run financial statement analysis or ESG portfolio analysis from structured CSV datasets."
    )
    subparsers = parser.add_subparsers(dest="command")
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
    esg_parser = subparsers.add_parser(
        "esg",
        help="Run the ESG analysis workflow.",
        description="Load ESG portfolio data, clean it, surface insights, and generate charts and reports.",
    )
    esg_parser.add_argument(
        "--input",
        type=_path_type,
        default=DEFAULT_ESG_INPUT_PATH,
        help="Path to the ESG metrics CSV file.",
    )
    esg_parser.add_argument(
        "--audience-name",
        type=str,
        default=DEFAULT_ESG_AUDIENCE,
        help="Stakeholder or institution name used in the ESG report.",
    )
    esg_parser.add_argument(
        "--summary-output",
        type=_path_type,
        default=DEFAULT_ESG_SUMMARY_OUTPUT,
        help="Path to write the ESG JSON summary output.",
    )
    esg_parser.add_argument(
        "--report-output",
        type=_path_type,
        default=DEFAULT_ESG_REPORT_OUTPUT,
        help="Path to write the ESG Markdown business report.",
    )
    esg_parser.add_argument(
        "--trend-chart-output",
        type=_path_type,
        default=DEFAULT_ESG_TREND_CHART,
        help="Path to write the ESG carbon intensity trend chart.",
    )
    esg_parser.add_argument(
        "--correlation-chart-output",
        type=_path_type,
        default=DEFAULT_ESG_CORRELATION_CHART,
        help="Path to write the ESG correlation heatmap.",
    )
    esg_parser.add_argument(
        "--risk-chart-output",
        type=_path_type,
        default=DEFAULT_ESG_RISK_CHART,
        help="Path to write the ESG risk signal chart.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments, run the selected pipeline, and print a terminal summary."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "esg":
        config = EsgAnalysisConfig(
            input_path=args.input,
            audience_name=args.audience_name,
            summary_output=args.summary_output,
            report_output=args.report_output,
            trend_chart_output=args.trend_chart_output,
            correlation_chart_output=args.correlation_chart_output,
            risk_chart_output=args.risk_chart_output,
        )
        summary = run_esg_analysis_pipeline(config)
        print(build_esg_console_summary(summary))
        print(f"\nJSON summary saved to {config.summary_output}")
        print(f"Markdown summary saved to {config.report_output}")
        print(f"Trend chart saved to {config.trend_chart_output}")
        print(f"Correlation heatmap saved to {config.correlation_chart_output}")
        print(f"Risk signal chart saved to {config.risk_chart_output}")
        return 0

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
    return Path(raw_value)
