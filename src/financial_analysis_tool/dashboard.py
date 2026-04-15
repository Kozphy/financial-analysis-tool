"""Top-level Streamlit dashboard launcher."""

from __future__ import annotations

from .esg_dashboard import render_esg_dashboard
from .financial_dashboard import render_financial_dashboard


def run_dashboard() -> None:
    """Launch the Streamlit dashboard and dispatch to the selected workflow."""
    try:
        import pandas as pd
        import streamlit as st
    except ImportError as exc:
        raise SystemExit(
            "Streamlit UI dependencies are not installed. Run: python -m pip install -e .[ui]"
        ) from exc

    st.set_page_config(
        page_title="Financial and ESG Analysis Dashboard",
        page_icon=":bar_chart:",
        layout="wide",
    )

    st.title("Financial and ESG Analysis Dashboard")
    st.caption(
        "Portfolio-ready financial statement and ESG analysis for accounting, audit, finance, ESG, and analytics interviews."
    )

    with st.sidebar:
        workflow = st.radio("Workflow", ("Financial Analysis", "ESG Analysis"))

    if workflow == "Financial Analysis":
        render_financial_dashboard(st, pd)
        return

    render_esg_dashboard(st, pd)


def main() -> None:
    """Expose a module-friendly entrypoint for the Streamlit dashboard."""
    run_dashboard()
