# Growth Equity / PE Underwriting Workflow

A reproducible Python workflow for **public-company underwriting** aimed at Growth Equity, PE, and Deal Advisory readers.

Hero path:

```text
Accounting
        ↓
Underwriting
        ↓
Valuation
        ↓
Risk
        ↓
Monitoring decision
```

The point of the repo is not a feature catalog. It is an **IC-style case** you can skim in minutes, then re-run from tested code.

## IC case study (start here)

### Apple FY2025 — underwriting memo

Read: [`case_studies/apple_fy2025.md`](case_studies/apple_fy2025.md)  
Source data: [`data/apple_fy2025_case.csv`](data/apple_fy2025_case.csv)

**What the workflow does**

1. Extract reported FY2025 statement facts (revenue, net income, CFO, capex, cash/securities, debt, shares, Services, Greater China).
2. Underwrite cash generation: CFO − capex FCF proxy and net cash / net debt bridge.
3. Value with explicit FCF growth path, DCF, and WACC × terminal-growth sensitivity.
4. Surface risks that would matter in a diligence or monitoring context (terminal-value dependence, growth fade, geographic exposure, share-count dynamics).
5. Keep reported facts separate from analyst assumptions so an associate can audit the model.

**Investment takeaway (illustrative, educational only)**

| Field | Working stance |
|---|---|
| IC-style conclusion | **Watch** |
| Why | Franchise-quality cash generation and net cash are clear in the filings, but base-case value is highly sensitive to WACC and terminal growth; public data alone does not close commercial / geographic diligence. |
| Base-case model output | Implied value ≈ **$143.49 / share** at 8.0% WACC and 2.5% terminal growth |
| Downside / stress lens | Same FCF path at higher WACC / lower g (see sensitivity table in the memo) |
| Monitoring language in code | Stable enums `HOLD` / `REVIEW` / `ENGAGE` / `REDUCE_EXPOSURE` / `ENHANCED_DUE_DILIGENCE` → PE labels **Invest / Watch / Engage / Reduce** (`pe_action`). **Pass** is IC-only. Explainable drivers + JSONL audit; no ML. |

> Educational portfolio artifact with illustrative assumptions. Not investment advice, not a price target, and not a private-deal recommendation.

### Reproduce the IC recommendation (exact commands)

IC conclusion in the memo is **Watch**, backed by tested bridges and DCF outputs (not a live market call).

```bash
# from repo root
python -m pip install -e ".[dev]"
pytest tests/test_case_study.py -q
```

Expected: all case-study tests pass (FCF **98,767**, net debt **−33,763**, base **$143.49**, downside **$114.84**, upside **$193.47**, full sensitivity table).

```bash
python -c "from financial_analysis_tool.case_study import CompanySnapshot, run_dcf_case, dcf_sensitivity; s=CompanySnapshot(416161,112010,111482,12715,132420,98657,14773.26); g=[0.07,0.06,0.05,0.045,0.04]; b=run_dcf_case(s,g,0.08,0.025); d=run_dcf_case(s,g,0.09,0.02); u=run_dcf_case(s,g,0.07,0.03); print('FCF', s.free_cash_flow_proxy); print('net_debt', s.net_debt); print('base', round(b.implied_value_per_share,2)); print('downside', round(d.implied_value_per_share,2)); print('upside', round(u.implied_value_per_share,2)); print('IC_stance', 'Watch')"
```

Expected stdout:

```text
FCF 98767
net_debt -33763
base 143.49
downside 114.84
upside 193.47
IC_stance Watch
```

Full walkthrough (assumptions, DD gaps, sensitivity grid): [`case_studies/apple_fy2025.md`](case_studies/apple_fy2025.md) Appendix D.
## Who this is for

Built to read cleanly for:

- Growth Equity / PE associates (underwriting + monitoring)
- Deal Advisory / transaction support (bridges, sensitivity, diligence gaps)
- Buy-side analysts who want audited assumptions over slideware

