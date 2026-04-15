"""Analysis logic for portfolio-style ESG insights and risk signals."""

from __future__ import annotations

from .esg_models import EsgAnalysisSummary, EsgInsight


def build_sector_summary(frame):
    """Aggregate latest-year ESG exposure by sector."""
    latest_year = int(frame["year"].max())
    latest_frame = frame.loc[frame["year"] == latest_year].copy()
    sector_summary = (
        latest_frame.groupby("sector", as_index=False)
        .agg(
            company_count=("company", "nunique"),
            average_esg_score=("esg_score", "mean"),
            average_carbon_intensity=("carbon_intensity", "mean"),
            average_green_capex_pct=("green_capex_pct", "mean"),
        )
        .sort_values("average_carbon_intensity", ascending=False)
        .reset_index(drop=True)
    )
    return sector_summary.round(2)


def build_correlation_matrix(frame):
    """Build a correlation matrix across key ESG metrics."""
    correlation_columns = [
        "esg_score",
        "environment_score",
        "governance_score",
        "renewable_energy_pct",
        "green_capex_pct",
        "carbon_intensity",
        "controversy_count",
    ]
    return frame[correlation_columns].corr(numeric_only=True).round(3)


def build_risk_signal_frame(frame):
    """Create a latest-year ESG risk watchlist for portfolio monitoring."""
    np = _require_numpy()

    latest_year = int(frame["year"].max())
    latest_frame = frame.loc[frame["year"] == latest_year].copy()
    latest_frame["carbon_risk"] = latest_frame["carbon_intensity"].rank(pct=True)
    latest_frame["governance_risk"] = 1 - latest_frame["governance_score"].rank(pct=True)
    latest_frame["controversy_risk"] = latest_frame["controversy_count"].rank(pct=True)
    latest_frame["safety_risk"] = latest_frame["safety_incidents"].rank(pct=True)
    latest_frame["risk_score"] = 100 * (
        (0.40 * latest_frame["carbon_risk"])
        + (0.30 * latest_frame["governance_risk"])
        + (0.20 * latest_frame["controversy_risk"])
        + (0.10 * latest_frame["safety_risk"])
    )
    latest_frame["risk_bucket"] = np.where(
        latest_frame["risk_score"] >= latest_frame["risk_score"].quantile(0.75),
        "High",
        np.where(
            latest_frame["risk_score"] >= latest_frame["risk_score"].median(),
            "Watch",
            "Stable",
        ),
    )
    columns = [
        "company",
        "sector",
        "esg_score",
        "carbon_intensity",
        "governance_score",
        "controversy_count",
        "risk_score",
        "risk_bucket",
    ]
    return latest_frame[columns].sort_values("risk_score", ascending=False).reset_index(drop=True).round(2)


def build_esg_summary(
    frame,
    sector_summary,
    correlation_matrix,
    risk_signal_frame,
    *,
    audience_name: str,
) -> EsgAnalysisSummary:
    """Build the ESG summary and business-facing insights for portfolio reporting."""
    latest_year = int(frame["year"].max())
    earliest_year = int(frame["year"].min())
    earliest_year_frame = frame.loc[frame["year"] == earliest_year]
    latest_year_frame = frame.loc[frame["year"] == latest_year]

    first_carbon_intensity = float(earliest_year_frame["carbon_intensity"].mean())
    latest_carbon_intensity = float(latest_year_frame["carbon_intensity"].mean())
    carbon_intensity_change = ((latest_carbon_intensity - first_carbon_intensity) / first_carbon_intensity) * 100

    first_esg_score = float(earliest_year_frame["esg_score"].mean())
    latest_esg_score = float(latest_year_frame["esg_score"].mean())
    esg_score_change = latest_esg_score - first_esg_score

    esg_carbon_correlation = float(correlation_matrix.loc["esg_score", "carbon_intensity"])
    green_capex_correlation = float(correlation_matrix.loc["green_capex_pct", "esg_score"])

    top_risk = risk_signal_frame.head(3)
    highest_carbon_sector = sector_summary.iloc[0]

    insights = [
        EsgInsight(
            title="Portfolio Decarbonization Trend",
            finding=(
                f"Average carbon intensity moved from {first_carbon_intensity:.2f} to "
                f"{latest_carbon_intensity:.2f} tCO2e per USD million revenue between "
                f"{earliest_year} and {latest_year}, a {carbon_intensity_change:.1f}% change, "
                f"while the average ESG score improved by {esg_score_change:.1f} points."
            ),
            implication=(
                f"For {audience_name}, this suggests the simulated coverage universe is improving on transition metrics, "
                "but engagement should remain focused on heavy-emitting laggards rather than the portfolio average alone."
            ),
        ),
        EsgInsight(
            title="Correlation Between ESG Quality and Transition Indicators",
            finding=(
                f"ESG score shows a {esg_carbon_correlation:.2f} correlation with carbon intensity and a "
                f"{green_capex_correlation:.2f} correlation with green capex intensity."
            ),
            implication=(
                "Companies allocating more capital to sustainability initiatives tend to score better on ESG, "
                "while carbon-intensive names tend to screen weaker. This supports using ESG data as a screening overlay in credit and investment review."
            ),
        ),
        EsgInsight(
            title="Latest-Year Risk Signal",
            finding=(
                f"The highest-risk names in the latest year are {', '.join(top_risk['company'].tolist())}, "
                f"and the most carbon-intensive sector is {highest_carbon_sector['sector']}."
            ),
            implication=(
                f"For {audience_name}, these names and sectors are the clearest candidates for stewardship, enhanced due diligence, "
                "or tighter underwriting and exposure limits."
            ),
        ),
    ]

    return EsgAnalysisSummary(
        audience_name=audience_name,
        cleaned_row_count=int(len(frame)),
        company_count=int(frame["company"].nunique()),
        years=[int(year) for year in sorted(frame["year"].unique())],
        average_esg_score=round(float(frame["esg_score"].mean()), 2),
        average_carbon_intensity=round(float(frame["carbon_intensity"].mean()), 2),
        cleaning_summary=dict(frame.attrs.get("cleaning_summary", {})),
        sector_summary=sector_summary.to_dict(orient="records"),
        high_risk_companies=risk_signal_frame.head(5).to_dict(orient="records"),
        insights=insights,
    )


def _require_numpy():
    """Load numpy lazily so ESG-only dependencies stay isolated."""
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - exercised only when ESG stack missing
        raise SystemExit(
            "ESG analysis requires numpy. Run: python -m pip install -e .[esg]"
        ) from exc
    return np
