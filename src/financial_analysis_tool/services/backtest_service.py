from __future__ import annotations

from financial_analysis_tool.core.config import BacktestRunConfig
from financial_analysis_tool.core.exceptions import InputDataError

from ..quant.backtest import run_backtest
from ..quant.loader import fetch_binance_price_records, load_price_records
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
        )

    raise InputDataError(f"Unsupported price source: {config.price_source}")
