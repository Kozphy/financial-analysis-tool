from __future__ import annotations

import csv
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from financial_analysis_tool.core.exceptions import (
    BinanceAPIError,
    InputDataError,
    TEJAPIError,
    TWSEAPIError,
)
from financial_analysis_tool.core.utils import to_epoch_milliseconds

from .models import PriceRecord


PRICE_REQUIRED_FIELDS = {
    "date",
    "ticker",
    "close",
}
TEJ_PRICE_COLUMNS = ("coid", "mdate", "open_d", "high_d", "low_d", "close_d", "volume")


def load_price_records(csv_path: str | Path) -> list[PriceRecord]:
    path = Path(csv_path)
    if not path.exists():
        raise InputDataError(f"Price dataset not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = PRICE_REQUIRED_FIELDS - fieldnames
        if missing:
            missing_fields = ", ".join(sorted(missing))
            raise InputDataError(f"Missing required CSV columns: {missing_fields}")

        records: list[PriceRecord] = []
        seen_keys: set[tuple[date, str]] = set()
        for row_number, row in enumerate(reader, start=2):
            if _is_blank_row(row):
                continue

            record_date = _parse_date(row["date"], row_number, "date")
            ticker = (row["ticker"] or "").strip().upper()
            if ticker == "":
                raise InputDataError(f"Row {row_number} is missing a value for 'ticker'.")

            record_key = (record_date, ticker)
            if record_key in seen_keys:
                raise InputDataError(
                    f"Duplicate price record found for ticker '{ticker}' on {record_date.isoformat()}."
                )
            seen_keys.add(record_key)

            close = _parse_number(row["close"], row_number, "close")
            records.append(
                PriceRecord(
                    date=record_date,
                    ticker=ticker,
                    open=_parse_optional_number(row.get("open"), close),
                    high=_parse_optional_number(row.get("high"), close),
                    low=_parse_optional_number(row.get("low"), close),
                    close=close,
                    volume=_parse_optional_number(row.get("volume"), 0.0),
                )
            )

    if not records:
        raise InputDataError("Price dataset is empty.")

    return sorted(records, key=lambda record: (record.ticker, record.date))


def fetch_binance_price_records(
    symbols: list[str] | tuple[str, ...],
    *,
    interval: str = "1d",
    limit: int = 365,
    base_url: str,
    start_date: date | None = None,
    end_date: date | None = None,
    timeout: int = 15,
) -> list[PriceRecord]:
    normalized_symbols = [symbol.strip().upper() for symbol in symbols if symbol.strip()]
    if not normalized_symbols:
        raise InputDataError("At least one Binance symbol is required.")
    if limit <= 0 or limit > 1000:
        raise InputDataError("Binance kline limit must be between 1 and 1000.")

    records: list[PriceRecord] = []
    for symbol in normalized_symbols:
        records.extend(
            _fetch_binance_symbol_klines(
                symbol,
                interval=interval,
                limit=limit,
                base_url=base_url,
                start_date=start_date,
                end_date=end_date,
                timeout=timeout,
            )
        )

    return sorted(records, key=lambda record: (record.ticker, record.date))


def fetch_twse_price_records(
    stock_nos: list[str] | tuple[str, ...],
    *,
    base_url: str,
    start_date: date | None = None,
    end_date: date | None = None,
    timeout: int = 15,
) -> list[PriceRecord]:
    normalized_stock_nos = [stock_no.strip().upper() for stock_no in stock_nos if stock_no.strip()]
    if not normalized_stock_nos:
        raise InputDataError("TWSE source requires at least one stock number.")

    resolved_start_date, resolved_end_date = _resolve_remote_date_window(
        start_date=start_date,
        end_date=end_date,
    )
    records: list[PriceRecord] = []
    seen_keys: set[tuple[date, str]] = set()
    current_month = date(resolved_start_date.year, resolved_start_date.month, 1)
    last_month = date(resolved_end_date.year, resolved_end_date.month, 1)

    while current_month <= last_month:
        for stock_no in normalized_stock_nos:
            payload = _request_twse_month(
                stock_no=stock_no,
                query_month=current_month,
                base_url=base_url,
                timeout=timeout,
            )
            records.extend(
                _parse_twse_month_payload(
                    payload,
                    stock_no=stock_no,
                    start_date=resolved_start_date,
                    end_date=resolved_end_date,
                    seen_keys=seen_keys,
                )
            )
        current_month = _next_month(current_month)

    if not records:
        raise InputDataError("No TWSE price records were returned for the requested range.")

    return sorted(records, key=lambda record: (record.ticker, record.date))


def fetch_tej_price_records(
    symbols: list[str] | tuple[str, ...],
    *,
    api_key: str,
    table_code: str,
    base_url: str,
    start_date: date | None = None,
    end_date: date | None = None,
    timeout: int = 15,
) -> list[PriceRecord]:
    normalized_symbols = [symbol.strip().upper() for symbol in symbols if symbol.strip()]
    if not normalized_symbols:
        raise InputDataError("TEJ source requires at least one symbol.")
    if not api_key or api_key.strip() == "":
        raise InputDataError("TEJ source requires an API key.")

    resolved_start_date, resolved_end_date = _resolve_remote_date_window(
        start_date=start_date,
        end_date=end_date,
    )
    records: list[PriceRecord] = []
    seen_keys: set[tuple[date, str]] = set()
    cursor_id: str | None = None

    while True:
        payload = _request_tej_page(
            symbols=normalized_symbols,
            api_key=api_key,
            table_code=table_code,
            base_url=base_url,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            cursor_id=cursor_id,
            timeout=timeout,
        )
        page_records, cursor_id = _parse_tej_page(payload, seen_keys=seen_keys)
        records.extend(page_records)
        if cursor_id is None:
            break

    if not records:
        raise InputDataError("No TEJ price records were returned for the requested range.")

    return sorted(records, key=lambda record: (record.ticker, record.date))


def _fetch_binance_symbol_klines(
    symbol: str,
    *,
    interval: str,
    limit: int,
    base_url: str,
    start_date: date | None,
    end_date: date | None,
    timeout: int,
) -> list[PriceRecord]:
    params: dict[str, str | int] = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }
    if start_date:
        params["startTime"] = to_epoch_milliseconds(start_date)
    if end_date:
        params["endTime"] = to_epoch_milliseconds(end_date, end_of_day=True)

    request_url = f"{base_url.rstrip('/')}/api/v3/klines?{urlencode(params)}"
    payload = _request_json(
        request_url,
        timeout=timeout,
        error_cls=BinanceAPIError,
        source_label="Binance",
    )
    if not isinstance(payload, list):
        raise BinanceAPIError(f"Unexpected Binance kline response for {symbol}.")

    return [_parse_binance_kline(symbol, item) for item in payload]


