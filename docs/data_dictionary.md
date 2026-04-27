# Data Dictionary

This project uses two CSV datasets:

1. Financial statement data for ratio analysis
2. ESG portfolio data for sustainability and risk analysis

## Financial Dataset

File: `data/financials.csv`

Purpose:
- provide a compact, interview-friendly company dataset for profitability, liquidity, and leverage analysis

Required columns:

| Column | Type | Description |
| --- | --- | --- |
| `period` | string | Reporting period in `YYYY-Qn` format, for example `2025-Q4` |
| `revenue` | float | Total revenue for the reporting period |
| `cost_of_revenue` | float | Direct cost associated with delivering revenue |
| `operating_expenses` | float | Operating expenses excluding direct cost of revenue |
| `net_income` | float | Net income after operating and non-operating effects |
| `current_assets` | float | Current assets used to calculate liquidity |
| `current_liabilities` | float | Current liabilities used to calculate liquidity |
| `total_assets` | float | Total assets used to calculate leverage |
| `total_liabilities` | float | Total liabilities used to calculate leverage |

Derived metrics:
- revenue growth
- gross margin
- operating margin
- net margin
- current ratio
- debt ratio

Assumptions:
- period labels must use quarterly format
- numeric fields are already currency-consistent
- each row represents one reporting period for the same company

## ESG Dataset

File: `data/esg_metrics.csv`

Purpose:
- simulate an investee portfolio dataset used to assess transition risk, ESG quality, and sector exposure

Required columns:

| Column | Type | Description |
| --- | --- | --- |
| `company` | string | Portfolio company name |
| `sector` | string | Sector label used for sector-level summaries |
| `year` | integer | Reporting year |
| `revenue_musd` | float | Revenue in USD millions |
| `scope1_emissions_tco2e` | float | Scope 1 emissions in tons of CO2 equivalent |
| `scope2_emissions_tco2e` | float | Scope 2 emissions in tons of CO2 equivalent |
| `esg_score` | float | Composite ESG score |
| `environment_score` | float | Environmental pillar score |
| `social_score` | float | Social pillar score |
| `governance_score` | float | Governance pillar score |
| `renewable_energy_pct` | float | Share of renewable energy consumption |
| `green_capex_pct` | float | Share of capital expenditure considered green |
| `board_independence_pct` | float | Share of independent directors |
| `women_board_pct` | float | Share of women on the board |
| `safety_incidents` | float | Count of workplace safety incidents |
| `controversy_count` | float | Count of public controversies or adverse events |

Derived fields created during cleaning:
- `total_emissions_tco2e`
- `carbon_intensity`
- `emissions_change_pct`
- `esg_score_change`
- `{field}_imputed` audit flags for selected imputed ESG columns
- `{field}_imputation_source` labels such as `company_history`, `sector_median`, or `dataset_median`
- `imputed_field_count`
- `imputation_applied`

Cleaning rules:
- duplicate `company` and `year` rows are dropped, keeping the last row
- invalid numeric values are coerced to null
- negative values in non-negative fields are set to null
- selected fields are imputed using company history, then sector medians, then dataset medians
- selected imputed fields are flagged with audit columns in the cleaned dataset export

Important interpretation note:
- ESG imputation is designed for a portfolio project and educational analysis
- it is not a substitute for production-grade source governance or audited ESG controls
