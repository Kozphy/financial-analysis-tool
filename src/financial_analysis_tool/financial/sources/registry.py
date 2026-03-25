from __future__ import annotations

from financial_analysis_tool.core.config import FinancialRunConfig
from financial_analysis_tool.core.exceptions import InputDataError

from .base import FinancialSource
from .csv_source import CSVFinancialSource
from .mops_source import MOPSFinancialSource


def create_financial_source(config: FinancialRunConfig) -> FinancialSource:
    if config.financial_source == "csv":
        return CSVFinancialSource(config.input_path)
    if config.financial_source == "mops":
        if not config.mops_company_id:
            raise InputDataError("MOPS source requires --mops-company-id.")
        if config.mops_start_year is None or config.mops_end_year is None:
            raise InputDataError("MOPS source requires --mops-start-year and --mops-end-year.")
        return MOPSFinancialSource(
            company_id=config.mops_company_id,
            start_year=config.mops_start_year,
            end_year=config.mops_end_year,
            seasons=config.mops_seasons,
            market=config.mops_market,
            base_url=config.mops_base_url,
            timeout=config.request_timeout,
            retries=config.retry_attempts,
            retry_backoff_seconds=config.retry_backoff_seconds,
            cache_dir=config.cache_dir,
        )

    raise InputDataError(f"Unsupported financial source: {config.financial_source}")
