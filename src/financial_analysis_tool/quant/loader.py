from __future__ import annotations

import csv
import json
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from financial_analysis_tool.core.exceptions import BinanceAPIError, InputDataError
from financial_analysis_tool.core.utils import to_epoch_milliseconds

from .models import PriceRecord


PRICE_REQUIRED_FIELDS = {
    "date",
    "ticker",
    "close",
}


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
    payload = _request_binance_json(request_url, timeout=timeout)
    if not isinstance(payload, list):
        raise BinanceAPIError(f"Unexpected Binance kline response for {symbol}.")

    return [_parse_binance_kline(symbol, item) for item in payload]


def _request_binance_json(url: str, *, timeout: int) -> object:
    request = Request(url, headers={"User-Agent": "financial-analysis-tool/0.1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise BinanceAPIError(f"Binance request failed with HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise BinanceAPIError(f"Unable to reach Binance: {exc.reason}") from exc

    if isinstance(payload, dict) and "code" in payload and "msg" in payload:
        raise BinanceAPIError(f"Binance error {payload['code']}: {payload['msg']}")

    return payload


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
