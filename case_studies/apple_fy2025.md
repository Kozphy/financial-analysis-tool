# Apple FY2025 — IC-Style Underwriting Memo

> Educational portfolio artifact. Illustrative analyst assumptions only.  
> Not investment advice, not a price target, and not a recommendation to transact in Apple securities or any private deal.

**Skim path:** Recommendation → Underwriting → Valuation → Kill criteria → **DD gap checklist** → Appendix.

---

## 1. Recommendation

| Field | Stance |
|---|---|
| **IC conclusion** | **Watch** |
| Base-case model output | ≈ **$143.49 / share** (8.0% WACC, 2.5% terminal growth) |
| Downside case (same FCF path) | ≈ **$114.84 / share** (9.0% WACC, 2.0% terminal growth) |
| Upside sensitivity corner | ≈ **$193.47 / share** (7.0% WACC, 3.0% terminal growth) |
| Monitoring map (repo enums) | Public-data underwriting → continued **REVIEW** (**PE: Watch**); no automated high-severity financial breach in this snapshot. Policy: `pe-monitoring-v1` (rule-based, not ML). |

### Why Watch (not Invest / Pass)

**Invest** would require conviction that (a) the base-case cash-flow path is durable and (b) entry valuation is attractive after diligence. This memo shows **strong reported cash generation and net cash**, but **~78% of base-case enterprise value sits in the terminal-value PV**, and WACC / g move per-share value by tens of dollars. That is underwriting uncertainty, not a closed Invest case.

**Pass** would require a clear kill (broken cash conversion, unsustainable leverage, or a diligence red flag already proven on public data). FY2025 filings show the opposite on leverage/liquidity under this simplified bridge: **net cash of $33.8B**. Geographic and growth-quality questions remain open — they justify **Watch + diligence**, not an automatic Pass.

**One-line IC note:** High-quality franchise cash flows on public numbers; valuation is assumption-sensitive; treat as a monitoring / further-work name until commercial and geographic diligence close.

---

## 2. Business quality / growth drivers

Facts below are **reported FY2025 line items** (USD millions) or simple mixes from those lines. No market-share claims.

| Signal | FY2025 fact | Underwriting read |
|---|---:|---|
| Scale | Revenue **416,161** | Large absolute earnings and cash base |
| Profitability (bottom line) | Net income **112,010** → net margin **26.9%** | High reported earnings conversion vs sales |
| Cash engine | CFO **111,482**; FCF proxy (CFO − capex) **98,767** → FCF / sales **23.7%** | Strong post-capex cash generation under the proxy |
| Mix — Services | Services revenue **109,158** → **26.2%** of total sales | Material recurring-leaning mix alongside hardware ecosystem (category label from filing; not a margin disclosure here) |
| Mix — Greater China | Greater China revenue **64,377** → **15.5%** of total sales | Material regional concentration for demand / policy diligence |
| Capex intensity | Capex **12,715** vs CFO **111,482** | Capex is modest vs operating cash in this year |

**Growth drivers to underwrite (questions, not claims):** durability of Services attach and pricing; hardware cycle and ASP; regional demand including Greater China; capital-return policy vs reinvestment. These are diligence hypotheses — not evidenced as forecasts in the public snapshot alone.

---

## 3. Financial underwriting

All values USD millions unless noted. Gross / operating margins are **not** in `data/apple_fy2025_case.csv`; this memo does not invent them.

### Earnings and cash

| Metric | Value | Notes |
|---|---:|---|
| Revenue | 416,161 | Reported |
| Net income | 112,010 | Reported |
| Net margin | 26.9% | Net income / revenue |
| Cash from operations | 111,482 | Reported |
| Capex | 12,715 | PPE purchases |
| FCF proxy | 98,767 | CFO − capex (simplified; not full FCFF) |
| FCF margin | 23.7% | FCF proxy / revenue |
| CFO margin | 26.8% | CFO / revenue |

### Leverage and liquidity (simplified bridge)

