# Financial and ESG Analysis Tool

Portfolio-ready Python project for analyzing company financial performance and ESG risk indicators. It combines a lightweight financial statement workflow with a finance-focused ESG analysis workflow so the repo is relevant for accounting, audit, FP&A, ESG, and data roles in financial institutions.

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
- Standard library for the financial analysis workflow
- pandas and numpy for ESG data cleaning and analysis
- matplotlib and seaborn for ESG visualization
- Streamlit as an optional demo UI for the financial workflow
- `unittest` for tests
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
```

Full architecture detail is documented in [architecture.md](C:/Users/Zixsa/Kozphy/financial-analysis-tool/docs/architecture.md).

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
|   |-- cli.py
|   |-- config.py
|   |-- dashboard.py
|   |-- esg_loader.py
|   |-- esg_metrics.py
|   |-- esg_models.py
|   |-- esg_pipeline.py
|   |-- esg_reporting.py
|   |-- esg_visualization.py
|   |-- loader.py
|   |-- metrics.py
|   |-- models.py
|   |-- pipeline.py
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
financial-analysis-tool esg --input data/esg_metrics.csv --audience-name "Cathay Financial Holdings" --summary-output output/reports/esg_summary.json --report-output output/reports/esg_business_insights.md --trend-chart-output output/charts/esg_carbon_trend.png --correlation-chart-output output/charts/esg_correlation_heatmap.png --risk-chart-output output/charts/esg_risk_signal.png
```

## Streamlit Dashboard

The Streamlit UI currently supports the financial analysis workflow:

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
`-- reports/
    |-- financial_summary.json
    |-- executive_summary.md
    |-- esg_summary.json
    `-- esg_business_insights.md
```

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

- It combines finance and ESG analysis in one coherent repo.
- It demonstrates data cleaning, analysis, and visualization.
- It shows business framing rather than only technical implementation.
- It is suitable for junior ESG and data candidates applying to banks, insurers, or asset managers.

## Future Enhancements

1. Add multi-company peer benchmarking across both financial and ESG metrics.
2. Add Excel export with management-ready summary tabs.
3. Add simple scenario analysis for emissions reduction targets or transition-risk watchlists.

## License

MIT. See [LICENSE](C:/Users/Zixsa/Kozphy/financial-analysis-tool/LICENSE).