Less optimized as a sell-side “stock pitch toolkit,” though the same engines can support research memos.

## Why it exists

Many finance portfolios stop at spreadsheets or notebooks. This repo shows how underwriting can become a **tested decision workflow**: statement facts → cash bridges → valuation → risk signals → monitoring actions, with assumptions you can challenge in an IC discussion.

## Setup

Base install:

```bash
python -m pip install -e .
```

Development and tests:

```bash
python -m pip install -e .[dev]
pytest
```

API (optional):

```bash
python -m pip install -e .[api]
python -m uvicorn financial_analysis_tool.api.app:app --reload
```

Full environment:

```bash
python -m pip install -e .[full]
```

## Repository layout

```text
financial-analysis-tool/
├── case_studies/
│   └── apple_fy2025.md          # IC-style underwriting memo
├── data/
│   └── apple_fy2025_case.csv
├── docs/
│   ├── architecture.md
│   ├── data_pipeline.md
│   ├── data_dictionary.md
│   └── finance_portfolio_track.md
├── src/financial_analysis_tool/
│   ├── case_study.py            # snapshot, FCF/net-debt bridges, DCF case
│   ├── valuation.py
│   ├── forecasting.py
│   ├── metrics.py
│   ├── risk_signals.py
│   ├── decision_engine.py
│   ├── portfolio_risk.py
│   ├── pipeline.py / esg_pipeline.py
│   └── api/
├── tests/
│   └── test_case_study.py
├── main.py
├── streamlit_app.py
└── pyproject.toml
```

## Supporting toolkit (secondary)

These modules support the IC workflow; they are not the hero.

### Underwriting & valuation

- Statement metrics: revenue growth, gross / operating / net margin, current ratio, debt ratio (`metrics.py`)
- Forecasting: growth rates, CAGR, base / bull / bear paths (`forecasting.py`)
- Valuation: PV, Gordon terminal value, DCF EV → equity → per share, simple comps helper (`valuation.py`)
- Case runner: FCF proxy, net-debt bridge, growth-path DCF, WACC × g sensitivity (`case_study.py`)

### Risk & monitoring

- Portfolio risk: returns, volatility, Sharpe, historical VaR, Expected Shortfall, max drawdown (`portfolio_risk.py`)
- Explainable financial / ESG signals (`risk_signals.py`)
- Deterministic monitoring decisions with PE label mapping and audit trail (`decision_engine.py`, `decision_audit.py`)
- ESG quality, carbon intensity, governance / controversy inputs (`esg_*`)

### Optional surfaces

FastAPI can expose the same logic as JSON for demos:

- `GET /health`, `GET /companies`
- `GET /features/{company}`, `GET /signals/{company}`
- `GET /risk/{company}`, `GET /decisions/{company}`
- `POST /pipeline/run`

Optional surfaces (API / Streamlit / charts) exist for walkthroughs; they are **not** required for the IC memo and are not the hiring-facing hero.

### Quick examples

Revenue scenarios:

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

Portfolio risk:

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
```

## Interview one-liner

> Audited Apple FY2025 underwriting workflow: accounting → cash bridges → DCF/sensitivity → risk → monitoring decision — with reproducible assumptions a PE associate can challenge.

## Next milestones

1. Time-stamped peer comps (label illustrative vs live).
2. Tighten FCFF / NWC bridges beyond the CFO − capex proxy where filings allow.
3. Keep model governance: every IC headline number stays locked in `tests/test_case_study.py`.

See [`docs/finance_portfolio_track.md`](docs/finance_portfolio_track.md) for the broader roadmap.

## Scope & disclaimer

Bundled data and analytics are for education, portfolio demonstration, and software practice. They are not investment advice, regulatory reporting, or a recommendation to buy, sell, or invest in any security or private deal.

## License

Proprietary. See [`LICENSE`](LICENSE).