```text
Cash + securities = 35,934 + 18,763 + 77,723 = 132,420
Debt              = 7,979 + 12,350 + 78,328 = 98,657
Net debt          = 98,657 − 132,420 = −33,763   (net cash)
```

| Metric | Value | Read |
|---|---:|---|
| Cash & securities | 132,420 | Cash-like assets in this case definition |
| Gross debt | 98,657 | CP + current + non-current term debt |
| Net debt | **−33,763** | Net cash under this bridge |
| Debt / cash & securities | 0.75× | Not a stressed liquidity picture on year-end balances |

**Caveats for Deal Advisory readers:** this is not a QoE, not a NWC schedule, and not a full net-debt diligence bridge (leases, other debt-like items, restricted cash, etc. are out of scope).

---

## 4. Valuation

### 4.1 DCF (primary)

Explicit FCF growth path (analyst assumptions, not Apple guidance):

| Year | FCF growth | Projected FCF |
|---|---:|---:|
| 1 | 7.0% | 105,680.69 |
| 2 | 6.0% | 112,021.53 |
| 3 | 5.0% | 117,622.61 |
| 4 | 4.5% | 122,915.63 |
| 5 | 4.0% | 127,832.25 |

Base-case inputs: WACC **8.0%**, terminal growth **2.5%**, net debt **−33,763**, shares **14,773.26M**.

| Output | Base case |
|---|---:|
| Enterprise value | $2,085.99B |
| Equity value | $2,119.75B |
| Implied value / share | **$143.49** |
| PV of explicit FCF | ~$464.6B |
| PV of terminal value | ~$1,621.4B (**~77.7%** of EV) |

### 4.2 Simple comps placeholder (illustrative only)

**Not live market comps.** No peer tickers, dates, or broker consensus are asserted. This table only shows how an EV / FCF-style multiple would translate through the repo’s `implied_equity_value_from_multiple` helper using **FY2025 FCF proxy** and the same net-debt bridge.

| Illustrative EV / FCF proxy | Implied equity value | Implied $/share |
|---:|---:|---:|
| 18.0× | $1,811.6B | $122.62 |
| 22.0× | $2,206.6B | $149.37 |
| 26.0× | $2,601.7B | $176.11 |

**Cross-check:** Base DCF (~$143.49) sits between the 18× and 22× placeholder rows. That is a sanity bracket, not a peer-set conclusion. A real Deal / PE comps pack needs time-stamped peer multiples and a consistent metric definition (e.g. NTM EBITDA), which this repo does not fetch.

### 4.3 Scenario lens

| Case | WACC | g | Implied $/share | Use |
|---|---:|---:|---:|---|
| Upside corner | 7.0% | 3.0% | 193.47 | Sensitivity only |
| **Base** | **8.0%** | **2.5%** | **143.49** | Working case |
| **Downside** | **9.0%** | **2.0%** | **114.84** | Stress / Watch trigger |

---

## 5. Key risks / kill criteria

### Material risks (public-data aware)

1. **Terminal-value dependence** — ~78% of base EV from terminal PV; small WACC/g errors dominate value.
2. **Growth fade / maturity** — Path assumes decelerating but still positive FCF growth; a hardware down-cycle or Services slowdown would break the path.
3. **Greater China concentration** — 15.5% of FY2025 sales; demand, channel, and policy outcomes are diligence items.
4. **Share-count / capital return** — Model freezes FY2025 year-end shares; buybacks change per-share economics.
5. **Proxy risk** — CFO − capex is not textbook unlevered FCFF; QoE and NWC can move cash reality.

### Kill / Pass triggers (would flip Watch → Pass)

| Trigger | Evidence bar |
|---|---|
| Cash conversion breaks | Sustained collapse in CFO or FCF proxy vs sales without credible explanation |
| Leverage regime change | Clear shift from net cash to stressed net debt **after** a full debt-like bridge |
| Thesis-breaking geographic shock | Durable impairment of Greater China (or other material) economics evidenced in filings / operations |
| Model integrity failure | Cannot reconcile bridges to primary statements, or assumptions presented as facts |

