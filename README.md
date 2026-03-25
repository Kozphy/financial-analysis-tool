# Financial Analysis Tool

Portfolio-ready Python CLI for financial statement analysis and lightweight quant backtesting.

This repo is designed to be easy to demo, easy to read in an interview, and straightforward to run locally. It combines structured fundamentals analysis with factor-driven backtests, supports both local CSV workflows and live market-data providers, and keeps the runtime dependency footprint intentionally small.

## What This Repo Shows

- clean separation between CLI, orchestration, financial analysis, quant logic, and provider adapters
- local and remote data ingestion across CSV, MOPS, TWSE, TEJ, and Binance
- deterministic unit tests with saved fixtures for provider parsing
- a backtest engine with explicit factor windows, rebalance semantics, and benchmark alignment
- standard-library-first implementation with editable installs, CI, coverage, and a console entrypoint

## Features

- Analyze company financial performance from structured CSV data
- Fetch Taiwan quarterly fundamentals from MOPS
- Generate JSON summaries and SVG charts for financial trends
- Run cross-sectional momentum and low-volatility backtests
- Pull market data from local CSV, Binance Spot, TWSE, or TEJ
- Cache and retry remote requests for more reliable local development

## Quick Start

Install the project in editable mode:

```bash
python -m pip install -e .[dev]
```

Run the bundled financial analysis sample:

```bash
financial-analysis-tool
```

Run the bundled quant backtest sample:

```bash
financial-analysis-tool backtest
```

If you prefer the repo entrypoint during development:

```bash
python main.py
python main.py backtest
```

Run through the module entrypoint after install:

```bash
python -m financial_analysis_tool
python -m financial_analysis_tool backtest
```

## Common Workflows

Local financial analysis:

```bash
financial-analysis-tool --input data/financials.csv --summary-output output/financial/summary.json --chart-output output/charts/financial-trends.svg
```

Local backtest:

```bash
financial-analysis-tool backtest --prices data/prices.csv --backtest-output output/backtests/sample-backtest.json
```

Taiwan fundamentals from MOPS:

```bash
financial-analysis-tool --financial-source mops --mops-company-id 2330 --mops-start-year 2024 --mops-end-year 2025 --summary-output output/financial/mops-2330-summary.json
```

Taiwan equities from TWSE:

```bash
financial-analysis-tool backtest --price-source twse --twse-stock-nos 2330,2317,2454 --start-date 2025-01-01 --end-date 2025-12-31 --momentum-lookback-days 126 --volatility-lookback-days 63 --rebalance-frequency monthly --periods-per-year 252 --backtest-output output/backtests/twse-top2.json
```

Crypto spot data from Binance:

```bash
financial-analysis-tool backtest --price-source binance --binance-symbols BTCUSDT,ETHUSDT,BNBUSDT --binance-interval 1d --binance-limit 365 --rebalance-frequency weekly --periods-per-year 365 --backtest-output output/backtests/binance-weekly.json
```

More end-to-end examples live in [docs/examples.md](docs/examples.md).

Docker usage lives in [README.Docker.md](README.Docker.md).

## Output Layout

Generated artifacts are organized by purpose:

```text
output/
|-- README.md
|-- financial/
|   `-- *.json
|-- charts/
|   `-- *.svg
|-- backtests/
|   `-- *.json
`-- logs/
    `-- *.log
```

Recommended defaults:

- financial summaries in `output/financial/`
- chart artifacts in `output/charts/`
- backtest reports in `output/backtests/`
- ad hoc logs in `output/logs/`

## Repository Layout

```text
financial-analysis-tool/
|-- data/                      # Sample financial and price datasets
|-- docs/                      # Architecture notes and runnable examples
|-- output/                    # Generated artifacts (kept out of git except placeholders)
|-- src/financial_analysis_tool/
|   |-- cli/                   # Parser construction and command dispatch
|   |-- core/                  # Shared config, I/O, HTTP, logging, exceptions
|   |-- financial/             # Fundamentals analysis and reporting
|   |-- quant/                 # Factors, ranking, portfolio, backtest engine
|   `-- services/              # Workflow orchestration
|-- tests/                     # Unit tests, CLI smoke tests, provider fixtures
|-- main.py                    # Development entrypoint
`-- pyproject.toml             # Packaging and console script definition
```

For a deeper walkthrough, see [docs/architecture.md](docs/architecture.md).

## Developer Experience

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

Run coverage locally:

```bash
coverage run -m unittest discover -s tests -v
coverage report
```

Build the package:

```bash
python -m build
```

If `make` is available, the repo also includes a small [Makefile](Makefile) with common commands such as `make install-dev`, `make test`, and `make run-backtest`.

Docker convenience targets are also available through `make docker-financial` and `make docker-backtest`.

CI is already configured in [.github/workflows/ci.yml](.github/workflows/ci.yml) to run tests, coverage, and packaging checks on push and pull request.

## Interview Talking Points

- The repo separates domain logic from provider adapters, which keeps financial and quant calculations testable without live network calls.
- The backtest engine uses calendar-day factor windows, explicit rebalance frequencies, and benchmark alignment modes instead of row-count assumptions.
- Provider integrations are covered with saved fixtures so remote API parsing can evolve without making the tests flaky.

## License

This project is available under the MIT License. See [LICENSE](LICENSE).
