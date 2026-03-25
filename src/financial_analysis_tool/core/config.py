from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path


DEFAULT_INPUT = Path("data/financials.csv")
DEFAULT_SUMMARY_OUTPUT = Path("output/financial/summary.json")
DEFAULT_CHART_OUTPUT = Path("output/charts/financial-trends.svg")
DEFAULT_PRICES_INPUT = Path("data/prices.csv")
DEFAULT_BACKTEST_OUTPUT = Path("output/backtests/backtest.json")
DEFAULT_MOPS_BASE_URL = "https://mops.twse.com.tw"
DEFAULT_TWSE_BASE_URL = "https://www.twse.com.tw"
DEFAULT_TEJ_BASE_URL = "https://api.tej.com.tw"
DEFAULT_BINANCE_BASE_URL = "https://api.binance.com"
DEFAULT_CACHE_DIR = Path(".cache/financial-analysis-tool")


@dataclass(frozen=True, slots=True)
class FinancialRunConfig:
    financial_source: str = "csv"
    input_path: Path = DEFAULT_INPUT
    summary_output: Path = DEFAULT_SUMMARY_OUTPUT
    chart_output: Path = DEFAULT_CHART_OUTPUT
    generate_chart: bool = True
    mops_company_id: str | None = None
    mops_market: str = "all"
    mops_start_year: int | None = None
    mops_end_year: int | None = None
    mops_seasons: tuple[int, ...] = (1, 2, 3, 4)
    mops_base_url: str = DEFAULT_MOPS_BASE_URL
    request_timeout: int = 15
    retry_attempts: int = 2
    retry_backoff_seconds: float = 0.5
    cache_dir: Path | None = None


@dataclass(frozen=True, slots=True)
class BacktestRunConfig:
    price_source: str = "csv"
    prices_path: Path = DEFAULT_PRICES_INPUT
    backtest_output: Path = DEFAULT_BACKTEST_OUTPUT
    momentum_lookback_days: int = 90
    volatility_lookback_days: int = 90
    rebalance_frequency: str = "monthly"
    benchmark_alignment: str = "strict"
    top_n: int = 2
    periods_per_year: int = 12
    benchmark_ticker: str | None = None
    momentum_weight: float = 0.8
    volatility_weight: float = 0.2
    binance_symbols: tuple[str, ...] = ()
    binance_interval: str = "1d"
    binance_limit: int = 365
    binance_base_url: str = DEFAULT_BINANCE_BASE_URL
    twse_stock_nos: tuple[str, ...] = ()
    twse_base_url: str = DEFAULT_TWSE_BASE_URL
    tej_symbols: tuple[str, ...] = ()
    tej_api_key: str | None = None
    tej_base_url: str = DEFAULT_TEJ_BASE_URL
    tej_table_code: str = "TWN/APRCD"
    start_date: date | None = None
    end_date: date | None = None
    request_timeout: int = 15
    retry_attempts: int = 2
    retry_backoff_seconds: float = 0.5
    cache_dir: Path | None = None
    parallelism: int = 4
