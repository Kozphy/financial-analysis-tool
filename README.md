# Financial Analytics & Decision Intelligence Platform

A finance-facing Python portfolio project that connects **accounting, financial statement analysis, forecasting, valuation, portfolio risk, ESG analytics, and decision intelligence**.

The project is designed to communicate a clear professional story:

```text
Accounting foundation
        ↓
Financial statement analysis
        ↓
Revenue / earnings / cash-flow forecasting
        ↓
DCF + comparable valuation
        ↓
Portfolio & ESG risk analytics
        ↓
Decision intelligence
        ↓
AI / model governance
```

## Featured Real-Company Case Study

### Apple FY2025 — Financial Analysis & DCF

The repository now includes a reproducible public-company case study built from Apple FY2025 financial statements:

- reported revenue, net income, operating cash flow, capex, cash/securities, debt, shares, Services revenue, and Greater China revenue;
- accounting-to-FCF and net-debt bridges;
- five-year explicit FCF growth assumptions;
- DCF enterprise value and equity value;
- WACC × terminal-growth sensitivity analysis;
- finance-style interpretation, risks, limitations, and source lineage;
- unit-tested Python helpers that reproduce the case.

Read the case study: [`case_studies/apple_fy2025.md`](case_studies/apple_fy2025.md)

Source dataset: [`data/apple_fy2025_case.csv`](data/apple_fy2025_case.csv)

> The case study is educational and uses illustrative analyst assumptions. It is not a price target or investment recommendation.

## Why This Project Exists

Many finance portfolios stop at spreadsheets or notebooks. This repository shows how financial analysis can be turned into a tested, reusable decision system with Python, APIs, dashboards, explainable risk signals, and auditable assumptions.

It is especially relevant to roles such as:

- Financial Analyst
- Finance / Data Analyst
- Investment Analytics
- Risk Analytics
- Technology Risk / Financial Risk
- Decision Intelligence
- AI / Model Governance in financial services

## Finance Portfolio Track

### 1. Financial Statement Analysis

Existing workflows analyze:

- revenue growth
- gross margin
- operating margin
- net margin
- current ratio
- debt ratio
- financial trends over time

### 2. Financial Forecasting

`src/financial_analysis_tool/forecasting.py`

Includes:

- historical growth rates
- CAGR
- forward growth forecasts
- average-historical-growth baseline
- base / bull / bear scenario forecasts

Use cases include revenue, EBITDA, earnings, and free-cash-flow forecasting.

### 3. Corporate Valuation

`src/financial_analysis_tool/valuation.py`

Includes:

- present-value calculations
- Gordon Growth terminal value
- DCF enterprise value
- net-debt bridge to equity value
- implied value per share
- simple comparable-company multiple valuation

### 4. Reproducible Company Case Studies

`src/financial_analysis_tool/case_study.py`

Includes:

- company financial snapshots;
- CFO-minus-capex FCF proxy bridges;
- debt-minus-cash/securities net-debt bridges;
- explicit growth-path projections;
- DCF case execution;
- WACC × terminal-growth sensitivity tables.

### 5. Portfolio Risk Analytics

`src/financial_analysis_tool/portfolio_risk.py`

Includes:

- simple returns
- annualized volatility
- Sharpe ratio
- historical Value at Risk
- Expected Shortfall
- maximum drawdown

### 6. ESG & Explainable Risk Intelligence

The existing ESG workflow supports:

- carbon emissions analysis
- ESG score trends
- renewable-energy and green-capex indicators
- governance and controversy signals
- explainable row-level risk signals
- portfolio decision mapping

## API Product

The FastAPI layer exposes finance and risk intelligence through JSON endpoints.

```text
Sample financial / ESG data
        ↓
Loaders + metrics
        ↓
Forecasting / valuation / risk logic
        ↓
Risk signals + decision engine
        ↓
FastAPI services
        ↓
JSON / dashboard / reporting surfaces
```

Key endpoints include:

