"""Default file paths and configuration objects for local analysis workflows.

The API, CLI, and Streamlit dashboard all use these defaults to keep the sample
financial and ESG pipelines runnable from a local checkout without extra
environment configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_INPUT_PATH = Path("data/financials.csv")
DEFAULT_SUMMARY_OUTPUT = Path("output/reports/financial_summary.json")
DEFAULT_REPORT_OUTPUT = Path("output/reports/executive_summary.md")
DEFAULT_PROFITABILITY_CHART = Path("output/charts/profitability_trends.svg")
DEFAULT_FINANCIAL_POSITION_CHART = Path("output/charts/financial_position_trends.svg")
DEFAULT_COMPANY_NAME = "Harbor Industrial Group"
DEFAULT_ESG_INPUT_PATH = Path("data/esg_metrics.csv")
DEFAULT_ESG_SUMMARY_OUTPUT = Path("output/reports/esg_summary.json")
DEFAULT_ESG_REPORT_OUTPUT = Path("output/reports/esg_business_insights.md")
DEFAULT_ESG_CLEANED_DATA_OUTPUT = Path("output/data/esg_cleaned_dataset.csv")
DEFAULT_ESG_TREND_CHART = Path("output/charts/esg_carbon_trend.png")
DEFAULT_ESG_CORRELATION_CHART = Path("output/charts/esg_correlation_heatmap.png")
DEFAULT_ESG_RISK_CHART = Path("output/charts/esg_risk_signal.png")
DEFAULT_ESG_AUDIENCE = "Cathay Financial Holdings"


@dataclass(frozen=True, slots=True)
class AnalysisConfig:
    """Configuration for the financial statement analysis pipeline.

    Attributes:
        input_path: Source CSV path containing financial statement rows.
        summary_output: JSON summary artifact path.
        report_output: Markdown report artifact path.
        profitability_chart_output: SVG profitability chart path.
        financial_position_chart_output: SVG liquidity/leverage chart path.
        company_name: Company label used in reports and chart titles.
    """

    input_path: Path = DEFAULT_INPUT_PATH
    summary_output: Path = DEFAULT_SUMMARY_OUTPUT
    report_output: Path = DEFAULT_REPORT_OUTPUT
    profitability_chart_output: Path = DEFAULT_PROFITABILITY_CHART
    financial_position_chart_output: Path = DEFAULT_FINANCIAL_POSITION_CHART
    company_name: str = DEFAULT_COMPANY_NAME


@dataclass(frozen=True, slots=True)
class EsgAnalysisConfig:
    """Configuration for the ESG analysis workflow."""

    input_path: Path = DEFAULT_ESG_INPUT_PATH
    summary_output: Path = DEFAULT_ESG_SUMMARY_OUTPUT
    report_output: Path = DEFAULT_ESG_REPORT_OUTPUT
    cleaned_data_output: Path = DEFAULT_ESG_CLEANED_DATA_OUTPUT
    trend_chart_output: Path = DEFAULT_ESG_TREND_CHART
    correlation_chart_output: Path = DEFAULT_ESG_CORRELATION_CHART
    risk_chart_output: Path = DEFAULT_ESG_RISK_CHART
    audience_name: str = DEFAULT_ESG_AUDIENCE
