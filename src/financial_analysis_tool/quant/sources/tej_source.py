from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from urllib.parse import urlencode

from financial_analysis_tool.core.exceptions import InputDataError, TEJAPIError
from financial_analysis_tool.core.http import request_json

from ..models import PriceRecord
from .helpers import parse_market_number, parse_tej_date, resolve_remote_date_window, sort_price_records


LOGGER = logging.getLogger(__name__)
TEJ_PRICE_COLUMNS = ("coid", "mdate", "open_d", "high_d", "low_d", "close_d", "volume")


class TEJPriceSource:
    def __init__(
        self,
        *,
        symbols: tuple[str, ...] | list[str],
        api_key: str,
        table_code: str,
        base_url: str,
        start_date: date | None,
        end_date: date | None,
        timeout: int = 15,
        retries: int = 2,
        retry_backoff_seconds: float = 0.5,
        cache_dir: Path | None = None,
        parallelism: int = 4,
        batch_size: int = 25,
    ) -> None:
        self._symbols = tuple(symbol.strip().upper() for symbol in symbols if symbol.strip())
        self._api_key = api_key
        self._table_code = table_code
        self._base_url = base_url
        self._start_date = start_date
        self._end_date = end_date
        self._timeout = timeout
        self._retries = retries
        self._retry_backoff_seconds = retry_backoff_seconds
        self._cache_dir = cache_dir
        self._parallelism = parallelism
        self._batch_size = max(batch_size, 1)

    def load_records(self) -> list[PriceRecord]:
        if not self._symbols:
            raise InputDataError("TEJ source requires at least one symbol.")
        if not self._api_key or self._api_key.strip() == "":
            raise InputDataError("TEJ source requires an API key.")

        resolved_start_date, resolved_end_date = resolve_remote_date_window(
            start_date=self._start_date,
            end_date=self._end_date,
        )
        batches = [
            self._symbols[index : index + self._batch_size]
            for index in range(0, len(self._symbols), self._batch_size)
        ]
        with ThreadPoolExecutor(max_workers=max(1, min(self._parallelism, len(batches)))) as executor:
            record_groups = list(
                executor.map(
                    lambda batch: self._fetch_batch(
                        symbols=batch,
                        start_date=resolved_start_date,
                        end_date=resolved_end_date,
                    ),
                    batches,
                )
            )

        records = [record for group in record_groups for record in group]
        if not records:
            raise InputDataError("No TEJ price records were returned for the requested range.")
        return sort_price_records(records)

    def _fetch_batch(
        self,
        *,
        symbols: tuple[str, ...],
        start_date: date,
        end_date: date,
    ) -> list[PriceRecord]:
        records: list[PriceRecord] = []
        seen_keys: set[tuple[date, str]] = set()
        cursor_id: str | None = None

        while True:
            payload = self._request_page(
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                cursor_id=cursor_id,
            )
            page_records, cursor_id = _parse_tej_page(payload, seen_keys=seen_keys)
            records.extend(page_records)
            if cursor_id is None:
                break

        return records

    def _request_page(
        self,
        *,
        symbols: tuple[str, ...],
        start_date: date,
        end_date: date,
        cursor_id: str | None,
    ) -> object:
        params = {
            "api_key": self._api_key,
            "coid": ",".join(symbols),
            "mdate.gte": start_date.isoformat(),
            "mdate.lte": end_date.isoformat(),
            "opts.columns": ",".join(TEJ_PRICE_COLUMNS),
            "opts.per_page": "10000",
            "opts.sort": "mdate.asc",
        }
        if cursor_id is not None:
            params["opts.cursor_id"] = cursor_id

        request_url = f"{self._base_url.rstrip('/')}/api/datatables/{self._table_code}.json?{urlencode(params)}"
        LOGGER.info("fetch_tej symbols=%s table=%s", ",".join(symbols), self._table_code)
        return request_json(
            request_url,
            timeout=self._timeout,
            retries=self._retries,
            backoff_seconds=self._retry_backoff_seconds,
            cache_dir=self._cache_dir,
            cache_namespace="tej",
            error_cls=TEJAPIError,
            source_label="TEJ",
        )


def _parse_tej_page(
    payload: object,
    *,
    seen_keys: set[tuple[date, str]],
) -> tuple[list[PriceRecord], str | None]:
    if not isinstance(payload, dict):
        raise TEJAPIError("Unexpected TEJ response payload.")
    if "error" in payload:
        raise TEJAPIError(f"TEJ error response: {payload['error']}")

    datatable = payload.get("datatable")
    if not isinstance(datatable, dict):
        raise TEJAPIError("TEJ response is missing the datatable payload.")

    raw_columns = datatable.get("columns", [])
    raw_rows = datatable.get("data", [])
    if not isinstance(raw_rows, list):
        raise TEJAPIError("TEJ response data payload is malformed.")

    column_names = _extract_column_names(raw_columns)
    index_map = {name: index for index, name in enumerate(column_names)}
    required_columns = {column: index_map.get(column) for column in TEJ_PRICE_COLUMNS}
    if any(index is None for index in required_columns.values()):
        raise TEJAPIError("TEJ response is missing one or more required price columns.")

    records: list[PriceRecord] = []
    for row in raw_rows:
        if not isinstance(row, list):
            continue

        ticker = str(_get_row_value(row, required_columns["coid"])).strip().upper()
        record_date = parse_tej_date(_get_row_value(row, required_columns["mdate"]))
        if ticker == "" or record_date is None:
            continue

        record_key = (record_date, ticker)
        if record_key in seen_keys:
            continue

        open_price = parse_market_number(_get_row_value(row, required_columns["open_d"]))
        high_price = parse_market_number(_get_row_value(row, required_columns["high_d"]))
        low_price = parse_market_number(_get_row_value(row, required_columns["low_d"]))
        close_price = parse_market_number(_get_row_value(row, required_columns["close_d"]))
        volume = parse_market_number(_get_row_value(row, required_columns["volume"]))
        if None in {open_price, high_price, low_price, close_price}:
            continue

        seen_keys.add(record_key)
        records.append(
            PriceRecord(
                date=record_date,
                ticker=ticker,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=volume or 0.0,
            )
        )

    meta = payload.get("meta", {})
    next_cursor_id = meta.get("next_cursor_id") if isinstance(meta, dict) else None
    return records, str(next_cursor_id) if next_cursor_id else None


def _extract_column_names(raw_columns: object) -> list[str]:
    if isinstance(raw_columns, list) and raw_columns:
        names = []
        for column in raw_columns:
            if isinstance(column, dict):
                names.append(str(column.get("name", "")))
            else:
                names.append(str(column))
        return names
    return list(TEJ_PRICE_COLUMNS)


def _get_row_value(row: list[object], index: int | None) -> object:
    if index is None or index >= len(row):
        return ""
    return row[index]
