from __future__ import annotations

import logging

from financial_analysis_tool.core.config import FinancialRunConfig

from ..financial.metrics import analyze_records, summarize_company_performance
from ..financial.reporting import write_summary_json
from ..financial.sources import create_financial_source
from ..financial.visualization import generate_trend_chart


LOGGER = logging.getLogger(__name__)


def run_financial_workflow(config: FinancialRunConfig):
    summary, analyses = generate_financial_summary(config)
    persist_financial_outputs(summary, analyses, config)
    return summary


def generate_financial_summary(config: FinancialRunConfig):
    LOGGER.info("generate_financial_summary source=%s", config.financial_source)
    records = create_financial_source(config).load_records()
    analyses = analyze_records(records)
    summary = summarize_company_performance(analyses)
    return summary, analyses


def persist_financial_outputs(summary, analyses, config: FinancialRunConfig) -> None:
    write_summary_json(summary, str(config.summary_output))
    if config.generate_chart:
        generate_trend_chart(analyses, config.chart_output)
