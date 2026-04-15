# Project Architecture

This project now has two related workflows under one package:

1. Financial statement analysis
2. ESG portfolio analysis

The design goal is to keep both workflows small, transparent, and interview-friendly while still reflecting the kind of analysis a financial institution would care about.

## System Diagram

```mermaid
flowchart TD
    A["Financial CSV"] --> B["loader.py"]
    B --> C["metrics.py"]
    C --> D["pipeline.py"]
    D --> E["reporting.py"]
    D --> F["visualization.py"]
    D --> G["cli.py"]
    D --> H["dashboard.py"]

    I["ESG CSV"] --> J["esg_loader.py"]
    J --> K["esg_metrics.py"]
    K --> L["esg_pipeline.py"]
    L --> M["esg_reporting.py"]
    L --> N["esg_visualization.py"]
    L --> G

    E --> O["output/reports/financial_summary.json"]
    F --> P["output/charts/financial_*.svg"]
    M --> Q["output/reports/esg_summary.json"]
    N --> R["output/charts/esg_*.png"]
```

## Module Boundaries

### Financial Workflow

- `models.py`
  - data contracts for financial records, period metrics, and summary output
- `loader.py`
  - CSV validation and parsing
- `metrics.py`
  - profitability, liquidity, and leverage calculations
- `pipeline.py`
  - orchestration for financial analysis outputs
- `reporting.py`
  - console, Markdown, and JSON output
- `visualization.py`
  - static SVG chart generation

### ESG Workflow

- `esg_models.py`
  - data contracts for ESG insights and summary output
- `esg_loader.py`
  - CSV loading, duplicate removal, missing-value handling, derived ESG metrics
- `esg_metrics.py`
  - sector summaries, correlation analysis, risk signal construction, business insights
- `esg_pipeline.py`
  - orchestration for ESG reports and plots
- `esg_reporting.py`
  - business-facing ESG summary output
- `esg_visualization.py`
  - matplotlib and seaborn visualizations

### Shared Delivery Surface

- `cli.py`
  - root financial workflow
  - `esg` subcommand for the ESG workflow
- `dashboard.py`
  - top-level Streamlit dashboard launcher
- `financial_dashboard.py`
  - financial Streamlit view and UI helpers
- `esg_dashboard.py`
  - ESG Streamlit view and UI helpers

## Data Contracts

- Financial input schema and metric definitions are documented in [data_dictionary.md](C:/Users/Zixsa/Kozphy/financial-analysis-tool/docs/data_dictionary.md).
- ESG input schema, imputation rules, and derived fields are also documented there.
- This keeps the business contract explicit instead of burying it in loader code alone.

## Execution Paths

### Financial Path

```text
main.py
  -> cli.py
  -> pipeline.py
  -> loader.py
  -> metrics.py
  -> reporting.py
  -> visualization.py
```

### ESG Path

```text
main.py esg
  -> cli.py
  -> esg_pipeline.py
  -> esg_loader.py
  -> esg_metrics.py
  -> esg_reporting.py
  -> esg_visualization.py
```

The detailed input-to-output flow for both paths is documented in [data_pipeline.md](C:/Users/Zixsa/Kozphy/financial-analysis-tool/docs/data_pipeline.md).

## Design Principles

- Keep business logic separate from UI and file output.
- Keep the financial workflow lightweight and standard-library based.
- Use pandas, numpy, matplotlib, and seaborn only where they add value: ESG cleaning, analysis, and visual exploration.
- Make outputs readable for finance stakeholders, not only engineers.
- Keep optional workflows explicit so users understand which dependencies are required.

## ESG Analysis Focus

The ESG workflow is built to surface signals useful in a financial institution:
- trend in carbon intensity
- correlation between ESG quality and sustainability indicators
- latest-year risk signals for investee monitoring

This makes the repo suitable for junior ESG, sustainability, data, and finance-role applications.
