# Financial Analysis Tool

A Python project for analyzing company financial performance and running lightweight quant backtests with structured financial data.

## Overview

This repository is organized into separate financial, quant, service, and CLI layers. It supports:

- financial statement analysis from CSV
- SVG trend reporting for company fundamentals
- factor-based quant backtesting from local CSV data
- Binance Spot kline ingestion for exchange-backed backtests

## Quick Start

Run the financial analysis workflow:

```bash
python main.py
```

Run the quant backtest from the bundled CSV sample:

```bash
python main.py backtest --prices data/prices.csv --backtest-output output/backtest.json
```

Run a Binance-backed backtest:

```bash
python main.py backtest --price-source binance --binance-symbols BTCUSDT,ETHUSDT,BNBUSDT --binance-interval 1d --binance-limit 365 --periods-per-year 365 --backtest-output output/backtest-binance.json
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
- The bundled sample backtest uses monthly price data, a 3-period momentum lookback, and a 3-period volatility window.
