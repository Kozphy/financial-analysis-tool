from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from urllib.parse import urlencode

from financial_analysis_tool.core.exceptions import InputDataError, TWSEAPIError
from financial_analysis_tool.core.http import request_json

from ..models import PriceRecord
from .helpers import parse_market_number, parse_twse_date, resolve_remote_date_window, sort_price_records


LOGGER = logging.getLogger(__name__)


class TWSEPriceSource:
    def __init__(
        self,
        *,
        stock_nos: tuple[str, ...] | list[str],
        base_url: str,
        start_date: date | None,
        end_date: date | None,
        timeout: int = 15,
        retries: int = 2,
        retry_backoff_seconds: float = 0.5,
        cache_dir: Path | None = None,
        parallelism: int = 4,
    ) -> None:
        self._stock_nos = tuple(stock_no.strip().upper() for stock_no in stock_nos if stock_no.strip())
        self._base_url = base_url
        self._start_date = start_date
        self._end_date = end_date
        self._timeout = timeout
        self._retries = retries
        self._retry_backoff_seconds = retry_backoff_seconds
        self._cache_dir = cache_dir
        self._parallelism = parallelism

    def load_records(self) -> list[PriceRecord]:
        if not self._stock_nos:
            raise InputDataError("TWSE source requires at least one stock number.")

        resolved_start_date, resolved_end_date = resolve_remote_date_window(
            start_date=self._start_date,
            end_date=self._end_date,
        )
        tasks = []
        current_month = date(resolved_start_date.year, resolved_start_date.month, 1)
        last_month = date(resolved_end_date.year, resolved_end_date.month, 1)
        while current_month <= last_month:
            for stock_no in self._stock_nos:
                tasks.append((stock_no, current_month))
            current_month = _next_month(current_month)

        with ThreadPoolExecutor(max_workers=max(1, min(self._parallelism, len(tasks)))) as executor:
            record_groups = list(
                executor.map(
                    lambda task: self._fetch_month(
                        stock_no=task[0],
                        query_month=task[1],
                        start_date=resolved_start_date,
                        end_date=resolved_end_date,
                    ),
                    tasks,
                )
            )

        records = [record for group in record_groups for record in group]
        if not records:
            raise InputDataError("No TWSE price records were returned for the requested range.")
        return sort_price_records(records)

    def _fetch_month(
        self,
        *,
        stock_no: str,
        query_month: date,
        start_date: date,
        end_date: date,
    ) -> list[PriceRecord]:
        request_url = (
            f"{self._base_url.rstrip('/')}/exchangeReport/STOCK_DAY?"
            f"{urlencode({'response': 'json', 'date': query_month.strftime('%Y%m01'), 'stockNo': stock_no})}"
        )
        LOGGER.info("fetch_twse stock_no=%s month=%s", stock_no, query_month.isoformat())
        payload = request_json(
            request_url,
            timeout=self._timeout,
            retries=self._retries,
            backoff_seconds=self._retry_backoff_seconds,
            cache_dir=self._cache_dir,
            cache_namespace="twse",
            error_cls=TWSEAPIError,
            source_label="TWSE",
        )
        return _parse_twse_month_payload(
            payload,
            stock_no=stock_no,
            start_date=start_date,
            end_date=end_date,
        )


def _parse_twse_month_payload(
    payload: object,
    *,
    stock_no: str,
    start_date: date,
    end_date: date,
) -> list[PriceRecord]:
    if not isinstance(payload, dict):
        raise TWSEAPIError(f"Unexpected TWSE payload for {stock_no}.")

    status = str(payload.get("stat", ""))
    if status and "OK" not in status.upper():
        return []

    fields = [str(field) for field in payload.get("fields", [])]
    rows = payload.get("data", [])
    if not isinstance(rows, list):
        raise TWSEAPIError(f"Unexpected TWSE row payload for {stock_no}.")

    index_map = {str(field).replace(" ", "").strip(): index for index, field in enumerate(fields)}
    date_index = index_map.get("日期", 0)
    volume_index = index_map.get("成交股數", 1)
    open_index = index_map.get("開盤價", 3)
    high_index = index_map.get("最高價", 4)
    low_index = index_map.get("最低價", 5)
    close_index = index_map.get("收盤價", 6)

    records: list[PriceRecord] = []
    seen_keys: set[tuple[date, str]] = set()
    for row in rows:
        if not isinstance(row, list):
            continue

        record_date = parse_twse_date(_get_row_value(row, date_index))
        if record_date is None or record_date < start_date or record_date > end_date:
            continue

        record_key = (record_date, stock_no)
        if record_key in seen_keys:
            continue

        open_price = parse_market_number(_get_row_value(row, open_index))
        high_price = parse_market_number(_get_row_value(row, high_index))
        low_price = parse_market_number(_get_row_value(row, low_index))
        close_price = parse_market_number(_get_row_value(row, close_index))
        volume = parse_market_number(_get_row_value(row, volume_index))
        if None in {open_price, high_price, low_price, close_price}:
            continue

        seen_keys.add(record_key)
        records.append(
            PriceRecord(
                date=record_date,
                ticker=stock_no,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=volume or 0.0,
            )
        )

    return records


def _get_row_value(row: list[object], index: int | None) -> object:
    if index is None or index >= len(row):
        return ""
    return row[index]


def _next_month(value: date) -> date:
    if value.month == 12:
        return date(value.year + 1, 1, 1)
    return date(value.year, value.month + 1, 1)
