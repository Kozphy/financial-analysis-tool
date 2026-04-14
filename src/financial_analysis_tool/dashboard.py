"""Optional Streamlit dashboard for interactive financial analysis demos."""

from __future__ import annotations

import json

from .config import DEFAULT_COMPANY_NAME, DEFAULT_INPUT_PATH
from .loader import load_financial_statements_from_text
from .pipeline import AnalysisArtifacts, analyze_financial_statements
from .reporting import build_markdown_report


def run_dashboard() -> None:
    """Launch the Streamlit dashboard and render the current analysis workflow."""
    try:
        import pandas as pd
        import streamlit as st
    except ImportError as exc:
        raise SystemExit(
            "Streamlit UI dependencies are not installed. Run: python -m pip install -e .[ui]"
        ) from exc

    st.set_page_config(
        page_title="Financial Analysis Dashboard",
        page_icon=":bar_chart:",
        layout="wide",
    )

    st.title("Financial Analysis Dashboard")
    st.caption(
        "Portfolio-ready financial statement analysis for accounting, audit, finance, and analytics interviews."
    )

    with st.sidebar:
        st.header("Inputs")
        company_name = st.text_input("Company name", value=DEFAULT_COMPANY_NAME)
        uploaded_file = st.file_uploader("Upload financial statement CSV", type=["csv"])
        st.caption(
            "Required columns: period, revenue, cost_of_revenue, operating_expenses, net_income, "
            "current_assets, current_liabilities, total_assets, total_liabilities"
        )

    try:
        if uploaded_file is not None:
            csv_text = uploaded_file.getvalue().decode("utf-8-sig")
            records = load_financial_statements_from_text(csv_text)
            artifacts = _analyze_records(records, company_name=company_name)
            input_label = uploaded_file.name
        else:
            artifacts = analyze_financial_statements(
                DEFAULT_INPUT_PATH,
                company_name=company_name,
            )
            input_label = str(DEFAULT_INPUT_PATH)
    except Exception as exc:  # pragma: no cover - UI error state
        st.error(str(exc))
        st.stop()

    summary = artifacts.summary
    metrics_frame = _build_metrics_frame(pd, artifacts.period_metrics)
    latest = summary.latest_period

    st.info(f"Using data source: `{input_label}`")

    top_metrics = st.columns(4)
    top_metrics[0].metric("Latest Revenue", _format_currency(latest.revenue))
    top_metrics[1].metric("Gross Margin", _format_percent(latest.gross_margin))
    top_metrics[2].metric("Current Ratio", _format_ratio(latest.current_ratio))
    top_metrics[3].metric("Debt Ratio", _format_percent(latest.debt_ratio))

    overview_tab, trends_tab, detail_tab, export_tab = st.tabs(
        ["Overview", "Trend Analysis", "Detailed Metrics", "Exports"]
    )

    with overview_tab:
        st.subheader("Executive Summary")
        st.markdown(build_markdown_report(summary))

    with trends_tab:
        left, right = st.columns(2)
        left.subheader("Revenue and Net Income")
        left.line_chart(
            metrics_frame.set_index("period")[["Revenue", "Net Income"]],
            height=320,
        )
        right.subheader("Margin Trend (%)")
        right.line_chart(
            metrics_frame.set_index("period")[
                ["Gross Margin (%)", "Operating Margin (%)", "Net Margin (%)"]
            ],
            height=320,
        )

        left, right = st.columns(2)
        left.subheader("Liquidity and Leverage")
        left.line_chart(
            metrics_frame.set_index("period")[["Current Ratio", "Debt Ratio (%)"]],
            height=320,
        )
        right.subheader("Balance Sheet Position")
        right.area_chart(
            metrics_frame.set_index("period")[["Current Assets", "Current Liabilities"]],
            height=320,
        )

    with detail_tab:
        st.subheader("Period Metrics")
        st.dataframe(metrics_frame, use_container_width=True, hide_index=True)

    with export_tab:
        summary_json = json.dumps(summary.to_dict(), indent=2)
        report_markdown = build_markdown_report(summary)
        st.subheader("Download Outputs")
        st.download_button(
            "Download JSON Summary",
            data=summary_json,
            file_name="financial_summary.json",
            mime="application/json",
        )
        st.download_button(
            "Download Executive Summary",
            data=report_markdown,
            file_name="executive_summary.md",
            mime="text/markdown",
        )


def _analyze_records(records, *, company_name: str) -> AnalysisArtifacts:
    """Reuse the core metric pipeline for records uploaded through the dashboard."""
    from .metrics import build_analysis_summary, calculate_period_metrics

    period_metrics = calculate_period_metrics(records)
    summary = build_analysis_summary(period_metrics, company_name=company_name)
    return AnalysisArtifacts(records=records, period_metrics=period_metrics, summary=summary)


def _build_metrics_frame(pd, period_metrics):
    """Build the tabular DataFrame used by the dashboard charts and data grid."""
    rows = []
    for period in period_metrics:
        rows.append(
            {
                "period": period.period,
                "Revenue": round(period.revenue, 2),
                "Net Income": round(period.net_income, 2),
                "Revenue Growth (%)": _percent_number(period.revenue_growth),
                "Gross Margin (%)": _percent_number(period.gross_margin),
                "Operating Margin (%)": _percent_number(period.operating_margin),
                "Net Margin (%)": _percent_number(period.net_margin),
                "Current Ratio": round(period.current_ratio or 0.0, 2),
                "Debt Ratio (%)": _percent_number(period.debt_ratio),
                "Current Assets": round(period.current_assets, 2),
                "Current Liabilities": round(period.current_liabilities, 2),
                "Total Assets": round(period.total_assets, 2),
                "Total Liabilities": round(period.total_liabilities, 2),
            }
        )
    return pd.DataFrame(rows)


def _percent_number(value: float | None) -> float:
    """Convert an optional decimal ratio into a rounded percentage number."""
    return round((value or 0.0) * 100, 2)


def _format_currency(value: float) -> str:
    """Format a numeric amount for dashboard KPI cards."""
    return f"${value:,.0f}"


def _format_percent(value: float | None) -> str:
    """Format a decimal ratio as a percentage label for dashboard KPIs."""
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def _format_ratio(value: float | None) -> str:
    """Format a ratio value as an x-multiple for dashboard KPIs."""
    if value is None:
        return "n/a"
    return f"{value:.2f}x"


def main() -> None:
    """Expose a module-friendly entrypoint for the Streamlit dashboard."""
    run_dashboard()
