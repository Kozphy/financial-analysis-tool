from __future__ import annotations

import logging

from financial_analysis_tool.core.config import BacktestRunConfig

from ..quant.backtest import run_backtest
from ..quant.reporting import write_backtest_json
from ..quant.sources import create_price_source


LOGGER = logging.getLogger(__name__)


def run_backtest_workflow(config: BacktestRunConfig):
    result = generate_backtest_result(config)
    persist_backtest_output(result, config)
    return result


def generate_backtest_result(config: BacktestRunConfig):
    LOGGER.info(
        "generate_backtest_result source=%s rebalance_frequency=%s benchmark_alignment=%s",
        config.price_source,
        config.rebalance_frequency,
        config.benchmark_alignment,
    )
    price_records = create_price_source(config).load_records()
    return run_backtest(
        price_records,
        momentum_lookback_days=config.momentum_lookback_days,
        volatility_lookback_days=config.volatility_lookback_days,
        rebalance_frequency=config.rebalance_frequency,
        top_n=config.top_n,
        periods_per_year=config.periods_per_year,
        benchmark_ticker=config.benchmark_ticker,
        benchmark_alignment=config.benchmark_alignment,
        momentum_weight=config.momentum_weight,
        volatility_weight=config.volatility_weight,
    )


def persist_backtest_output(result, config: BacktestRunConfig) -> None:
    write_backtest_json(result, str(config.backtest_output))
