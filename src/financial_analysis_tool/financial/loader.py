from __future__ import annotations

from pathlib import Path

from .models import FinancialRecord
from .sources.csv_source import CSVFinancialSource
from .sources.mops_source import MOPSFinancialSource


def load_financial_records(csv_path: str | Path) -> list[FinancialRecord]:
    return CSVFinancialSource(csv_path).load_records()


def fetch_mops_financial_records(
    company_id: str,
    *,
    start_year: int,
    end_year: int,
    seasons: tuple[int, ...] | list[int] = (1, 2, 3, 4),
    base_url: str,
    market: str = "all",
    timeout: int = 15,
    retries: int = 2,
    retry_backoff_seconds: float = 0.5,
    cache_dir: Path | None = None,
) -> list[FinancialRecord]:
    return MOPSFinancialSource(
        company_id=company_id,
        start_year=start_year,
        end_year=end_year,
        seasons=seasons,
        base_url=base_url,
        market=market,
        timeout=timeout,
        retries=retries,
        retry_backoff_seconds=retry_backoff_seconds,
        cache_dir=cache_dir,
    ).load_records()
