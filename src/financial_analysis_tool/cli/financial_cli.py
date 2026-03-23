from __future__ import annotations

import argparse

from financial_analysis_tool.core.config import (
    DEFAULT_CHART_OUTPUT,
    DEFAULT_INPUT,
    DEFAULT_SUMMARY_OUTPUT,
    FinancialRunConfig,
)
from financial_analysis_tool.core.exceptions import ApplicationError
from financial_analysis_tool.financial.reporting import build_console_report
from financial_analysis_tool.services.financial_service import run_financial_workflow


def register_financial_arguments(parser: argparse.ArgumentParser) -> None:
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


def handle_financial_command(args: argparse.Namespace) -> int:
    try:
        config = FinancialRunConfig(
            input_path=args.input,
            summary_output=args.summary_output,
            chart_output=args.chart_output,
            generate_chart=not args.no_chart,
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
