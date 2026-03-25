from __future__ import annotations

from datetime import date
from pathlib import Path

from .models import PriceRecord
from .sources.binance_source import BinancePriceSource
from .sources.csv_source import CSVPriceSource
from .sources.tej_source import TEJPriceSource
from .sources.twse_source import TWSEPriceSource


def load_price_records(csv_path: str | Path) -> list[PriceRecord]:
    return CSVPriceSource(csv_path).load_records()


def fetch_binance_price_records(
    symbols: list[str] | tuple[str, ...],
    *,
    interval: str = "1d",
    limit: int = 365,
    base_url: str,
    start_date: date | None = None,
    end_date: date | None = None,
    timeout: int = 15,
    retries: int = 2,
    retry_backoff_seconds: float = 0.5,
    cache_dir: Path | None = None,
    parallelism: int = 4,
) -> list[PriceRecord]:
    return BinancePriceSource(
        symbols=symbols,
        interval=interval,
        limit=limit,
        base_url=base_url,
        start_date=start_date,
        end_date=end_date,
        timeout=timeout,
        retries=retries,
        retry_backoff_seconds=retry_backoff_seconds,
        cache_dir=cache_dir,
        parallelism=parallelism,
    ).load_records()


def fetch_twse_price_records(
    stock_nos: list[str] | tuple[str, ...],
    *,
    base_url: str,
    start_date: date | None = None,
    end_date: date | None = None,
    timeout: int = 15,
    retries: int = 2,
    retry_backoff_seconds: float = 0.5,
    cache_dir: Path | None = None,
    parallelism: int = 4,
) -> list[PriceRecord]:
    return TWSEPriceSource(
        stock_nos=stock_nos,
        base_url=base_url,
        start_date=start_date,
        end_date=end_date,
        timeout=timeout,
        retries=retries,
        retry_backoff_seconds=retry_backoff_seconds,
        cache_dir=cache_dir,
        parallelism=parallelism,
    ).load_records()


def fetch_tej_price_records(
    symbols: list[str] | tuple[str, ...],
    *,
    api_key: str,
    table_code: str,
    base_url: str,
    start_date: date | None = None,
    end_date: date | None = None,
    timeout: int = 15,
    retries: int = 2,
    retry_backoff_seconds: float = 0.5,
    cache_dir: Path | None = None,
    parallelism: int = 4,
) -> list[PriceRecord]:
    return TEJPriceSource(
        symbols=symbols,
        api_key=api_key,
        table_code=table_code,
        base_url=base_url,
        start_date=start_date,
        end_date=end_date,
        timeout=timeout,
        retries=retries,
        retry_backoff_seconds=retry_backoff_seconds,
        cache_dir=cache_dir,
        parallelism=parallelism,
    ).load_records()
