# Financial Analysis Tool

Practical Python project for analyzing company financial statement trends. It loads structured CSV data, calculates core profitability and balance-sheet ratios, and produces presentation-ready outputs for accounting, audit, finance, and analytics portfolios.

## Business Use Case

This project answers a simple business question:

How has a company's profitability, liquidity, and leverage changed over time?

That makes it useful for:
- accounting and audit case discussions
- FP&A and finance analyst interviews
- data analytics portfolios with business context
- GitHub portfolio screenshots and resume bullets

## Features

- Load structured financial statement data from CSV
- Calculate key metrics:
  - revenue growth
  - gross margin
  - operating margin
  - net margin
  - current ratio
  - debt ratio
- Generate clean SVG trend charts for:
  - profitability
  - liquidity and leverage
- Export:
  - JSON summary
  - Markdown executive summary
- Visualize the same analysis in a lightweight Streamlit dashboard

## Tech Stack

- Python 3.10+
- Standard library for the analysis pipeline
- Streamlit and pandas as optional UI dependencies for the dashboard
- `unittest` for tests
- `setuptools` for packaging

## Repository Layout

```text
financial-analysis-tool/
├─ data/
│  └─ financials.csv
├─ docs/
│  ├─ architecture.md
│  └─ examples.md
├─ output/
│  ├─ charts/
│  └─ reports/
├─ src/financial_analysis_tool/
│  ├─ cli.py
│  ├─ config.py
│  ├─ dashboard.py
│  ├─ loader.py
│  ├─ metrics.py
│  ├─ models.py
│  ├─ pipeline.py
│  ├─ reporting.py
│  └─ visualization.py
├─ tests/
├─ main.py
└─ streamlit_app.py
```

## Installation

Base CLI install:

```bash
python -m pip install -e .
```

Install developer tools:

```bash
python -m pip install -e .[dev]
```

Install Streamlit UI extras:

```bash
python -m pip install -e .[ui]
```

## Run The Analysis Pipeline

Use the sample dataset:

```bash
python main.py
```

Or use the console script after install:

```bash
financial-analysis-tool
```

Custom input and output paths:

```bash
financial-analysis-tool --input data/financials.csv --company-name "Harbor Industrial Group" --summary-output output/reports/financial_summary.json --report-output output/reports/executive_summary.md --profitability-chart-output output/charts/profitability_trends.svg --financial-position-chart-output output/charts/financial_position_trends.svg
```

## Run The Streamlit Dashboard

```bash
python -m streamlit run streamlit_app.py
```

The dashboard supports:
- the bundled sample CSV
- uploaded CSV files with the same schema
- KPI cards
- trend charts
- detailed period metrics
- downloadable JSON and Markdown outputs

## Required CSV Schema

```text
period,revenue,cost_of_revenue,operating_expenses,net_income,current_assets,current_liabilities,total_assets,total_liabilities
```

Example:

```csv
2025-Q4,1840000,690000,480000,372000,1205000,568000,2930000,1055000
```

## Output Structure

```text
output/
├─ charts/
│  ├─ profitability_trends.svg
│  └─ financial_position_trends.svg
└─ reports/
   ├─ financial_summary.json
   └─ executive_summary.md
```

## Sample Output

Typical latest-period metrics from the bundled dataset:

- Revenue: `$1.84M`
- Gross margin: `62.5%`
- Operating margin: `36.4%`
- Net margin: `20.2%`
- Current ratio: `2.12x`
- Debt ratio: `36.0%`

## Testing

```bash
python -m unittest discover -s tests -v
```

## Why This Project Works In Interviews

- It shows business-oriented analysis, not just code execution.
- It turns raw financial statement data into interpretable ratios and trends.
- It has both a scriptable pipeline and a simple demo UI.
- It is easy to review quickly on GitHub.

## Future Enhancements

Good next steps that recruiters would recognize as practical:

1. Add multi-company benchmarking and peer comparison.
2. Add Excel export with presentation-ready management summary tabs.
3. Add anomaly flags for margin compression, liquidity deterioration, or leverage drift.

## License

MIT. See [LICENSE](LICENSE).
