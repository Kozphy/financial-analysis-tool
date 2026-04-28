# Financial ESG Risk Intelligence API

Production-style FastAPI product for financial and ESG risk intelligence using local sample CSV data. The project exposes existing financial statement analysis and ESG analytics through clean JSON endpoints that can support a frontend, dashboard, or portfolio monitoring workflow.

The repo still includes the original CLI and Streamlit analytics workflows, but the primary interview-facing surface is now the API.

## API Product Overview

**Product name:** Financial ESG Risk Intelligence API

The API answers practical portfolio monitoring questions:

- Which companies are covered by the sample financial and ESG universe?
- What financial and ESG features are available for a company?
- Which row-level risk signals explain the company risk profile?
- What portfolio action should a risk analyst consider?
- Can the existing CSV-based pipelines still be run locally?

## API Architecture

```text
Sample CSV data
  -> existing loaders and pipelines
  -> risk_signals.py / decision_engine.py
  -> api/services.py
  -> api/app.py
  -> JSON responses
```

The route handlers stay thin. Business rules live outside FastAPI so they can be tested without HTTP.

```text
src/financial_analysis_tool/
|-- api/
|   |-- app.py          # FastAPI routes only
|   |-- schemas.py      # Pydantic request/response models
|   `-- services.py     # API orchestration and JSON-safe formatting
|-- risk_signals.py     # explainable signal generation
|-- decision_engine.py  # portfolio decision mapping
|-- pipeline.py         # existing financial workflow
`-- esg_pipeline.py     # existing ESG workflow
```

## Run The API Locally

Install API and ESG dependencies:

```bash
python -m pip install -e .[api,esg]
```

Start the API:

```bash
python -m uvicorn financial_analysis_tool.api.app:app --reload
```

Open the interactive docs:

```text
http://127.0.0.1:8000/docs
```

### API Endpoints

- `GET /health`
- `GET /companies`
- `GET /features/{company}`
- `GET /signals/{company}`
- `GET /risk/{company}`
- `GET /decisions/{company}`
- `POST /pipeline/run`

### Example Requests

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/companies
curl http://127.0.0.1:8000/signals/Harbor%20Cement
curl http://127.0.0.1:8000/decisions/Harbor%20Cement
curl -X POST http://127.0.0.1:8000/pipeline/run -H "Content-Type: application/json" -d "{\"mode\":\"all\"}"
```

### Example Decision Response

```json
{
  "company": "Harbor Cement",
  "decision": "REDUCE_EXPOSURE",
  "highest_severity": "HIGH",
  "signal_count": 5,
  "key_drivers": [
    "WEAK_GOVERNANCE: Latest governance score is below the governance quality threshold.",
    "TRANSITION_RISK_WATCHLIST: Company combines elevated carbon intensity with limited renewable energy or green capex indicators.",
    "HIGH_CARBON_INTENSITY: Latest carbon intensity is above the latest-year portfolio watchlist threshold of 0.41."
  ],
  "rationale": "Multiple high-severity signals indicate concentrated downside risk."
}
```

## Run Tests

```bash
python -m pip install -e .[api,esg,dev]
pytest
```

## Business Context

Financial institutions increasingly need two views of the same investee universe:

1. Financial performance
- revenue growth
- profitability margins
- liquidity
- leverage

2. ESG quality and transition risk
- carbon emissions
- ESG scores
- renewable energy adoption
- governance and controversy signals

This project is built to show both.

## Workflows

### Financial Analysis Workflow

Answers:
- How is the company performing financially over time?

Outputs:
- JSON summary
- Markdown executive summary
- SVG profitability chart
- SVG liquidity and leverage chart

### ESG Analysis Workflow

Answers:
- Which companies or sectors show ESG improvement?
- Where are carbon intensity and governance signals creating portfolio risk?
- What should a financial institution prioritize for engagement or enhanced due diligence?

Outputs:
- JSON ESG summary
- Markdown ESG business report
- cleaned ESG dataset export
- matplotlib/seaborn trend chart
- correlation heatmap
- risk signal chart

## Features

- Load structured financial statement data from CSV
- Calculate key financial metrics:
  - revenue growth
  - gross margin
  - operating margin
  - net margin
  - current ratio
  - debt ratio
- Load and clean ESG portfolio data from CSV
- Analyze ESG indicators including:
  - scope 1 and scope 2 emissions
  - ESG score trends
  - renewable energy and green capex indicators
  - governance and controversy risk signals
- Generate finance and ESG charts for portfolio presentation
- Export clean business-facing summaries for GitHub and interviews

## Tech Stack

- Python 3.10+
- FastAPI and Pydantic for the API layer
- Standard library for the financial analysis workflow
- pandas and numpy for ESG data cleaning and analysis
- matplotlib and seaborn for ESG visualization
- Streamlit as an optional demo UI for both financial and ESG workflows
- `unittest` and `pytest` for tests
- `setuptools` for packaging

## Architecture Summary

The repo uses two sibling workflows under one package so the project stays coherent while covering both financial and ESG use cases.

```text
Financial CSV
  -> loader.py
  -> metrics.py
  -> pipeline.py
     -> reporting.py
     -> visualization.py
     -> cli.py
     -> dashboard.py

ESG CSV
  -> esg_loader.py
  -> esg_metrics.py
  -> esg_pipeline.py
     -> esg_reporting.py
     -> esg_visualization.py
     -> cli.py (esg subcommand)

API workflow
  -> api/app.py
  -> api/services.py
  -> risk_signals.py
  -> decision_engine.py
