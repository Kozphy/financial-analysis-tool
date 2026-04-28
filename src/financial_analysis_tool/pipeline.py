"""Financial statement analysis pipeline orchestration.

Data flow:
    financial CSV -> loader validation -> metric calculation -> analysis
    summary -> optional JSON, Markdown, and SVG artifacts.

The module exposes both an in-memory analysis function for API/dashboard use
and a file-writing pipeline used by the CLI.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import AnalysisConfig
from .loader import load_financial_statements
from .metrics import build_analysis_summary, calculate_period_metrics
from .models import AnalysisSummary, FinancialStatementRecord, PeriodMetrics
from .reporting import write_markdown_report, write_summary_json
from .visualization import (
    generate_financial_position_chart,
    generate_profitability_chart,
)


@dataclass(frozen=True, slots=True)
class AnalysisArtifacts:
    """In-memory outputs from the financial analysis workflow.

    Attributes:
        records: Validated financial statement rows loaded from CSV.
        period_metrics: Derived profitability, liquidity, and leverage metrics.
        summary: Aggregated financial analysis summary for reporting surfaces.
    """

    records: list[FinancialStatementRecord]
    period_metrics: list[PeriodMetrics]
    summary: AnalysisSummary


def analyze_financial_statements(
    input_path: str | Path,
    *,
    company_name: str = "",
) -> AnalysisArtifacts:
    """Analyze a financial statement CSV without writing output files.

    Args:
        input_path: Path to the financial statement CSV.
        company_name: Company label used in summaries and charts.

    Returns:
        AnalysisArtifacts: Validated records, calculated period metrics, and
        the aggregated analysis summary.

    Raises:
        ValueError: If the CSV is missing, empty, malformed, or contains
        invalid financial data.
    """
    records = load_financial_statements(input_path)
    period_metrics = calculate_period_metrics(records)
    summary = build_analysis_summary(period_metrics, company_name=company_name)
    return AnalysisArtifacts(
        records=records, period_metrics=period_metrics, summary=summary
    )


def run_analysis_pipeline(config: AnalysisConfig) -> AnalysisSummary:
    """Run the full financial CSV-to-artifacts pipeline.

    Data flow:
        input CSV -> validation -> metric calculation -> summary -> JSON,
        Markdown, profitability chart, and financial-position chart outputs.

    Args:
        config: Input/output paths and company display name.

    Returns:
        AnalysisSummary: The summary written to disk and returned to callers.

    Raises:
        ValueError: If financial input validation or metric calculation fails.
    """
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
