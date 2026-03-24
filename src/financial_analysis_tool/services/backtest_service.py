from __future__ import annotations

from financial_analysis_tool.core.config import BacktestRunConfig
from financial_analysis_tool.core.exceptions import InputDataError

from ..quant.backtest import run_backtest
from ..quant.loader import (
    fetch_binance_price_records,
    fetch_tej_price_records,
    fetch_twse_price_records,
    load_price_records,
)
from ..quant.reporting import write_backtest_json


def run_backtest_workflow(config: BacktestRunConfig):
    price_records = _load_price_records(config)
    result = run_backtest(
        price_records,
        lookback_periods=config.lookback_periods,
        volatility_window=config.volatility_window,
        top_n=config.top_n,
        periods_per_year=config.periods_per_year,
        benchmark_ticker=config.benchmark_ticker,
        momentum_weight=config.momentum_weight,
        volatility_weight=config.volatility_weight,
    )
    write_backtest_json(result, str(config.backtest_output))
    return result


def _load_price_records(config: BacktestRunConfig):
    if config.price_source == "csv":
        return load_price_records(config.prices_path)
    if config.price_source == "binance":
        if not config.binance_symbols:
            raise InputDataError("Binance source requires at least one symbol.")
        return fetch_binance_price_records(
            config.binance_symbols,
            interval=config.binance_interval,
            limit=config.binance_limit,
            base_url=config.binance_base_url,
            start_date=config.start_date,
            end_date=config.end_date,
            timeout=config.request_timeout,
        )
    if config.price_source == "twse":
        if not config.twse_stock_nos:
            raise InputDataError("TWSE source requires at least one stock number.")
        return fetch_twse_price_records(
            config.twse_stock_nos,
            base_url=config.twse_base_url,
            start_date=config.start_date,
            end_date=config.end_date,
            timeout=config.request_timeout,
        )
    if config.price_source == "tej":
        if not config.tej_symbols:
            raise InputDataError("TEJ source requires at least one symbol.")
        if not config.tej_api_key:
            raise InputDataError("TEJ source requires an API key.")
        return fetch_tej_price_records(
            config.tej_symbols,
            api_key=config.tej_api_key,
            table_code=config.tej_table_code,
            base_url=config.tej_base_url,
            start_date=config.start_date,
            end_date=config.end_date,
            timeout=config.request_timeout,
        )

    raise InputDataError(f"Unsupported price source: {config.price_source}")
