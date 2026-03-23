from __future__ import annotations

import csv
from pathlib import Path

from financial_analysis_tool.core.exceptions import InputDataError

from .models import FinancialRecord


REQUIRED_FIELDS = {
    "period",
    "revenue",
    "cost_of_revenue",
    "operating_expenses",
    "net_income",
}


def load_financial_records(csv_path: str | Path) -> list[FinancialRecord]:
    path = Path(csv_path)
    if not path.exists():
        raise InputDataError(f"Financial dataset not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_FIELDS - fieldnames
        if missing:
            missing_fields = ", ".join(sorted(missing))
            raise InputDataError(f"Missing required CSV columns: {missing_fields}")

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
        raise InputDataError("Financial dataset is empty.")

    return records


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