### Invest upgrade triggers (would flip Watch → Invest)

| Trigger | Evidence bar |
|---|---|
| Entry attractiveness | Diligence-supported cash-flow path with downside still acceptable vs entry price |
| Closed commercial DD | Product, pricing, and Services durability validated beyond category revenue labels |
| Assumption discipline | WACC/g and share-count forecast owned and stress-tested with IC sign-off |

---

## 6. Diligence workplan (if this were a private minority deal)

Public filings are a **starting pack**, not a dataroom. This section is a **Due Diligence Gap checklist** only. It does **not** claim private interviews, dataroom review, or completed QoE were performed.

**Status legend**

| Status | Meaning |
|---|---|
| **Covered by public data** | Supported by FY2025 filings / IR materials already used in this memo (or clearly derivable from them) |
| **Needs management access** | Would require dataroom, management, customers, or advisors in a real private minority deal |
| **Out of scope for this repo** | Intentionally not built here; do not treat absence as a completed negative finding |

### 6.1 Due Diligence Gap checklist

#### Commercial

| Diligence item | Status | What this repo actually has |
|---|---|---|
| Total revenue (FY2025) | Covered by public data | Reported in case CSV / statements |
| Services revenue (category) | Covered by public data | $109,158M reported; mix only |
| Greater China revenue (segment) | Covered by public data | $64,377M reported; concentration flag only |
| Customer cohorts / retention / NRR | Needs management access | Not available from this snapshot |
| Pricing power / discounting / channel inventory | Needs management access | Not in filings used here |
| Pipeline / win-loss / competitor displacement | Needs management access | No private commercial DD performed |
| Unit economics by product SKU | Needs management access | Not disclosed in case inputs |
| Market share / TAM claims | Out of scope for this repo | **Not invented**; do not infer from this memo |

#### Financial (QoE / NWC / net debt)

| Diligence item | Status | What this repo actually has |
|---|---|---|
| Reported net income, CFO, capex | Covered by public data | FY2025 statement lines in case CSV |
| Simplified FCF proxy (CFO − capex) | Covered by public data | Model choice; labeled as proxy, not full FCFF |
| Simplified net cash / net debt bridge | Covered by public data | Cash + securities vs CP + term debt only |
| Quality of Earnings (QoE) adjustments | Needs management access | No multi-year QoE, SBC bridge, or one-off schedule |
| Normalized EBITDA / margin bridge | Needs management access | Gross / operating margins not even in case CSV |
| Net working capital (NWC) analysis | Needs management access | No NWC roll-forward or seasonality study |
| Full debt-like / lease / pension bridge | Needs management access | Leases, guarantees, other debt-like items not in bridge |
| Restricted cash / undrawn facilities | Needs management access | Not verified beyond headline balances |
| True unlevered FCFF build | Out of scope for this repo | Would need tax, D&A, NWC, and interest treatment beyond current helper |
| Live peer comps with market timestamps | Out of scope for this repo | Comps table is an **illustrative multiple placeholder** only |

#### Legal / tax

| Diligence item | Status | What this repo actually has |
|---|---|---|
| Primary financial statement PDF cited | Covered by public data | Source links in Appendix A |
| Entity / subsidiary map | Needs management access | Not reconstructed here |
| Material contracts / IP chain of title | Needs management access | No legal DD |
| Litigation / contingency review | Needs management access | No counsel memo; filings not mined for contingencies in this repo |
| Tax basis, transfer pricing, attributes | Needs management access | No tax DD |
| Minority deal docs (ROFR, vetoes, info rights) | Out of scope for this repo | Public-company demo; no private SPA/SHA workstream |

#### Governance / ESG

