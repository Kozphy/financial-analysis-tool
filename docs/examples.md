# Examples

## Run The Default Analysis

```bash
python main.py
```

## Run With A Custom Company Name

```bash
financial-analysis-tool --company-name "North Sea Components"
```

## Run With A Different CSV

```bash
financial-analysis-tool --input data/financials.csv
```

## Write Outputs To A Custom Folder

```bash
financial-analysis-tool --summary-output output/reports/custom_summary.json --report-output output/reports/custom_summary.md --profitability-chart-output output/charts/custom_profitability.svg --financial-position-chart-output output/charts/custom_financial_position.svg
```

## Launch The Streamlit Dashboard

```bash
python -m streamlit run streamlit_app.py
```

## Use Your Own CSV In Streamlit

1. Launch the dashboard.
2. Upload a CSV with the required schema.
3. Review KPI cards, trend charts, and the detailed metrics table.
4. Download the JSON or Markdown outputs.
