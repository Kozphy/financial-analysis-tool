from __future__ import annotations

from financial_analysis_tool.core.config import FinancialRunConfig
from financial_analysis_tool.core.exceptions import InputDataError

from ..financial.loader import fetch_mops_financial_records, load_financial_records
from ..financial.metrics import analyze_records, summarize_company_performance
from ..financial.reporting import write_summary_json
from ..financial.visualization import generate_trend_chart


def run_financial_workflow(config: FinancialRunConfig):
    records = _load_financial_records(config)
    analyses = analyze_records(records)
    summary = summarize_company_performance(analyses)

    write_summary_json(summary, str(config.summary_output))
    if config.generate_chart:
        generate_trend_chart(analyses, config.chart_output)

    return summary


def _load_financial_records(config: FinancialRunConfig):
    if config.financial_source == "csv":
        return load_financial_records(config.input_path)
    if config.financial_source == "mops":
        if not config.mops_company_id:
            raise InputDataError("MOPS source requires --mops-company-id.")
        if config.mops_start_year is None or config.mops_end_year is None:
            raise InputDataError("MOPS source requires --mops-start-year and --mops-end-year.")
        return fetch_mops_financial_records(
            config.mops_company_id,
            start_year=config.mops_start_year,
            end_year=config.mops_end_year,
            seasons=config.mops_seasons,
            market=config.mops_market,
            base_url=config.mops_base_url,
            timeout=config.request_timeout,
        )

    raise InputDataError(f"Unsupported financial source: {config.financial_source}")
