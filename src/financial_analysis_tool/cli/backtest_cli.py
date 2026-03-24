from __future__ import annotations

import argparse
import os
from datetime import date

from financial_analysis_tool.core.config import (
    DEFAULT_BACKTEST_OUTPUT,
    DEFAULT_BINANCE_BASE_URL,
    DEFAULT_PRICES_INPUT,
    DEFAULT_TEJ_BASE_URL,
    DEFAULT_TWSE_BASE_URL,
    BacktestRunConfig,
)
from financial_analysis_tool.core.exceptions import ApplicationError, InputDataError
from financial_analysis_tool.quant.reporting import build_backtest_report
from financial_analysis_tool.services.backtest_service import run_backtest_workflow


def register_backtest_subcommand(subparsers) -> None:
    parser = subparsers.add_parser(
        "backtest",
        help="Run a simple cross-sectional momentum and volatility backtest.",
    )
    parser.add_argument(
        "--price-source",
        choices=["csv", "binance", "twse", "tej"],
        default="csv",
        help="Load price data from CSV, Binance Spot, TWSE, or TEJ.",
    )
    parser.add_argument(
        "--prices",
        type=_path_type,
        default=DEFAULT_PRICES_INPUT,
        help="Path to the input price CSV file when using the csv source.",
    )
    parser.add_argument(
        "--backtest-output",
        type=_path_type,
        default=DEFAULT_BACKTEST_OUTPUT,
        help="Path to write the JSON backtest report.",
    )
    parser.add_argument(
        "--lookback-periods",
        type=int,
        default=3,
        help="Trailing periods used for momentum calculation.",
    )
    parser.add_argument(
        "--volatility-window",
        type=int,
        default=3,
        help="Trailing return periods used for volatility calculation.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=2,
        help="Number of ranked assets to hold each rebalance period.",
    )
    parser.add_argument(
        "--periods-per-year",
        type=int,
        default=12,
        help="Used to annualize performance metrics. Use 12 for monthly or 252 for daily data.",
    )
    parser.add_argument(
        "--benchmark-ticker",
        type=str,
        default=None,
        help="Optional benchmark ticker. If omitted, the benchmark is the equal-weight universe.",
    )
    parser.add_argument(
        "--momentum-weight",
        type=float,
        default=0.8,
        help="Weight assigned to the momentum rank.",
    )
    parser.add_argument(
        "--volatility-weight",
        type=float,
        default=0.2,
        help="Weight assigned to the low-volatility rank.",
    )
    parser.add_argument(
        "--binance-symbols",
        type=str,
        default="",
        help="Comma-separated Binance spot symbols, for example BTCUSDT,ETHUSDT.",
    )
    parser.add_argument(
        "--binance-interval",
        type=str,
        default="1d",
        help="Binance kline interval such as 1d, 1h, 1w, or 1M.",
    )
    parser.add_argument(
        "--binance-limit",
        type=int,
        default=365,
        help="Number of Binance klines to request per symbol. Binance supports up to 1000.",
    )
    parser.add_argument(
        "--binance-base-url",
        type=str,
        default=DEFAULT_BINANCE_BASE_URL,
        help="Binance REST base URL.",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Optional start date in YYYY-MM-DD format for Binance, TWSE, or TEJ pulls.",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default=None,
        help="Optional end date in YYYY-MM-DD format for Binance, TWSE, or TEJ pulls.",
    )
    parser.add_argument(
        "--twse-stock-nos",
        type=str,
        default="",
        help="Comma-separated TWSE stock numbers, for example 2330,2317.",
    )
    parser.add_argument(
        "--twse-base-url",
        type=str,
        default=DEFAULT_TWSE_BASE_URL,
        help="TWSE REST base URL.",
    )
    parser.add_argument(
        "--tej-symbols",
        type=str,
        default="",
        help="Comma-separated TEJ symbols, for example 2330,2317.",
    )
    parser.add_argument(
        "--tej-api-key",
        type=str,
        default=None,
        help="TEJ API key. Falls back to the TEJ_API_KEY environment variable.",
    )
    parser.add_argument(
        "--tej-table-code",
        type=str,
        default="TWN/APRCD",
        help="TEJ datatable code for daily price data.",
    )
    parser.add_argument(
        "--tej-base-url",
        type=str,
        default=DEFAULT_TEJ_BASE_URL,
        help="TEJ REST base URL.",
    )
    parser.add_argument(
        "--request-timeout",
        type=int,
        default=15,
        help="HTTP timeout in seconds for remote data sources.",
    )


def handle_backtest_command(args: argparse.Namespace) -> int:
    try:
        config = BacktestRunConfig(
            price_source=args.price_source,
            prices_path=args.prices,
            backtest_output=args.backtest_output,
            lookback_periods=args.lookback_periods,
            volatility_window=args.volatility_window,
            top_n=args.top_n,
            periods_per_year=args.periods_per_year,
            benchmark_ticker=args.benchmark_ticker,
            momentum_weight=args.momentum_weight,
            volatility_weight=args.volatility_weight,
            binance_symbols=_parse_symbols(args.binance_symbols),
            binance_interval=args.binance_interval,
            binance_limit=args.binance_limit,
            binance_base_url=args.binance_base_url,
            twse_stock_nos=_parse_symbols(args.twse_stock_nos),
            twse_base_url=args.twse_base_url,
            tej_symbols=_parse_symbols(args.tej_symbols),
            tej_api_key=args.tej_api_key or os.getenv("TEJ_API_KEY"),
            tej_base_url=args.tej_base_url,
            tej_table_code=args.tej_table_code,
            start_date=_parse_optional_date(args.start_date),
            end_date=_parse_optional_date(args.end_date),
            request_timeout=args.request_timeout,
        )
        result = run_backtest_workflow(config)
    except ApplicationError as exc:
        print(f"Error: {exc}")
        return 1

    print(build_backtest_report(result))
    print(f"\nBacktest report saved to {config.backtest_output}")
    return 0


def _parse_symbols(raw_symbols: str) -> tuple[str, ...]:
    return tuple(symbol.strip().upper() for symbol in raw_symbols.split(",") if symbol.strip())


def _parse_optional_date(raw_value: str | None) -> date | None:
    if raw_value in (None, ""):
        return None

    try:
        return date.fromisoformat(raw_value)
    except ValueError as exc:
        raise InputDataError(f"Invalid date value: {raw_value}") from exc


def _path_type(raw_value: str):
    from pathlib import Path

    return Path(raw_value)
