from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path


DEFAULT_INPUT = Path("data/financials.csv")
DEFAULT_SUMMARY_OUTPUT = Path("output/summary.json")
DEFAULT_CHART_OUTPUT = Path("output/charts.svg")
DEFAULT_PRICES_INPUT = Path("data/prices.csv")
DEFAULT_BACKTEST_OUTPUT = Path("output/backtest.json")
DEFAULT_BINANCE_BASE_URL = "https://api.binance.com"


@dataclass(frozen=True, slots=True)
class FinancialRunConfig:
    input_path: Path = DEFAULT_INPUT
    summary_output: Path = DEFAULT_SUMMARY_OUTPUT
    chart_output: Path = DEFAULT_CHART_OUTPUT
    generate_chart: bool = True


@dataclass(frozen=True, slots=True)
class BacktestRunConfig:
    price_source: str = "csv"
    prices_path: Path = DEFAULT_PRICES_INPUT
    backtest_output: Path = DEFAULT_BACKTEST_OUTPUT
    lookback_periods: int = 3
    volatility_window: int = 3
    top_n: int = 2
    periods_per_year: int = 12
    benchmark_ticker: str | None = None
    momentum_weight: float = 0.8
    volatility_weight: float = 0.2
    binance_symbols: tuple[str, ...] = ()
    binance_interval: str = "1d"
    binance_limit: int = 365
    binance_base_url: str = DEFAULT_BINANCE_BASE_URL
    start_date: date | None = None
    end_date: date | None = None
