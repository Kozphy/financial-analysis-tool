"""High-level workflow orchestration for the ESG analysis pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import EsgAnalysisConfig
from .esg_loader import load_and_clean_esg_dataset
from .esg_metrics import (
    build_correlation_matrix,
    build_esg_summary,
    build_risk_signal_frame,
    build_sector_summary,
)
from .esg_models import EsgAnalysisSummary
from .esg_reporting import write_esg_markdown_report, write_esg_summary_json
from .esg_visualization import (
    generate_esg_correlation_heatmap,
    generate_esg_risk_signal_chart,
    generate_esg_trend_chart,
)


@dataclass(frozen=True, slots=True)
class EsgAnalysisArtifacts:
    """Bundle the cleaned ESG data, helper frames, and summary outputs."""

    cleaned_frame: Any
    sector_trend_frame: Any
    correlation_matrix: Any
    risk_signal_frame: Any
    summary: EsgAnalysisSummary


def analyze_esg_dataset(
    input_path: str | Path,
    *,
    audience_name: str,
) -> EsgAnalysisArtifacts:
    """Run the in-memory ESG analysis workflow without writing output files."""
    cleaned_frame = load_and_clean_esg_dataset(input_path)
    sector_trend_frame = (
        cleaned_frame.groupby(["year", "sector"], as_index=False)
        .agg(
            average_carbon_intensity=("carbon_intensity", "mean"),
            average_esg_score=("esg_score", "mean"),
        )
        .round(2)
    )
    correlation_matrix = build_correlation_matrix(cleaned_frame)
    risk_signal_frame = build_risk_signal_frame(cleaned_frame)
    sector_summary = build_sector_summary(cleaned_frame)
    summary = build_esg_summary(
        cleaned_frame,
        sector_summary,
        correlation_matrix,
        risk_signal_frame,
        audience_name=audience_name,
    )
    return EsgAnalysisArtifacts(
        cleaned_frame=cleaned_frame,
        sector_trend_frame=sector_trend_frame,
        correlation_matrix=correlation_matrix,
        risk_signal_frame=risk_signal_frame,
        summary=summary,
    )


def run_esg_analysis_pipeline(config: EsgAnalysisConfig) -> EsgAnalysisSummary:
    """Run the full ESG pipeline and write reports and chart artifacts to disk."""
    artifacts = analyze_esg_dataset(
        config.input_path,
        audience_name=config.audience_name,
    )
    write_esg_summary_json(artifacts.summary, config.summary_output)
    write_esg_markdown_report(artifacts.summary, config.report_output)
    generate_esg_trend_chart(artifacts.sector_trend_frame, config.trend_chart_output)
    generate_esg_correlation_heatmap(artifacts.correlation_matrix, config.correlation_chart_output)
    generate_esg_risk_signal_chart(artifacts.risk_signal_frame, config.risk_chart_output)
    return artifacts.summary
