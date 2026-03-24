from __future__ import annotations

import argparse

from financial_analysis_tool.core.config import (
    DEFAULT_CHART_OUTPUT,
    DEFAULT_INPUT,
    DEFAULT_MOPS_BASE_URL,
    DEFAULT_SUMMARY_OUTPUT,
    FinancialRunConfig,
)
from financial_analysis_tool.core.exceptions import ApplicationError
from financial_analysis_tool.financial.reporting import build_console_report
from financial_analysis_tool.services.financial_service import run_financial_workflow


def register_financial_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--financial-source",
        choices=["csv", "mops"],
        default="csv",
        help="Load financial statements from a local CSV file or Taiwan MOPS.",
    )
    parser.add_argument(
        "--input",
        type=_path_type,
        default=DEFAULT_INPUT,
        help="Path to the input financial CSV file.",
    )
    parser.add_argument(
        "--summary-output",
        type=_path_type,
        default=DEFAULT_SUMMARY_OUTPUT,
        help="Path to write the JSON performance summary.",
    )
    parser.add_argument(
        "--chart-output",
        type=_path_type,
        default=DEFAULT_CHART_OUTPUT,
        help="Path to write the SVG trend chart.",
    )
    parser.add_argument(
        "--no-chart",
        action="store_true",
        help="Skip chart generation.",
    )
    parser.add_argument(
        "--mops-company-id",
        type=str,
        default=None,
        help="MOPS company id, for example 2330.",
    )
    parser.add_argument(
        "--mops-market",
        choices=["all", "sii", "otc", "rotc", "pub"],
        default="all",
        help="MOPS market segment to query.",
    )
    parser.add_argument(
        "--mops-start-year",
        type=int,
        default=None,
        help="MOPS start year. Accepts either Gregorian year (2024) or ROC year (113).",
    )
    parser.add_argument(
        "--mops-end-year",
        type=int,
        default=None,
        help="MOPS end year. Accepts either Gregorian year (2025) or ROC year (114).",
    )
    parser.add_argument(
        "--mops-seasons",
        type=str,
        default="1,2,3,4",
        help="Comma-separated MOPS fiscal quarters, for example 1,2,3,4.",
    )
    parser.add_argument(
        "--mops-base-url",
        type=str,
        default=DEFAULT_MOPS_BASE_URL,
        help="MOPS base URL.",
    )
    parser.add_argument(
        "--request-timeout",
        type=int,
        default=15,
        help="HTTP timeout in seconds for remote data sources.",
    )


def handle_financial_command(args: argparse.Namespace) -> int:
    try:
        config = FinancialRunConfig(
            financial_source=args.financial_source,
            input_path=args.input,
            summary_output=args.summary_output,
            chart_output=args.chart_output,
            generate_chart=not args.no_chart,
            mops_company_id=args.mops_company_id,
            mops_market=args.mops_market,
            mops_start_year=args.mops_start_year,
            mops_end_year=args.mops_end_year,
            mops_seasons=_parse_quarters(args.mops_seasons),
            mops_base_url=args.mops_base_url,
            request_timeout=args.request_timeout,
        )
        summary = run_financial_workflow(config)
    except ApplicationError as exc:
        print(f"Error: {exc}")
        return 1

    print(build_console_report(summary))
    print(f"\nJSON summary saved to {config.summary_output}")
    if config.generate_chart:
        print(f"Chart saved to {config.chart_output}")
    return 0


def _path_type(raw_value: str):
    from pathlib import Path

    return Path(raw_value)


def _parse_quarters(raw_value: str) -> tuple[int, ...]:
    try:
        return tuple(
            int(part.strip())
            for part in raw_value.split(",")
            if part.strip()
        )
    except ValueError as exc:
        raise ApplicationError(f"Invalid quarter list: {raw_value}") from exc
