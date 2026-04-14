"""High-level workflow orchestration for the financial analysis pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import AnalysisConfig
from .loader import load_financial_statements
from .metrics import build_analysis_summary, calculate_period_metrics
from .models import AnalysisSummary, FinancialStatementRecord, PeriodMetrics
from .reporting import write_markdown_report, write_summary_json
from .visualization import generate_financial_position_chart, generate_profitability_chart


@dataclass(frozen=True, slots=True)
class AnalysisArtifacts:
    """Bundle raw records, calculated metrics, and summary output for reuse across interfaces."""

    records: list[FinancialStatementRecord]
    period_metrics: list[PeriodMetrics]
    summary: AnalysisSummary


def analyze_financial_statements(
    input_path: str | Path,
    *,
    company_name: str,
) -> AnalysisArtifacts:
    """Run the in-memory analysis workflow without writing output files."""
    records = load_financial_statements(input_path)
    period_metrics = calculate_period_metrics(records)
    summary = build_analysis_summary(period_metrics, company_name=company_name)
    return AnalysisArtifacts(records=records, period_metrics=period_metrics, summary=summary)


def run_analysis_pipeline(config: AnalysisConfig) -> AnalysisSummary:
    """Run the full pipeline and write summary reports and chart artifacts to disk."""
    artifacts = analyze_financial_statements(
        config.input_path,
        company_name=config.company_name,
    )

    write_summary_json(artifacts.summary, config.summary_output)
    write_markdown_report(artifacts.summary, config.report_output)
    generate_profitability_chart(
        artifacts.period_metrics,
        config.profitability_chart_output,
        company_name=config.company_name,
    )
    generate_financial_position_chart(
        artifacts.period_metrics,
        config.financial_position_chart_output,
        company_name=config.company_name,
    )
    return artifacts.summary
