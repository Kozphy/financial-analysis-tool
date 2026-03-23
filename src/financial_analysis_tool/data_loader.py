from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from .models import FinancialRecord, PriceRecord


REQUIRED_FIELDS = {
    "period",
    "revenue",
    "cost_of_revenue",
    "operating_expenses",
    "net_income",
}

PRICE_REQUIRED_FIELDS = {
    "date",
    "ticker",
    "close",
}


def load_financial_records(csv_path: str | Path) -> list[FinancialRecord]:
    path = Path(csv_path)
    if not path.exists():
        raise ValueError(f"Financial dataset not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_FIELDS - fieldnames
        if missing:
            missing_fields = ", ".join(sorted(missing))
            raise ValueError(f"Missing required CSV columns: {missing_fields}")

        records: list[FinancialRecord] = []
        for row_number, row in enumerate(reader, start=2):
            if _is_blank_row(row):
                continue

            records.append(
                FinancialRecord(
                    period=(row["period"] or "").strip(),
                    revenue=_parse_number(row["revenue"], row_number, "revenue"),
                    cost_of_revenue=_parse_number(
                        row["cost_of_revenue"], row_number, "cost_of_revenue"
                    ),
                    operating_expenses=_parse_number(
                        row["operating_expenses"], row_number, "operating_expenses"
                    ),
                    net_income=_parse_number(row["net_income"], row_number, "net_income"),
                )
            )

    if not records:
        raise ValueError("Financial dataset is empty.")

    return records


def load_price_records(csv_path: str | Path) -> list[PriceRecord]:
    path = Path(csv_path)
    if not path.exists():
        raise ValueError(f"Price dataset not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = PRICE_REQUIRED_FIELDS - fieldnames
        if missing:
            missing_fields = ", ".join(sorted(missing))
            raise ValueError(f"Missing required CSV columns: {missing_fields}")

        records: list[PriceRecord] = []
        seen_keys: set[tuple[date, str]] = set()
        for row_number, row in enumerate(reader, start=2):
            if _is_blank_row(row):
                continue

            record_date = _parse_date(row["date"], row_number, "date")
            ticker = (row["ticker"] or "").strip().upper()
            if ticker == "":
                raise ValueError(f"Row {row_number} is missing a value for 'ticker'.")

            record_key = (record_date, ticker)
            if record_key in seen_keys:
                raise ValueError(
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
        raise ValueError("Price dataset is empty.")

    return sorted(records, key=lambda record: (record.ticker, record.date))


def _is_blank_row(row: dict[str, str | None]) -> bool:
    return all((value or "").strip() == "" for value in row.values())


def _parse_number(value: str | None, row_number: int, field_name: str) -> float:
    raw_value = (value or "").strip().replace(",", "")
    if raw_value == "":
        raise ValueError(f"Row {row_number} is missing a value for '{field_name}'.")

    try:
        return float(raw_value)
    except ValueError as exc:
        raise ValueError(
            f"Row {row_number} has an invalid numeric value for '{field_name}': {value}"
        ) from exc


def _parse_optional_number(value: str | None, default: float) -> float:
    raw_value = (value or "").strip().replace(",", "")
    if raw_value == "":
        return default

    try:
        return float(raw_value)
    except ValueError as exc:
        raise ValueError(f"Invalid optional numeric value: {value}") from exc


def _parse_date(value: str | None, row_number: int, field_name: str) -> date:
    raw_value = (value or "").strip()
    if raw_value == "":
        raise ValueError(f"Row {row_number} is missing a value for '{field_name}'.")

    try:
        return date.fromisoformat(raw_value)
    except ValueError as exc:
        raise ValueError(
            f"Row {row_number} has an invalid date value for '{field_name}': {value}"
        ) from exc
