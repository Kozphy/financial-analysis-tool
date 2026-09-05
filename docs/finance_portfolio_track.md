# Finance Portfolio Track

This repository now has a dedicated finance-facing track designed to make the portfolio read clearly as **Accounting -> Financial Analysis -> Forecasting -> Valuation -> Portfolio Risk -> Decision Intelligence**.

## 1. Financial Statement Analysis

Use the existing loaders, metrics, reporting, API, and dashboard layers to analyze revenue growth, margins, liquidity, leverage, ESG quality, and explainable risk signals.

## 2. Forecasting

`src/financial_analysis_tool/forecasting.py` adds dependency-light forecasting utilities:

- historical growth rates
- CAGR
- forward forecasts from an explicit growth assumption
- average-historical-growth baseline
- base / bull / bear scenarios

Recommended interview project: forecast revenue, EBITDA, or free cash flow rather than presenting stock-price prediction as the main finance signal.

## 3. Valuation

`src/financial_analysis_tool/valuation.py` adds:

- present-value calculation
- Gordon Growth terminal value
- DCF enterprise value
- net-debt bridge to equity value
- implied value per share
- simple comparable-company multiple valuation

A strong next artifact is an investment memo showing assumptions, forecast drivers, DCF output, comparable valuation, sensitivity analysis, and a conclusion.

## 4. Portfolio & Risk Analytics

`src/financial_analysis_tool/portfolio_risk.py` adds:

- simple returns
- annualized volatility
- Sharpe ratio
- historical VaR
- Expected Shortfall
- maximum drawdown

These metrics can later feed a Streamlit or Power BI portfolio-risk dashboard.

## 5. Target Portfolio Narrative

```text
Accounting foundation
        ↓
Financial statement analysis
        ↓
Revenue / earnings / cash-flow forecasting
        ↓
DCF + comparable valuation
        ↓
Portfolio risk analytics
        ↓
Decision intelligence
        ↓
AI / model governance
```

The objective is not to hide engineering skill. The objective is to make engineering visibly serve financial analysis and decision-making.

## Suggested Next Milestones

1. Add one real-company case study using public filings.
2. Add a three-statement forecast model.
3. Add DCF sensitivity tables for WACC and terminal growth.
4. Add peer-company multiples and valuation ranges.
5. Add a portfolio dashboard with volatility, VaR, Expected Shortfall, and drawdown.
6. Generate a concise investment memo as Markdown/PDF.
7. Add reproducible data-source notes and assumptions.

## Interview Positioning

A useful headline for this project is:

> Financial Analytics & Decision Intelligence — Accounting, Forecasting, Valuation, Risk, Python

The strongest differentiation is: **finance/accounting reasoning plus the ability to build auditable financial decision systems in code.**
