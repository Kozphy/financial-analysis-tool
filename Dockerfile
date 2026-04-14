# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.11
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY data ./data
COPY main.py ./main.py

RUN python -m pip install --no-cache-dir .
RUN mkdir -p /app/output/reports /app/output/charts

CMD ["financial-analysis-tool", "--input", "data/financials.csv", "--summary-output", "output/reports/financial_summary.json", "--report-output", "output/reports/executive_summary.md", "--profitability-chart-output", "output/charts/profitability_trends.svg", "--financial-position-chart-output", "output/charts/financial_position_trends.svg"]
