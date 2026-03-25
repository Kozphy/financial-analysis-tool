# Usage Examples

This page collects copy-paste examples for the most common demo paths.

## 1. Local Financial Analysis Demo

```bash
financial-analysis-tool --input data/financials.csv --summary-output output/financial/summary.json --chart-output output/charts/financial-trends.svg
```

Expected artifacts:

- `output/financial/summary.json`
- `output/charts/financial-trends.svg`

## 2. Local Quant Backtest Demo

```bash
financial-analysis-tool backtest --prices data/prices.csv --momentum-lookback-days 90 --volatility-lookback-days 90 --rebalance-frequency monthly --backtest-output output/backtests/sample-backtest.json
```

Expected artifact:

- `output/backtests/sample-backtest.json`

## 3. Taiwan Fundamentals From MOPS

```bash
financial-analysis-tool --financial-source mops --mops-company-id 2330 --mops-start-year 2024 --mops-end-year 2025 --mops-seasons 1,2,3,4 --cache-dir .cache/financial-analysis-tool --summary-output output/financial/mops-2330-summary.json --chart-output output/charts/mops-2330-trends.svg
```

## 4. Taiwan Equities Backtest From TWSE

```bash
financial-analysis-tool backtest --price-source twse --twse-stock-nos 2330,2317,2454 --start-date 2025-01-01 --end-date 2025-12-31 --momentum-lookback-days 126 --volatility-lookback-days 63 --rebalance-frequency monthly --benchmark-alignment strict --periods-per-year 252 --parallelism 8 --cache-dir .cache/financial-analysis-tool --backtest-output output/backtests/twse-top2.json
```

## 5. Taiwan Equities Backtest From TEJ

```bash
financial-analysis-tool backtest --price-source tej --tej-symbols 2330,2317,2454 --tej-api-key YOUR_TEJ_API_KEY --start-date 2025-01-01 --end-date 2025-12-31 --momentum-lookback-days 126 --volatility-lookback-days 63 --rebalance-frequency monthly --periods-per-year 252 --backtest-output output/backtests/tej-top2.json
```

## 6. Crypto Backtest From Binance

```bash
financial-analysis-tool backtest --price-source binance --binance-symbols BTCUSDT,ETHUSDT,BNBUSDT --binance-interval 1d --binance-limit 365 --momentum-lookback-days 90 --volatility-lookback-days 30 --rebalance-frequency weekly --periods-per-year 365 --parallelism 4 --backtest-output output/backtests/binance-weekly.json
```

## 7. Development Loop

Install dev tooling:

```bash
python -m pip install -e .[dev]
```

Run through the package module:

```bash
python -m financial_analysis_tool --help
python -m financial_analysis_tool backtest --prices data/prices.csv --backtest-output output/backtests/module-backtest.json
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

Run coverage:

```bash
coverage run -m unittest discover -s tests -v
coverage report
```

If `make` is available:

```bash
make install-dev
make test
make run-financial
make run-backtest
make docker-financial
make docker-backtest
```
