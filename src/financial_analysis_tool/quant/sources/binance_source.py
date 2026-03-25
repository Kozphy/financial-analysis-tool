from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from financial_analysis_tool.core.exceptions import BinanceAPIError, InputDataError
from financial_analysis_tool.core.http import request_json
from financial_analysis_tool.core.utils import to_epoch_milliseconds

from ..models import PriceRecord
from .helpers import sort_price_records


LOGGER = logging.getLogger(__name__)


class BinancePriceSource:
    def __init__(
        self,
        *,
        symbols: tuple[str, ...] | list[str],
        interval: str,
        limit: int,
        base_url: str,
        start_date: date | None,
        end_date: date | None,
        timeout: int = 15,
        retries: int = 2,
        retry_backoff_seconds: float = 0.5,
        cache_dir: Path | None = None,
        parallelism: int = 4,
    ) -> None:
        self._symbols = tuple(symbol.strip().upper() for symbol in symbols if symbol.strip())
        self._interval = interval
        self._limit = limit
        self._base_url = base_url
        self._start_date = start_date
        self._end_date = end_date
        self._timeout = timeout
        self._retries = retries
        self._retry_backoff_seconds = retry_backoff_seconds
        self._cache_dir = cache_dir
        self._parallelism = parallelism

    def load_records(self) -> list[PriceRecord]:
        if not self._symbols:
            raise InputDataError("At least one Binance symbol is required.")
        if self._limit <= 0 or self._limit > 1000:
            raise InputDataError("Binance kline limit must be between 1 and 1000.")

        with ThreadPoolExecutor(max_workers=max(1, min(self._parallelism, len(self._symbols)))) as executor:
            record_groups = list(executor.map(self._fetch_symbol_klines, self._symbols))

        records = [record for group in record_groups for record in group]
        return sort_price_records(records)

    def _fetch_symbol_klines(self, symbol: str) -> list[PriceRecord]:
        params: dict[str, str | int] = {
            "symbol": symbol,
            "interval": self._interval,
            "limit": self._limit,
        }
        if self._start_date:
            params["startTime"] = to_epoch_milliseconds(self._start_date)
        if self._end_date:
            params["endTime"] = to_epoch_milliseconds(self._end_date, end_of_day=True)

        request_url = f"{self._base_url.rstrip('/')}/api/v3/klines?{urlencode(params)}"
        LOGGER.info("fetch_binance symbol=%s interval=%s", symbol, self._interval)
        payload = request_json(
            request_url,
            timeout=self._timeout,
            retries=self._retries,
            backoff_seconds=self._retry_backoff_seconds,
            cache_dir=self._cache_dir,
            cache_namespace="binance",
            error_cls=BinanceAPIError,
            source_label="Binance",
        )
        if not isinstance(payload, list):
            raise BinanceAPIError(f"Unexpected Binance kline response for {symbol}.")
        return [_parse_binance_kline(symbol, item) for item in payload]


def _parse_binance_kline(symbol: str, raw_kline: list[object]) -> PriceRecord:
    if not isinstance(raw_kline, list) or len(raw_kline) < 6:
        raise BinanceAPIError(f"Unexpected Binance kline payload for {symbol}: {raw_kline}")

    open_time = int(raw_kline[0])
    record_date = datetime.fromtimestamp(open_time / 1000, tz=timezone.utc).date()
    return PriceRecord(
        date=record_date,
        ticker=symbol,
        open=float(raw_kline[1]),
        high=float(raw_kline[2]),
        low=float(raw_kline[3]),
        close=float(raw_kline[4]),
        volume=float(raw_kline[5]),
    )
