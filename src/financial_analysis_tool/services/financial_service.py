from __future__ import annotations

from financial_analysis_tool.core.config import FinancialRunConfig

from ..financial.loader import load_financial_records
from ..financial.metrics import analyze_records, summarize_company_performance
from ..financial.reporting import write_summary_json
from ..financial.visualization import generate_trend_chart


def run_financial_workflow(config: FinancialRunConfig):
    records = load_financial_records(config.input_path)
    analyses = analyze_records(records)
    summary = summarize_company_performance(analyses)

    write_summary_json(summary, str(config.summary_output))
    if config.generate_chart:
        generate_trend_chart(analyses, config.chart_output)

    return summary
