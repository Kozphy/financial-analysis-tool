from __future__ import annotations

import argparse

from .backtest_cli import handle_backtest_command, register_backtest_subcommand
from .financial_cli import handle_financial_command, register_financial_arguments


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze company financial performance and run simple quant backtests from structured CSV data."
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
        help="Set the application log level.",
    )
    register_financial_arguments(parser)
    parser.set_defaults(handler=handle_financial_command)

    subparsers = parser.add_subparsers(dest="command")
    register_backtest_subcommand(subparsers, handler=handle_backtest_command)
    return parser
