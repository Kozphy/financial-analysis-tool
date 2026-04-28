# Interview Script

## 60-Second Explanation

This project is a Financial ESG Risk Intelligence API. It started as a financial and ESG analytics repo that loaded local CSVs, calculated metrics, and generated reports. I upgraded it into a production-style FastAPI service without rewriting the core logic.

The API exposes company features, explainable risk signals, risk profiles, decisions, and pipeline execution endpoints. The important design choice is separation: FastAPI route handlers are thin, services orchestrate the existing workflows, and business rules live in pure Python modules for risk signals and decision mapping.

## 3-Minute Technical Walkthrough

The data source is intentionally simple: bundled sample CSV files for financial statements and ESG metrics. The existing loaders validate and clean those files. The existing financial and ESG pipelines calculate profitability, liquidity, leverage, ESG trends, carbon intensity, governance indicators, and portfolio-level ESG summaries.

I added a new API layer under `src/financial_analysis_tool/api/`. `app.py` defines the routes, `schemas.py` defines Pydantic request and response models, and `services.py` adapts the existing analysis outputs into JSON-safe API responses.

I also added `risk_signals.py` and `decision_engine.py`. The risk signal engine emits row-level explainable signals with company, year, signal type, severity, reason, metric value, and recommendation. The decision engine maps those signals into portfolio actions such as `HOLD`, `REVIEW`, `ENGAGE`, `REDUCE_EXPOSURE`, and `ENHANCED_DUE_DILIGENCE`.

Tests cover the API wiring, unknown-company error handling, deterministic signal generation, and decision mapping logic.

## API Boundary Explanation

The API layer does not calculate business logic directly. Route handlers call service functions. Services call existing pipeline and metric functions, then invoke pure business modules for risk signals and decisions. This makes the code easier to test and keeps HTTP concerns separate from analytical rules.

## CSV vs Database Tradeoff

I kept CSV because this is an interview-ready local project. It is free, reproducible, easy to inspect, and avoids infrastructure setup. In production, I would move the data into a database, object storage plus a warehouse, or a feature store depending on access patterns and freshness requirements.

## Fixed vs Configurable Threshold Tradeoff

The current signal thresholds are fixed so the sample is deterministic and easy to explain. In production, I would version threshold policies and make them configurable by portfolio, sector, asset class, or risk appetite.

## Scaling To Thousands Of Companies

To scale, I would not recalculate everything from CSV on every request. I would ingest raw data on a schedule, validate it, materialize company-year features, precompute risk signals, and cache API responses for common queries. I would also add pagination, filtering, authentication, and audit logs.

## What To Cache

I would cache:

- cleaned ESG datasets by data vintage
- company feature payloads
- risk signal lists by company and year
- decision outputs by company and policy version
- company lists and metadata

## API Versioning

I would version API routes and schemas with paths such as `/v1/signals/{company}`. I would also version the risk policy separately so a client can distinguish schema changes from business-rule changes.

## Data Quality And Drift Monitoring

I would monitor missing values, duplicate company-year rows, invalid numeric fields, outlier movements, coverage changes, and shifts in portfolio-level carbon intensity or ESG score distributions. For model-like rules, I would also monitor how often each signal type fires over time.

## Test Coverage Story

The tests are split by responsibility:

- API tests cover health checks, company discovery, unknown-company errors, and response shape.
- Risk signal tests cover explainability and deterministic output.
- Decision engine tests cover how high-severity and multi-signal cases map to portfolio actions.
- Existing tests still cover loaders, metrics, pipelines, reporting, CLI behavior, and dashboard imports.

## What I Would Improve Next

I would add API versioning, OpenAPI examples, configurable risk policies, a lightweight persistence layer, and cached feature stores. I would also add contract tests for response schemas and data-quality checks that fail fast when source data changes unexpectedly.
