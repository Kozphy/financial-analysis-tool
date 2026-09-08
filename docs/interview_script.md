# Interview Script

## 60-Second Explanation

This repo is a **PE / Growth Equity underwriting workflow**, not a sell-side stock-pitch toolkit.

The primary output is an **IC-style memo** on Apple FY2025: **Watch** (not Invest / Pass), with an explicit FCF and net-debt bridge, DCF base case, downside/upside sensitivity corners, and a public-data **Due Diligence Gap** checklist. Every headline number is locked in tests and can be re-run from the command line.

Supporting modules turn statement facts into underwriting outputs, then into explainable risk signals and PE monitoring labels (Invest / Watch / Engage / Reduce). **Pass** stays an IC judgment. There is no ML black box and no fake private dataroom.

## 3-Minute Walkthrough

1. **Accounting → underwriting** — Pull reported FY2025 lines into `CompanySnapshot`; FCF proxy = CFO − capex; net debt = debt − cash/securities.
2. **Valuation** — Explicit five-year FCF path → DCF at 8% WACC / 2.5% g → ≈ **$143.49/sh**; stress at 9%/2% → ≈ **$114.84**; upside corner ≈ **$193.47**.
3. **IC conclusion** — **Watch**, because franchise cash/net cash show on public data, but ~78% of EV is terminal-value PV and commercial/geographic DD is still open.
4. **DD gaps** — Checklist marks each item covered by public data / needs management access / out of scope — no invented private DD.
5. **Monitoring** — `risk_signals.py` + `decision_engine.py` map breaches to stable enums and `pe_action` labels, with JSONL audit (`policy_version`, drivers, rationale).

Optional FastAPI/Streamlit surfaces exist for demos; they are secondary to the memo.

## Reproduce Commands (say this out loud)

```bash
python -m pip install -e ".[dev]"
pytest tests/test_case_study.py -q
```

```bash
python -c "from financial_analysis_tool.case_study import CompanySnapshot, run_dcf_case; s=CompanySnapshot(416161,112010,111482,12715,132420,98657,14773.26); g=[0.07,0.06,0.05,0.045,0.04]; b=run_dcf_case(s,g,0.08,0.025); d=run_dcf_case(s,g,0.09,0.02); u=run_dcf_case(s,g,0.07,0.03); print('FCF', s.free_cash_flow_proxy); print('net_debt', s.net_debt); print('base', round(b.implied_value_per_share,2)); print('downside', round(d.implied_value_per_share,2)); print('upside', round(u.implied_value_per_share,2)); print('IC_stance', 'Watch')"
```

## Why Not Invest / Pass

- **Not Invest:** terminal-value dependence + unfinished commercial DD on public data alone.
- **Not Pass:** public bridge shows strong cash conversion and net cash under the simplified definition — no public kill proven yet.

## API / Engineering Appendix (if they ask)

Thin FastAPI routes → services → pure Python rules. Decision enums stay stable; `pe_action` adds PE language. CSV keeps the case local and auditable; production would version data and policy separately.

## Test Coverage Story

- `tests/test_case_study.py` — FCF bridge, net debt, DCF base, full sensitivity grid, comps placeholders.
- Decision / audit / API tests — explainability, PE mapping, JSONL audit trail.
- Existing loader/metrics/pipeline tests — supporting toolkit integrity.

## What I Would Improve Next

Live time-stamped peer comps (clearly labeled), tighter FCFF/NWC where filings allow, and keep every memo headline number test-locked. I would **not** prioritize new dashboards over underwriting quality.