| Diligence item | Status | What this repo actually has |
|---|---|---|
| Board / control rights for a minority stake | Needs management access | Not applicable to this public underwriting pack |
| Related-party / key-person risk deep dive | Needs management access | No management interviews |
| Controversy / incident diligence | Needs management access | Not run on Apple in this case CSV |
| Climate / regulatory exposure deep dive | Needs management access | Apple-specific ESG dossier not part of this case |
| Portfolio ESG signal engine (generic sample cos.) | Out of scope for this repo | ESG modules exist for **sample portfolio data**, not wired as Apple IC evidence |
| Fake or simulated private ESG dataroom | Out of scope for this repo | **Explicitly not created** |

### 6.2 How to read the gaps

- **Covered by public data** items support the Watch recommendation’s *facts* (cash generation, net cash under the simplified bridge, mix disclosures).
- **Needs management access** items are why the IC conclusion stays **Watch**, not **Invest**.
- **Out of scope for this repo** items must not be filled with fabricated private DD, market-share claims, or mock dataroom artifacts.

**Associate checklist (first 2 weeks on a real deal):** request dataroom index → rebuild QoE and net debt → customer calls → sync legal/tax red flags → refresh valuation with management case vs diligence case → IC memo with Invest / Watch / Pass and kill criteria.

### 6.3 Post-close monitoring language (code enums)

Repo monitoring after a hypothetical close uses explainable signals → stable enums, with an explicit PE label for associates:

| Code enum | PE monitoring action | Meaning |
|---|---|---|
| `HOLD` | **Invest** | Maintain position; no threshold breach |
| `REVIEW` | **Watch** | Next-cycle review |
| `ENGAGE` | **Engage** | Active management engagement |
| `ENHANCED_DUE_DILIGENCE` | **Watch** | Diligence escalation (not auto-exit) |
| `REDUCE_EXPOSURE` | **Reduce** | Cut exposure / risk budget |
| *(IC memo only)* | **Pass** | Do not invest / kill deal — human underwriting, never auto-emitted by the signal engine |

Audit trail: each `/decisions/{company}` call appends JSONL with `decision`, `pe_action`, `key_drivers`, `rationale`, and `policy_version`. No ML scores.

---

## 7. Appendix

### A. Sources

- Apple FY2025 Q4 consolidated financial statements: https://www.apple.com/newsroom/pdfs/fy2025-q4/FY25_Q4_Consolidated_Financial_Statements.pdf
- Apple Investor Relations: https://investor.apple.com/investor-relations/
- Machine-readable case input: [`data/apple_fy2025_case.csv`](../data/apple_fy2025_case.csv)

### B. Model assumptions (explicit)

| Assumption | Value | Type |
|---|---:|---|
| FCF definition | CFO − capex | Model choice |
| Cash-like assets | Cash + current + non-current marketable securities | Model choice |
| Debt | Commercial paper + current + non-current term debt | Model choice |
| Explicit FCF growth path | 7% / 6% / 5% / 4.5% / 4% | Analyst |
| Base WACC | 8.0% | Analyst |
| Base terminal growth | 2.5% | Analyst |
| Shares | 14,773.26M year-end | Reported (frozen) |
| Comps multiples | 18× / 22× / 26× EV / FCF proxy | **Illustrative placeholder only** |

### C. WACC × terminal-growth sensitivity (implied $/share)

| WACC \ g | 2.0% | 2.5% | 3.0% |
|---:|---:|---:|---:|
| 7.0% | 160.47 | 175.14 | 193.47 |
| 7.5% | 145.95 | 157.73 | 172.13 |
| 8.0% | 133.85 | **143.49** | 155.05 |
| 8.5% | 123.61 | 131.62 | 141.08 |
| 9.0% | **114.84** | 121.58 | 129.44 |

### D. Reproduce the IC recommendation (exact commands)

Memo IC stance: **Watch** (illustrative / educational). Numbers below must match `tests/test_case_study.py`.

#### 1) Install and lock headline numbers with tests

```bash
# run from repository root
python -m pip install -e ".[dev]"
pytest tests/test_case_study.py -q
```

