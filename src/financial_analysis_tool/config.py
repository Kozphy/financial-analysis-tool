from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_INPUT_PATH = Path("data/financials.csv")
DEFAULT_SUMMARY_OUTPUT = Path("output/reports/financial_summary.json")
DEFAULT_REPORT_OUTPUT = Path("output/reports/executive_summary.md")
DEFAULT_PROFITABILITY_CHART = Path("output/charts/profitability_trends.svg")
DEFAULT_FINANCIAL_POSITION_CHART = Path("output/charts/financial_position_trends.svg")
DEFAULT_COMPANY_NAME = "Harbor Industrial Group"


@dataclass(frozen=True, slots=True)
class AnalysisConfig:
    input_path: Path = DEFAULT_INPUT_PATH
    summary_output: Path = DEFAULT_SUMMARY_OUTPUT
    report_output: Path = DEFAULT_REPORT_OUTPUT
    profitability_chart_output: Path = DEFAULT_PROFITABILITY_CHART
    financial_position_chart_output: Path = DEFAULT_FINANCIAL_POSITION_CHART
    company_name: str = DEFAULT_COMPANY_NAME
