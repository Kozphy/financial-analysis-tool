from __future__ import annotations

import argparse

from .backtest_cli import handle_backtest_command, register_backtest_subcommand
from .financial_cli import handle_financial_command, register_financial_arguments


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze company financial performance and run simple quant backtests from structured CSV data."
    )
    register_financial_arguments(parser)
    subparsers = parser.add_subparsers(dest="command")
    register_backtest_subcommand(subparsers)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "backtest":
        return handle_backtest_command(args)
    return handle_financial_command(args)