def _request_twse_month(
    *,
    stock_no: str,
    query_month: date,
    base_url: str,
    timeout: int,
) -> object:
    request_url = (
        f"{base_url.rstrip('/')}/exchangeReport/STOCK_DAY?"
        f"{urlencode({'response': 'json', 'date': query_month.strftime('%Y%m01'), 'stockNo': stock_no})}"
    )
    return _request_json(
        request_url,
        timeout=timeout,
        error_cls=TWSEAPIError,
        source_label="TWSE",
    )


def _request_tej_page(
    *,
    symbols: list[str],
    api_key: str,
    table_code: str,
    base_url: str,
    start_date: date,
    end_date: date,
    cursor_id: str | None,
    timeout: int,
) -> object:
    params = {
        "api_key": api_key,
        "coid": ",".join(symbols),
        "mdate.gte": start_date.isoformat(),
        "mdate.lte": end_date.isoformat(),
        "opts.columns": ",".join(TEJ_PRICE_COLUMNS),
        "opts.per_page": "10000",
        "opts.sort": "mdate.asc",
    }
    if cursor_id is not None:
        params["opts.cursor_id"] = cursor_id

    request_url = f"{base_url.rstrip('/')}/api/datatables/{table_code}.json?{urlencode(params)}"
    return _request_json(
        request_url,
        timeout=timeout,
        error_cls=TEJAPIError,
        source_label="TEJ",
    )


