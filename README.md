# Financial Analysis Tool

A Python project for analyzing company financial performance and running lightweight quant backtests with structured financial data.

## Overview

This repository is organized into separate financial, quant, service, and CLI layers. It supports:

- financial statement analysis from CSV
- financial statement ingestion from Taiwan MOPS
- SVG trend reporting for company fundamentals
- factor-based quant backtesting from local CSV data
- Binance Spot kline ingestion for exchange-backed backtests
- TWSE daily price ingestion for Taiwan-listed stocks
- TEJ daily price ingestion for Taiwan market datasets

## Quick Start

Run the financial analysis workflow:

```bash
python main.py
```

Run a MOPS-backed financial pull for a Taiwan company:

```bash
python main.py --financial-source mops --mops-company-id 2330 --mops-start-year 2024 --mops-end-year 2025 --summary-output output/mops-summary.json
```

Run the quant backtest from the bundled CSV sample:

```bash
python main.py backtest --prices data/prices.csv --backtest-output output/backtest.json
```

Run a Binance-backed backtest:

```bash
python main.py backtest --price-source binance --binance-symbols BTCUSDT,ETHUSDT,BNBUSDT --binance-interval 1d --binance-limit 365 --periods-per-year 365 --backtest-output output/backtest-binance.json
```

Run a TWSE-backed backtest:

```bash
python main.py backtest --price-source twse --twse-stock-nos 2330,2317,2454 --start-date 2025-01-01 --end-date 2025-12-31 --periods-per-year 252 --backtest-output output/backtest-twse.json
```

Run a TEJ-backed backtest:

```bash
python main.py backtest --price-source tej --tej-symbols 2330,2317,2454 --tej-api-key YOUR_TEJ_API_KEY --start-date 2025-01-01 --end-date 2025-12-31 --periods-per-year 252 --backtest-output output/backtest-tej.json
```

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

## Project Structure

```text
financial-analysis-tool/
|-- README.md
|-- requirements.txt
|-- pyproject.toml
|-- main.py
|-- .gitignore
|-- data/
|   |-- financials.csv
|   `-- prices.csv
|-- output/
|   `-- .gitkeep
|-- src/
|   `-- financial_analysis_tool/
|       |-- __init__.py
|       |-- __main__.py
|       |-- cli/
|       |   |-- __init__.py
|       |   |-- app.py
|       |   |-- financial_cli.py
|       |   `-- backtest_cli.py
|       |-- core/
|       |   |-- __init__.py
|       |   |-- config.py
|       |   |-- exceptions.py
|       |   |-- io.py
|       |   |-- types.py
|       |   `-- utils.py
|       |-- financial/
|       |   |-- __init__.py
|       |   |-- loader.py
|       |   |-- models.py
|       |   |-- metrics.py
|       |   |-- reporting.py
|       |   `-- visualization.py
|       |-- quant/
|       |   |-- __init__.py
|       |   |-- loader.py
|       |   |-- models.py
|       |   |-- factors.py
|       |   |-- strategy.py
|       |   |-- portfolio.py
|       |   |-- backtest.py
|       |   `-- reporting.py
|       `-- services/
|           |-- __init__.py
|           |-- financial_service.py
|           `-- backtest_service.py
|-- tests/
|   |-- test_financial_metrics.py
|   |-- test_financial_reporting.py
|   |-- test_quant_factors.py
|   |-- test_quant_strategy.py
|   |-- test_backtest.py
|   `-- test_cli.py
`-- docs/
    |-- architecture.md
    `-- examples.md
```

## Notes

- The project uses Python's standard library only.
- Binance integration uses the Spot REST kline endpoint and is intended for exchange market-data pulls before factor calculation and backtesting.
- MOPS integration uses the public quarterly financial statement summary endpoint and filters the requested company from the returned tables.
- TWSE integration uses the public `exchangeReport/STOCK_DAY` endpoint and works with TWSE-listed stock numbers.
- TEJ integration uses the official REST datatable API and requires a valid TEJ API key or `TEJ_API_KEY` environment variable.
- The bundled sample backtest uses monthly price data, a 3-period momentum lookback, and a 3-period volatility window.
