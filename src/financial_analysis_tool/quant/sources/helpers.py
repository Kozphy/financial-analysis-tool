from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

from financial_analysis_tool.core.exceptions import InputDataError

from ..models import PriceRecord


PRICE_REQUIRED_FIELDS = {
    "date",
    "ticker",
    "close",
}


def load_csv_price_records(csv_path: str | Path) -> list[PriceRecord]:
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
            if is_blank_row(row):
                continue

            record_date = parse_iso_date(row["date"], row_number, "date")
            ticker = (row["ticker"] or "").strip().upper()
            if ticker == "":
                raise InputDataError(f"Row {row_number} is missing a value for 'ticker'.")

            record_key = (record_date, ticker)
            if record_key in seen_keys:
                raise InputDataError(
                    f"Duplicate price record found for ticker '{ticker}' on {record_date.isoformat()}."
                )
            seen_keys.add(record_key)

            close = parse_required_number(row["close"], row_number, "close")
            records.append(
                PriceRecord(
                    date=record_date,
                    ticker=ticker,
                    open=parse_optional_number(row.get("open"), close),
                    high=parse_optional_number(row.get("high"), close),
                    low=parse_optional_number(row.get("low"), close),
                    close=close,
                    volume=parse_optional_number(row.get("volume"), 0.0),
                )
            )

    if not records:
        raise InputDataError("Price dataset is empty.")

    return sort_price_records(records)


def sort_price_records(records: list[PriceRecord]) -> list[PriceRecord]:
    return sorted(records, key=lambda record: (record.ticker, record.date))


def resolve_remote_date_window(
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


def parse_iso_date(value: str | None, row_number: int, field_name: str) -> date:
    raw_value = (value or "").strip()
    if raw_value == "":
        raise InputDataError(f"Row {row_number} is missing a value for '{field_name}'.")

    try:
        return date.fromisoformat(raw_value)
    except ValueError as exc:
        raise InputDataError(
            f"Row {row_number} has an invalid date value for '{field_name}': {value}"
        ) from exc


def parse_required_number(value: str | None, row_number: int, field_name: str) -> float:
    raw_value = (value or "").strip().replace(",", "")
    if raw_value == "":
        raise InputDataError(f"Row {row_number} is missing a value for '{field_name}'.")

    try:
        return float(raw_value)
    except ValueError as exc:
        raise InputDataError(
            f"Row {row_number} has an invalid numeric value for '{field_name}': {value}"
        ) from exc


def parse_optional_number(value: str | None, default: float) -> float:
    raw_value = (value or "").strip().replace(",", "")
    if raw_value == "":
        return default

    try:
        return float(raw_value)
    except ValueError as exc:
        raise InputDataError(f"Invalid optional numeric value: {value}") from exc


def parse_market_number(value: object) -> float | None:
    raw_value = str(value).strip()
    if raw_value in {"", "--", "---", "----", "X", "除權息"}:
        return None

    normalized_value = raw_value.replace(",", "").replace("X", "").replace("+", "").strip()
    if normalized_value in {"", "-"}:
        return None

    try:
        return float(normalized_value)
    except ValueError:
        return None


def parse_twse_date(value: object) -> date | None:
    raw_value = str(value).strip()
    if raw_value == "":
        return None
    try:
        year_raw, month_raw, day_raw = raw_value.split("/")
        return date(int(year_raw) + 1911, int(month_raw), int(day_raw))
    except ValueError:
        return None


def parse_tej_date(value: object) -> date | None:
    raw_value = str(value).strip()
    if raw_value == "":
        return None
    try:
        return date.fromisoformat(raw_value[:10])
    except ValueError:
        return None


def is_blank_row(row: dict[str, str | None]) -> bool:
    return all((value or "").strip() == "" for value in row.values())