def _request_json(
    url: str,
    *,
    timeout: int,
    error_cls: type[Exception],
    source_label: str,
) -> object:
    request = Request(url, headers={"User-Agent": "financial-analysis-tool/0.1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise error_cls(f"{source_label} request failed with HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise error_cls(f"Unable to reach {source_label}: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise error_cls(f"{source_label} returned invalid JSON.") from exc


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


def _parse_twse_month_payload(
    payload: object,
    *,
    stock_no: str,
    start_date: date,
    end_date: date,
    seen_keys: set[tuple[date, str]],
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

    index_map = {
        _normalize_field_name(field): index for index, field in enumerate(fields)
    }
    date_index = index_map.get("日期", 0)
    volume_index = index_map.get("成交股數", 1)
    open_index = index_map.get("開盤價", 3)
    high_index = index_map.get("最高價", 4)
    low_index = index_map.get("最低價", 5)
    close_index = index_map.get("收盤價", 6)

    records: list[PriceRecord] = []
    for row in rows:
        if not isinstance(row, list):
            continue

        record_date = _parse_twse_date(_get_row_value(row, date_index))
        if record_date is None or record_date < start_date or record_date > end_date:
            continue

        record_key = (record_date, stock_no)
        if record_key in seen_keys:
            continue

        open_price = _parse_market_number(_get_row_value(row, open_index))
        high_price = _parse_market_number(_get_row_value(row, high_index))
        low_price = _parse_market_number(_get_row_value(row, low_index))
        close_price = _parse_market_number(_get_row_value(row, close_index))
        volume = _parse_market_number(_get_row_value(row, volume_index))

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

    column_names = _extract_tej_column_names(raw_columns)
    index_map = {name: index for index, name in enumerate(column_names)}
    required_columns = {column: index_map.get(column) for column in TEJ_PRICE_COLUMNS}
    if any(index is None for index in required_columns.values()):
        raise TEJAPIError("TEJ response is missing one or more required price columns.")

    records: list[PriceRecord] = []
    for row in raw_rows:
        if not isinstance(row, list):
            continue

        ticker = str(_get_row_value(row, required_columns["coid"])).strip().upper()
        record_date = _parse_tej_date(_get_row_value(row, required_columns["mdate"]))
        if ticker == "" or record_date is None:
            continue

        record_key = (record_date, ticker)
        if record_key in seen_keys:
            continue

        open_price = _parse_market_number(_get_row_value(row, required_columns["open_d"]))
        high_price = _parse_market_number(_get_row_value(row, required_columns["high_d"]))
        low_price = _parse_market_number(_get_row_value(row, required_columns["low_d"]))
        close_price = _parse_market_number(_get_row_value(row, required_columns["close_d"]))
        volume = _parse_market_number(_get_row_value(row, required_columns["volume"]))
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


def _extract_tej_column_names(raw_columns: object) -> list[str]:
    if isinstance(raw_columns, list) and raw_columns:
        names = []
        for column in raw_columns:
            if isinstance(column, dict):
                names.append(str(column.get("name", "")))
            else:
                names.append(str(column))
        return names
    return list(TEJ_PRICE_COLUMNS)


def _resolve_remote_date_window(
    *,
    start_date: date | None,
    end_date: date | None,
) -> tuple[date, date]:
    today = date.today()
    resolved_end_date = end_date or today
    resolved_start_date = start_date or (resolved_end_date - timedelta(days=365))
    if resolved_start_date > resolved_end_date:
        raise InputDataError("Start date must be less than or equal to the end date.")
    return resolved_start_date, resolved_end_date


def _next_month(value: date) -> date:
    if value.month == 12:
        return date(value.year + 1, 1, 1)
    return date(value.year, value.month + 1, 1)


def _get_row_value(row: list[object], index: int | None) -> object:
    if index is None or index >= len(row):
        return ""
    return row[index]


def _normalize_field_name(value: str) -> str:
    return str(value).replace(" ", "").strip()


def _parse_twse_date(value: object) -> date | None:
    raw_value = str(value).strip()
    if raw_value == "":
        return None
    try:
        year_raw, month_raw, day_raw = raw_value.split("/")
        return date(int(year_raw) + 1911, int(month_raw), int(day_raw))
    except ValueError:
        return None


def _parse_tej_date(value: object) -> date | None:
    raw_value = str(value).strip()
    if raw_value == "":
        return None
    try:
        return date.fromisoformat(raw_value[:10])
    except ValueError:
        return None


def _is_blank_row(row: dict[str, str | None]) -> bool:
    return all((value or "").strip() == "" for value in row.values())


def _parse_number(value: str | None, row_number: int, field_name: str) -> float:
    raw_value = (value or "").strip().replace(",", "")
    if raw_value == "":
        raise InputDataError(f"Row {row_number} is missing a value for '{field_name}'.")

    try:
        return float(raw_value)
    except ValueError as exc:
        raise InputDataError(
            f"Row {row_number} has an invalid numeric value for '{field_name}': {value}"
        ) from exc


def _parse_optional_number(value: str | None, default: float) -> float:
    raw_value = (value or "").strip().replace(",", "")
    if raw_value == "":
        return default

    try:
        return float(raw_value)
    except ValueError as exc:
        raise InputDataError(f"Invalid optional numeric value: {value}") from exc


def _parse_market_number(value: object) -> float | None:
    raw_value = str(value).strip()
    if raw_value in {"", "--", "---", "----", "X", "除權息"}:
        return None

    normalized_value = raw_value.replace(",", "").replace("X", "").replace("+", "")
    normalized_value = normalized_value.strip()
    if normalized_value in {"", "-"}:
        return None

    try:
        return float(normalized_value)
    except ValueError:
        return None


def _parse_date(value: str | None, row_number: int, field_name: str) -> date:
    raw_value = (value or "").strip()
    if raw_value == "":
        raise InputDataError(f"Row {row_number} is missing a value for '{field_name}'.")

    try:
        return date.fromisoformat(raw_value)
    except ValueError as exc:
        raise InputDataError(
            f"Row {row_number} has an invalid date value for '{field_name}': {value}"
        ) from exc