Covered assertions:

| Headline | Expected |
|---|---:|
| FCF bridge (CFO − capex) | 98,767 |
| Net debt bridge | −33,763 |
| Explicit FCF path Y1–Y5 | 105,680.69 … 127,832.25 |
| Base DCF (8.0% / 2.5%) | $143.49 / sh; EV $2,085.99B |
| Downside corner (9.0% / 2.0%) | $114.84 |
| Upside corner (7.0% / 3.0%) | $193.47 |
| Full WACC × g grid | Appendix C table |
| Illustrative comps 18× / 22× / 26× | $122.62 / $149.37 / $176.11 |

#### 2) One-liner reproduce (bridges + base / downside / upside + stance)

```bash
python -c "from financial_analysis_tool.case_study import CompanySnapshot, run_dcf_case; s=CompanySnapshot(416161,112010,111482,12715,132420,98657,14773.26); g=[0.07,0.06,0.05,0.045,0.04]; b=run_dcf_case(s,g,0.08,0.025); d=run_dcf_case(s,g,0.09,0.02); u=run_dcf_case(s,g,0.07,0.03); print('FCF', s.free_cash_flow_proxy); print('net_debt', s.net_debt); print('base', round(b.implied_value_per_share,2)); print('downside', round(d.implied_value_per_share,2)); print('upside', round(u.implied_value_per_share,2)); print('IC_stance', 'Watch')"
```

Expected:

```text
FCF 98767
net_debt -33763
base 143.49
downside 114.84
upside 193.47
IC_stance Watch
```

#### 3) Interactive Python (same numbers)

```python
from financial_analysis_tool.case_study import (
    CompanySnapshot,
    dcf_sensitivity,
    run_dcf_case,
)
from financial_analysis_tool.valuation import implied_equity_value_from_multiple

snapshot = CompanySnapshot(
    revenue=416_161,
    net_income=112_010,
    cash_from_operations=111_482,
    capital_expenditures=12_715,
    cash_and_securities=132_420,
    debt=98_657,
    shares_outstanding=14_773.26,
)

growth_rates = [0.07, 0.06, 0.05, 0.045, 0.04]

base = run_dcf_case(snapshot, growth_rates, wacc=0.08, terminal_growth_rate=0.025)
downside = run_dcf_case(snapshot, growth_rates, wacc=0.09, terminal_growth_rate=0.02)
upside = run_dcf_case(snapshot, growth_rates, wacc=0.07, terminal_growth_rate=0.03)

print(snapshot.free_cash_flow_proxy)              # 98767
print(snapshot.net_debt)                          # -33763
print(round(base.implied_value_per_share, 2))     # 143.49
print(round(downside.implied_value_per_share, 2)) # 114.84
print(round(upside.implied_value_per_share, 2))   # 193.47
print("IC_stance", "Watch")

for multiple in (18.0, 22.0, 26.0):
    equity = implied_equity_value_from_multiple(
        snapshot.free_cash_flow_proxy, multiple, snapshot.net_debt
    )
    print(multiple, round(equity / snapshot.shares_outstanding, 2))

table = dcf_sensitivity(
    snapshot,
    growth_rates,
    wacc_values=[0.07, 0.075, 0.08, 0.085, 0.09],
    terminal_growth_values=[0.02, 0.025, 0.03],
)
```

Why **Watch** (human IC judgment, not a model enum): strong public-data cash / net-cash underwriting, but high terminal-value dependence and open DD gaps (§6). Automated monitoring enums are separate (`REVIEW` → PE **Watch** under `pe-monitoring-v1`).

### E. Limitations (do not hide)

- Single-year snapshot; no three-statement forecast.
- FCF proxy ≠ full FCFF.
- No gross/operating margin schedule in the case dataset.
- Share count frozen; no repurchase forecast.
- Comps table is a multiple placeholder, not a peer set.
- No private dataroom, management model, or insider information.
