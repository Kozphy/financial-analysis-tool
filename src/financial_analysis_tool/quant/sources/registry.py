from __future__ import annotations

from financial_analysis_tool.core.config import BacktestRunConfig
from financial_analysis_tool.core.exceptions import InputDataError

from .base import PriceSource
from .binance_source import BinancePriceSource
from .csv_source import CSVPriceSource
from .tej_source import TEJPriceSource
from .twse_source import TWSEPriceSource


def create_price_source(config: BacktestRunConfig) -> PriceSource:
    if config.price_source == "csv":
        return CSVPriceSource(config.prices_path)
    if config.price_source == "binance":
        return BinancePriceSource(
            symbols=config.binance_symbols,
            interval=config.binance_interval,
            limit=config.binance_limit,
            base_url=config.binance_base_url,
            start_date=config.start_date,
            end_date=config.end_date,
            timeout=config.request_timeout,
            retries=config.retry_attempts,
            retry_backoff_seconds=config.retry_backoff_seconds,
            cache_dir=config.cache_dir,
            parallelism=config.parallelism,
        )
    if config.price_source == "twse":
        return TWSEPriceSource(
            stock_nos=config.twse_stock_nos,
            base_url=config.twse_base_url,
            start_date=config.start_date,
            end_date=config.end_date,
            timeout=config.request_timeout,
            retries=config.retry_attempts,
            retry_backoff_seconds=config.retry_backoff_seconds,
            cache_dir=config.cache_dir,
            parallelism=config.parallelism,
        )
    if config.price_source == "tej":
        if not config.tej_api_key:
            raise InputDataError("TEJ source requires an API key.")
        return TEJPriceSource(
            symbols=config.tej_symbols,
            api_key=config.tej_api_key,
            table_code=config.tej_table_code,
            base_url=config.tej_base_url,
            start_date=config.start_date,
            end_date=config.end_date,
            timeout=config.request_timeout,
            retries=config.retry_attempts,
            retry_backoff_seconds=config.retry_backoff_seconds,
            cache_dir=config.cache_dir,
            parallelism=config.parallelism,
        )

    raise InputDataError(f"Unsupported price source: {config.price_source}")
