# Finance Portfolio Track

Primary narrative for PE / Growth Equity / Deal Advisory readers:

```text
Accounting → Underwriting → Valuation → Risk → Monitoring decision
```

Hero artifact: [`case_studies/apple_fy2025.md`](../case_studies/apple_fy2025.md) (IC-style memo, conclusion **Watch**).

## Reproduce the Apple IC recommendation

```bash
# from repository root
python -m pip install -e ".[dev]"
pytest tests/test_case_study.py -q
```

```bash
python -c "from financial_analysis_tool.case_study import CompanySnapshot, run_dcf_case; s=CompanySnapshot(416161,112010,111482,12715,132420,98657,14773.26); g=[0.07,0.06,0.05,0.045,0.04]; b=run_dcf_case(s,g,0.08,0.025); d=run_dcf_case(s,g,0.09,0.02); u=run_dcf_case(s,g,0.07,0.03); print('FCF', s.free_cash_flow_proxy); print('net_debt', s.net_debt); print('base', round(b.implied_value_per_share,2)); print('downside', round(d.implied_value_per_share,2)); print('upside', round(u.implied_value_per_share,2)); print('IC_stance', 'Watch')"
```

Expected: FCF `98767`, net debt `-33763`, base `143.49`, downside `114.84`, upside `193.47`, `IC_stance Watch`.

## Supporting modules

### 1. Financial Statement Analysis

Use the existing loaders, metrics, reporting, API, and dashboard layers to analyze revenue growth, margins, liquidity, leverage, ESG quality, and explainable risk signals.

### 2. Forecasting

`src/financial_analysis_tool/forecasting.py` adds dependency-light forecasting utilities:

- historical growth rates
- CAGR
- forward forecasts from an explicit growth assumption
- average-historical-growth baseline
- base / bull / bear scenarios

Recommended interview project: forecast revenue, EBITDA, or free cash flow rather than presenting stock-price prediction as the main finance signal.

### 3. Valuation

`src/financial_analysis_tool/valuation.py` and `case_study.py` add:

- present-value calculation
- Gordon Growth terminal value
- DCF enterprise value
- net-debt bridge to equity value
- implied value per share
- simple comparable-company multiple valuation
- WACC × terminal-growth sensitivity for the Apple IC memo

### 4. Portfolio & Risk Analytics

`src/financial_analysis_tool/portfolio_risk.py` adds:

- simple returns
- annualized volatility
- Sharpe ratio
- historical VaR
- Expected Shortfall
- maximum drawdown

### 5. Monitoring decisions

`decision_engine.py` maps explainable signals to stable enums and PE labels (Invest / Watch / Engage / Reduce). **Pass** is IC-only. Audit trail via `decision_audit.py` (no ML).

## Suggested Next Milestones

1. Time-stamped peer comps (still label illustrative vs live).
2. Tighter FCFF / NWC bridges where filings allow.
3. Keep every memo headline number locked in `tests/test_case_study.py`.

## Interview Positioning

> Audited Apple FY2025 underwriting workflow: accounting → cash bridges → DCF/sensitivity → DD gaps → Watch — with reproduce commands and tests a PE associate can challenge.
