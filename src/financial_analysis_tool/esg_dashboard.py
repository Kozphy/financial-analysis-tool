"""Streamlit views and helpers for the ESG analysis dashboard."""

from __future__ import annotations

import json

from .config import DEFAULT_ESG_AUDIENCE, DEFAULT_ESG_INPUT_PATH
from .esg_loader import load_and_clean_esg_dataset_from_text
from .esg_metrics import (
    build_correlation_matrix,
    build_esg_summary,
    build_risk_signal_frame,
    build_sector_summary,
)
from .esg_pipeline import EsgAnalysisArtifacts, analyze_esg_dataset
from .esg_reporting import build_esg_markdown_report


def render_esg_dashboard(st, pd) -> None:
    """Render the ESG analysis dashboard workflow."""
    with st.sidebar:
        st.header("ESG Inputs")
        audience_name = st.text_input("Audience name", value=DEFAULT_ESG_AUDIENCE)
        uploaded_file = st.file_uploader("Upload ESG metrics CSV", type=["csv"], key="esg_upload")
        st.caption(
            "Required columns: company, sector, year, revenue_musd, scope1_emissions_tco2e, "
            "scope2_emissions_tco2e, esg_score, environment_score, social_score, governance_score, "
            "renewable_energy_pct, green_capex_pct, board_independence_pct, women_board_pct, "
            "safety_incidents, controversy_count"
        )

    try:
        if uploaded_file is not None:
            csv_text = uploaded_file.getvalue().decode("utf-8-sig")
            artifacts = _analyze_esg_text(csv_text, audience_name=audience_name)
            input_label = uploaded_file.name
        else:
            artifacts = analyze_esg_dataset(
                DEFAULT_ESG_INPUT_PATH,
                audience_name=audience_name,
            )
            input_label = str(DEFAULT_ESG_INPUT_PATH)
    except SystemExit as exc:  # pragma: no cover - UI dependency state
        st.error(str(exc))
        st.stop()
    except Exception as exc:  # pragma: no cover - UI error state
        st.error(str(exc))
        st.stop()

    summary = artifacts.summary
    portfolio_trend_frame = _build_esg_portfolio_trend_frame(pd, artifacts.cleaned_frame)
    correlation_frame = artifacts.correlation_matrix.copy()
    risk_frame = artifacts.risk_signal_frame.copy()
    sector_frame = pd.DataFrame(summary.sector_summary)

    st.info(f"Using data source: `{input_label}`")

    top_risk_company = summary.high_risk_companies[0]["company"] if summary.high_risk_companies else "n/a"
    top_metrics = st.columns(4)
    top_metrics[0].metric("Avg ESG Score", f"{summary.average_esg_score:.2f}")
    top_metrics[1].metric("Avg Carbon Intensity", f"{summary.average_carbon_intensity:.2f}")
    top_metrics[2].metric("Companies", str(summary.company_count))
    top_metrics[3].metric("Top Risk Name", top_risk_company)

    overview_tab, trends_tab, correlation_tab, watchlist_tab, export_tab = st.tabs(
        ["Overview", "Trend Analysis", "Correlation", "Risk Watchlist", "Exports"]
    )

    with overview_tab:
        st.subheader("ESG Business Summary")
        st.markdown(build_esg_markdown_report(summary))

    with trends_tab:
        left, right = st.columns(2)
        left.subheader("Portfolio Trend")
        left.line_chart(
            portfolio_trend_frame.set_index("year")[
                ["Average ESG Score", "Average Carbon Intensity"]
            ],
            height=320,
        )
        right.subheader("Transition Readiness")
        right.line_chart(
            portfolio_trend_frame.set_index("year")[
                ["Renewable Energy (%)", "Green Capex (%)"]
            ],
            height=320,
        )

        st.subheader("Sector Carbon Intensity")
        sector_trend_frame = artifacts.sector_trend_frame.pivot(
            index="year",
            columns="sector",
            values="average_carbon_intensity",
        )
        st.line_chart(sector_trend_frame, height=320)

    with correlation_tab:
        st.subheader("Correlation Matrix")
        st.dataframe(correlation_frame, use_container_width=True)

    with watchlist_tab:
        left, right = st.columns(2)
        left.subheader("Latest-Year Risk Signals")
        left.bar_chart(
            risk_frame.head(5).set_index("company")[["risk_score"]],
            height=320,
        )
        left.dataframe(risk_frame, use_container_width=True, hide_index=True)

        right.subheader("Sector Exposure Snapshot")
        right.dataframe(sector_frame, use_container_width=True, hide_index=True)

    with export_tab:
        summary_json = json.dumps(summary.to_dict(), indent=2)
        report_markdown = build_esg_markdown_report(summary)
        st.subheader("Download Outputs")
        st.download_button(
            "Download ESG JSON Summary",
            data=summary_json,
            file_name="esg_summary.json",
            mime="application/json",
        )
        st.download_button(
            "Download ESG Business Report",
            data=report_markdown,
            file_name="esg_business_insights.md",
            mime="text/markdown",
        )


def _analyze_esg_text(csv_text: str, *, audience_name: str) -> EsgAnalysisArtifacts:
    """Reuse the ESG analysis flow for uploaded CSV text in the dashboard."""
    cleaned_frame = load_and_clean_esg_dataset_from_text(csv_text)
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


def _build_esg_portfolio_trend_frame(pd, cleaned_frame):
    """Build the ESG portfolio trend frame used by the dashboard charts."""
    return (
        cleaned_frame.groupby("year", as_index=False)
        .agg(
            average_esg_score=("esg_score", "mean"),
            average_carbon_intensity=("carbon_intensity", "mean"),
            renewable_energy_pct=("renewable_energy_pct", "mean"),
            green_capex_pct=("green_capex_pct", "mean"),
        )
        .rename(
            columns={
                "average_esg_score": "Average ESG Score",
                "average_carbon_intensity": "Average Carbon Intensity",
                "renewable_energy_pct": "Renewable Energy (%)",
                "green_capex_pct": "Green Capex (%)",
            }
        )
        .round(2)
    )