- `GET /health`
- `GET /companies`
- `GET /features/{company}`
- `GET /signals/{company}`
- `GET /risk/{company}`
- `GET /decisions/{company}`
- `POST /pipeline/run`

## Repository Layout

```text
financial-analysis-tool/
├── case_studies/
│   └── apple_fy2025.md
├── data/
│   └── apple_fy2025_case.csv
├── docs/
│   ├── architecture.md
│   ├── data_pipeline.md
│   ├── data_dictionary.md
│   └── finance_portfolio_track.md
├── output/
│   ├── charts/
│   └── reports/
├── src/financial_analysis_tool/
│   ├── api/
│   ├── case_study.py
│   ├── forecasting.py
│   ├── valuation.py
│   ├── portfolio_risk.py
│   ├── metrics.py
│   ├── risk_signals.py
│   ├── decision_engine.py
│   ├── pipeline.py
│   └── esg_pipeline.py
├── tests/
│   └── test_case_study.py
├── main.py
├── streamlit_app.py
└── pyproject.toml
```

## Installation

Base install:

```bash
python -m pip install -e .
```

Development and tests:

```bash
python -m pip install -e .[dev]
pytest
```

API:

```bash
python -m pip install -e .[api]
python -m uvicorn financial_analysis_tool.api.app:app --reload
```

Full environment:

```bash
python -m pip install -e .[full]
```

## Example: Reproduce the Apple FY2025 DCF

```python
from financial_analysis_tool.case_study import CompanySnapshot, run_dcf_case

snapshot = CompanySnapshot(
    revenue=416_161,
    net_income=112_010,
    cash_from_operations=111_482,
    capital_expenditures=12_715,
    cash_and_securities=132_420,
    debt=98_657,
    shares_outstanding=14_773.26,
)

result = run_dcf_case(
    snapshot,
    growth_rates=[0.07, 0.06, 0.05, 0.045, 0.04],
    wacc=0.08,
    terminal_growth_rate=0.025,
)

print(result.implied_value_per_share)
```

Under those illustrative assumptions, the expected model output is approximately `143.49`.

## Example: Revenue Forecast Scenarios

```python
from financial_analysis_tool.forecasting import scenario_forecast

forecast = scenario_forecast(
    latest_value=1_000,
    base_growth=0.06,
    bull_growth=0.10,
    bear_growth=-0.02,
    periods=5,
)
```

## Example: Portfolio Risk

```python
from financial_analysis_tool.portfolio_risk import (
    annualized_volatility,
    expected_shortfall,
    historical_var,
    max_drawdown,
    sharpe_ratio,
    simple_returns,
)

prices = [100, 103, 101, 108, 104, 111]
returns = simple_returns(prices)

print(annualized_volatility(returns))
print(sharpe_ratio(returns))
print(historical_var(returns))
print(expected_shortfall(returns))
print(max_drawdown(prices))
```

## Interview Positioning

This repository is intentionally positioned as more than a coding project.

**Core narrative:**

> Accounting + Financial Analysis + Python + Forecasting + Valuation + Risk → Decision Intelligence

The differentiator is the ability to combine finance/accounting reasoning with tested software, public-company analysis, transparent assumptions, and explainable decision logic.

## Next Milestones

1. Upgrade the Apple case to a full three-statement forecast.
2. Add explicit FCFF: EBIT × (1 − tax) + D&A − capex − change in NWC.
3. Add segment-level revenue and margin drivers.
4. Add peer-company comparable valuation ranges with time-stamped market data.
5. Add bull/base/bear investment theses and scenario probabilities.
6. Build a portfolio dashboard for volatility, VaR, Expected Shortfall, and drawdown.
7. Generate management-ready investment memo outputs automatically.
8. Add source-lineage and model-validation checks.

See [`docs/finance_portfolio_track.md`](docs/finance_portfolio_track.md) for the detailed finance roadmap.

## Scope & Disclaimer

The bundled data and analytics are for education, portfolio demonstration, and software engineering practice. They are not investment advice, regulatory reporting, or a recommendation to buy or sell any security.

## License

MIT. See [`LICENSE`](LICENSE).
