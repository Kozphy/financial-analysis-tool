# Financial Analysis Tool

A Python project for analyzing company financial performance using structured financial data.

## Overview

This repository provides a lightweight command-line workflow for reading company financial statement data from CSV, calculating key performance metrics, and exporting both a machine-readable summary and a visual trend report.

## Features

- Load structured financial data from CSV
- Calculate revenue growth, gross margin, operating margin, and net margin
- Print a readable terminal summary for each reporting period
- Export a JSON summary for downstream automation or reporting
- Generate an SVG chart showing revenue, net income, and margin trends

## Quick Start

Run the included sample dataset:

```bash
python main.py
```

Use a custom input file:

```bash
python main.py --input data/financials.csv --summary-output output/summary.json --chart-output output/charts.svg
```

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

## CSV Schema

The CLI expects the following columns in chronological order:

```csv
period,revenue,cost_of_revenue,operating_expenses,net_income
2025-Q1,1565000,615000,420000,301000
```

## Project Structure

```text
financial-analysis-tool/
|-- data/
|   `-- financials.csv
|-- output/
|   `-- .gitkeep
|-- src/
|   `-- financial_analysis_tool/
|       |-- __init__.py
|       |-- __main__.py
|       |-- cli.py
|       |-- data_loader.py
|       |-- metrics.py
|       |-- models.py
|       |-- reporting.py
|       `-- visualization.py
|-- tests/
|   `-- test_financial_analysis.py
|-- Dockerfile
|-- README.Docker.md
|-- README.md
|-- main.py
`-- requirements.txt
```

## Outputs

Running the project creates:

- `output/summary.json` with structured metrics
- `output/charts.svg` with a shareable trend visualization

## Notes

- The project uses Python's standard library only.
- Input rows should be ordered from oldest period to newest period for accurate growth calculations.
