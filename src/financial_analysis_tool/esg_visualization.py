"""Matplotlib and seaborn chart generation for ESG analysis outputs."""

from __future__ import annotations

from pathlib import Path


def generate_esg_trend_chart(sector_trend_frame, output_path: str | Path) -> None:
    """Generate a sector-level carbon intensity trend chart."""
    _, _, plt, sns = _require_visualization_dependencies()

    figure = plt.figure(figsize=(10, 6))
    sns.lineplot(
        data=sector_trend_frame,
        x="year",
        y="average_carbon_intensity",
        hue="sector",
        marker="o",
    )
    plt.title("ESG Portfolio Carbon Intensity Trend")
    plt.xlabel("Year")
    plt.ylabel("Average carbon intensity (tCO2e / USD million revenue)")
    plt.tight_layout()
    path = _ensure_parent_directory(output_path)
    figure.savefig(path, dpi=150)
    plt.close(figure)


def generate_esg_correlation_heatmap(correlation_matrix, output_path: str | Path) -> None:
    """Generate a correlation heatmap across key ESG variables."""
    _, _, plt, sns = _require_visualization_dependencies()

    figure = plt.figure(figsize=(8.5, 6.5))
    sns.heatmap(correlation_matrix, annot=True, cmap="RdYlGn", center=0, fmt=".2f")
    plt.title("ESG Metric Correlation Heatmap")
    plt.tight_layout()
    path = _ensure_parent_directory(output_path)
    figure.savefig(path, dpi=150)
    plt.close(figure)


def generate_esg_risk_signal_chart(risk_signal_frame, output_path: str | Path) -> None:
    """Generate a latest-year ESG risk signal chart for the highest-risk companies."""
    _, _, plt, sns = _require_visualization_dependencies()

    figure = plt.figure(figsize=(9, 5.5))
    top_risk = risk_signal_frame.head(5).copy()
    sns.barplot(data=top_risk, x="risk_score", y="company", hue="risk_bucket", dodge=False)
    plt.title("Latest-Year ESG Risk Signals")
    plt.xlabel("Risk score")
    plt.ylabel("Company")
    plt.tight_layout()
    path = _ensure_parent_directory(output_path)
    figure.savefig(path, dpi=150)
    plt.close(figure)


def _ensure_parent_directory(path: str | Path) -> Path:
    """Create the parent directory for a chart output path when needed."""
    resolved_path = Path(path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_path


def _require_visualization_dependencies():
    """Load the ESG plotting stack lazily."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        import pandas as pd
        import seaborn as sns
    except ImportError as exc:  # pragma: no cover - exercised only when ESG stack missing
        raise SystemExit(
            "ESG charts require numpy, pandas, matplotlib, and seaborn. Run: python -m pip install -e .[esg]"
        ) from exc
    return pd, np, plt, sns
