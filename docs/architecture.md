# Architecture

This repo is intentionally simple. The goal is a clean, explainable financial analysis workflow rather than a large application platform.

## High-Level Flow

```text
CSV Input
   |
   v
loader.py
   |
   v
metrics.py
   |
   |----> reporting.py ------> JSON summary + Markdown summary
   |
   `----> visualization.py --> SVG charts
   |
   v
pipeline.py
   |
   |----> cli.py
   `----> dashboard.py (Streamlit)
```

## Module Responsibilities

### `loader.py`
- reads and validates financial statement CSV files
- enforces required columns
- normalizes and sorts reporting periods

### `metrics.py`
- calculates profitability, liquidity, and leverage metrics
- builds the summary object used by reports and UI

### `visualization.py`
- creates static SVG charts for GitHub screenshots and portfolio artifacts

### `reporting.py`
- generates console output, JSON summaries, and Markdown executive summaries

### `pipeline.py`
- coordinates the full analysis workflow
- exposes a shared analysis result used by both CLI and Streamlit

### `cli.py`
- provides a simple command-line interface for batch runs and local demos

### `dashboard.py`
- provides a minimal Streamlit interface for interview demos and portfolio presentation

## Design Principles

- Keep business logic independent from UI.
- Keep the core pipeline runnable with only the standard library.
- Add Streamlit and pandas only as optional presentation-layer dependencies.
- Optimize for clarity, traceability, and ease of review.
