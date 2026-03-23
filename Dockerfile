# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.11
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY . .

RUN mkdir -p /app/output

CMD ["python", "main.py", "--input", "data/financials.csv", "--summary-output", "output/summary.json", "--chart-output", "output/charts.svg"]