```

Full architecture detail is documented in [architecture.md](C:/Users/Zixsa/Kozphy/financial-analysis-tool/docs/architecture.md).
The end-to-end data flow is documented in [data_pipeline.md](C:/Users/Zixsa/Kozphy/financial-analysis-tool/docs/data_pipeline.md).

## Repository Layout

```text
financial-analysis-tool/
|-- data/
|   |-- financials.csv
|   `-- esg_metrics.csv
|-- docs/
|   |-- architecture.md
|   `-- examples.md
|-- output/
|   |-- charts/
|   `-- reports/
|-- src/financial_analysis_tool/
|   |-- api/
|   |   |-- app.py
|   |   |-- schemas.py
|   |   `-- services.py
|   |-- cli.py
|   |-- config.py
|   |-- decision_engine.py
|   |-- dashboard.py
|   |-- esg_dashboard.py
|   |-- esg_loader.py
|   |-- esg_metrics.py
|   |-- esg_models.py
|   |-- esg_pipeline.py
|   |-- esg_reporting.py
|   |-- esg_visualization.py
|   |-- financial_dashboard.py
|   |-- loader.py
|   |-- metrics.py
|   |-- models.py
|   |-- pipeline.py
|   |-- risk_signals.py
|   |-- reporting.py
|   `-- visualization.py
|-- tests/
|-- main.py
`-- streamlit_app.py
```

## Installation

Base financial workflow:

```bash
python -m pip install -e .
```

Developer tools:

```bash
python -m pip install -e .[dev]
```

ESG workflow dependencies:

```bash
python -m pip install -e .[esg]
```

Streamlit dashboard dependencies:

```bash
python -m pip install -e .[ui]
```

Full local environment:

```bash
python -m pip install -e .[full]
```

## Run The Financial Analysis Pipeline

Use the bundled financial sample:

```bash
python main.py
```

Or:

```bash
financial-analysis-tool
```

## Run The ESG Analysis Pipeline

Use the bundled ESG sample:

```bash
python main.py esg
```

Or:

```bash
financial-analysis-tool esg
```

Custom ESG run:

```bash
financial-analysis-tool esg --input data/esg_metrics.csv --audience-name "Cathay Financial Holdings" --summary-output output/reports/esg_summary.json --report-output output/reports/esg_business_insights.md --cleaned-data-output output/data/esg_cleaned_dataset.csv --trend-chart-output output/charts/esg_carbon_trend.png --correlation-chart-output output/charts/esg_correlation_heatmap.png --risk-chart-output output/charts/esg_risk_signal.png
```

## Streamlit Dashboard

The Streamlit UI supports:
- financial analysis
- ESG overview, risk review, and cleaning audit

Install the UI dependencies:

```bash
python -m pip install -e .[ui]
```

Launch the dashboard:

```bash
python -m streamlit run streamlit_app.py
```

## ESG Dataset Schema

The simulated ESG dataset includes:

```text
company,sector,year,revenue_musd,scope1_emissions_tco2e,scope2_emissions_tco2e,esg_score,environment_score,social_score,governance_score,renewable_energy_pct,green_capex_pct,board_independence_pct,women_board_pct,safety_incidents,controversy_count
```

It includes deliberate data quality issues such as:
- duplicate company-year rows
- missing sustainability values

That allows the project to demonstrate data cleaning as well as analysis.

## Output Structure

```text
output/
|-- charts/
|   |-- profitability_trends.svg
|   |-- financial_position_trends.svg
|   |-- esg_carbon_trend.png
|   |-- esg_correlation_heatmap.png
|   `-- esg_risk_signal.png
|-- data/
|   `-- esg_cleaned_dataset.csv
`-- reports/
    |-- financial_summary.json
    |-- executive_summary.md
    |-- esg_summary.json
    `-- esg_business_insights.md
```

## Data Contracts

The input schemas and calculation assumptions are documented in [data_dictionary.md](C:/Users/Zixsa/Kozphy/financial-analysis-tool/docs/data_dictionary.md).
The cleaned ESG dataset export also includes imputation audit columns and source labels so users can trace which values were filled during cleaning and where the fill came from.

## Example ESG Insights

The ESG workflow is designed to surface business insights a financial institution can act on. In the bundled sample, the analysis is intended to show:

1. Trend
- average carbon intensity declines over time while the average ESG score improves

2. Correlation
- stronger ESG scores tend to align with lower carbon intensity and higher green capex

3. Risk signal
- the highest-risk names combine high carbon intensity, weaker governance, and elevated controversy counts

These are the kinds of findings that support portfolio monitoring, stewardship, underwriting review, or sector engagement planning.

## Why This Project Works In Interviews

- It shows how to turn existing analytics code into an API product without rewriting the core logic.
- It keeps API routes, service orchestration, and business rules separated.
- It produces explainable risk signals instead of opaque scores only.
- It includes tests for both HTTP wiring and pure decision logic.
- It gives a realistic scaling story: CSV sample data today, database-backed ingestion and cached features later.

## Known Scope Boundaries

- ESG analysis is an optional workflow that requires the `.[esg]` dependency group.
- The Streamlit dashboard supports ESG review, but the CLI ESG artifact pipeline is still the richer output surface because it also writes PNG charts to disk.
- The sample datasets are designed for demonstration and portfolio use, not regulatory reporting.

## Future Enhancements

1. Add multi-company peer benchmarking across both financial and ESG metrics.
2. Add Excel export with management-ready summary tabs.
3. Add simple scenario analysis for emissions reduction targets or transition-risk watchlists.

## License

MIT. See [LICENSE](C:/Users/Zixsa/Kozphy/financial-analysis-tool/LICENSE).
