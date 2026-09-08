# API Design

## Purpose

The Financial ESG Risk Intelligence API turns the existing CSV-based financial and ESG workflows into a backend product. It keeps the original analytics logic intact while adding a clean HTTP interface for dashboards, frontend clients, or portfolio monitoring tools.

## Boundary Design

```text
FastAPI routes
  -> API services
  -> existing financial / ESG pipelines
  -> risk signal engine
  -> decision engine
  -> Pydantic JSON responses
```

- `api/app.py` owns routing, response models, and HTTP error mapping.
- `api/schemas.py` owns Pydantic contracts.
- `api/services.py` owns orchestration, sample-data loading, and JSON-safe formatting.
- `risk_signals.py` owns explainable financial and ESG signal rules.
- `decision_engine.py` owns portfolio action mapping.

This separation keeps route handlers thin and makes the business rules testable without an HTTP server.

## Endpoints

- `GET /health`: service status and version.
- `GET /companies`: available companies from bundled sample data.
- `GET /features/{company}`: financial metrics and/or ESG history for a company.
- `GET /signals/{company}`: explainable row-level risk signals.
- `GET /risk/{company}`: summarized severity counts and supporting signals.
- `GET /decisions/{company}`: decision-engine recommendation.
- `POST /pipeline/run`: runs the existing financial, ESG, or combined sample pipelines.

## Risk Signals

Each signal includes:

- `company`
- `year`
- `signal_type`
- `severity`
- `reason`
- `metric_value`
- `recommendation`

Signals are designed for auditability. A reviewer can see not only that a company is risky, but why the rule fired and what action is recommended.

Supported signal types:

- `FINANCIAL_DETERIORATION`
- `HIGH_LEVERAGE`
- `LIQUIDITY_STRESS`
- `HIGH_CARBON_INTENSITY`
- `WEAK_GOVERNANCE`
- `ELEVATED_CONTROVERSY_RISK`
- `ESG_IMPROVEMENT`
- `TRANSITION_RISK_WATCHLIST`

## Decision Mapping

The decision engine is **deterministic policy logic** (not ML). It maps explainable signals into stable code enums:

- `HOLD`
- `REVIEW`
- `ENGAGE`
- `REDUCE_EXPOSURE`
- `ENHANCED_DUE_DILIGENCE`

Each enum also carries a PE portfolio monitoring label (`pe_action`) for Growth Equity / PE readers:

| Code enum | PE action |
|---|---|
| `HOLD` | Invest (maintain) |
| `REVIEW` | Watch |
| `ENGAGE` | Engage |
| `ENHANCED_DUE_DILIGENCE` | Watch (enhanced diligence) |
| `REDUCE_EXPOSURE` | Reduce |

**Pass** is an IC underwriting outcome in case memos (kill criteria). It is not auto-emitted from signals.

Policy precedence (interview-readable):

- No signals maps to `HOLD` / Invest.
- Medium signals map to `REVIEW` / Watch.
- Carbon and transition-risk concerns map to `ENGAGE` / Engage.
- High governance, controversy, or liquidity concerns map to `ENHANCED_DUE_DILIGENCE` / Watch.
- Three or more high-severity signals map to `REDUCE_EXPOSURE` / Reduce.

Decision API responses and JSONL audit logs include `key_drivers`, `rationale`, `pe_action`, and `policy_version` for an explainable audit trail.

## Error Handling

- Unknown companies return `404`.
- Invalid pipeline modes return `400`.
- API responses are Pydantic JSON models, not pandas DataFrames or raw dataclasses.

## Tradeoffs

### CSV vs Database

CSV keeps the project local, free, transparent, and easy to run in interviews. A production version would move source data into object storage, a warehouse, or an OLTP store depending on ingestion and query patterns.

### Fixed vs Configurable Thresholds

Fixed thresholds make the sample deterministic and easy to test. A production version would store threshold policy by sector, asset class, portfolio, or risk committee version.

### Recalculation vs Caching

The API can recalculate from small CSVs quickly. A larger deployment should cache cleaned features, risk signals, and decision outputs by company and data vintage.

## Scaling Path

To scale to thousands of companies:

1. Replace CSV reads with scheduled ingestion into a database or feature store.
2. Precompute company-year features and risk signals.
3. Cache hot endpoint responses.
4. Add API pagination and filtering.
5. Add authentication, authorization, and audit logging.
6. Track schema versions and signal-policy versions.
7. Monitor data quality, missingness, duplicate rows, and metric drift.
