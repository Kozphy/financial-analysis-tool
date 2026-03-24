# Examples

## Financial Analysis

Run the default financial analysis:

```bash
python main.py
```

Run with explicit outputs:

```bash
python main.py --input data/financials.csv --summary-output output/summary.json --chart-output output/charts.svg
```

Run against Taiwan MOPS:

```bash
python main.py --financial-source mops --mops-company-id 2330 --mops-start-year 2024 --mops-end-year 2025 --mops-seasons 1,2,3,4 --summary-output output/mops-summary.json
```

## Quant Backtest From CSV

```bash
python main.py backtest --prices data/prices.csv --backtest-output output/backtest.json
```

## Quant Backtest From Binance

Daily Binance spot data:

```bash
python main.py backtest --price-source binance --binance-symbols BTCUSDT,ETHUSDT,BNBUSDT --binance-interval 1d --binance-limit 365 --periods-per-year 365 --backtest-output output/backtest-binance.json
```

Bounded Binance pull:

```bash
python main.py backtest --price-source binance --binance-symbols BTCUSDT,ETHUSDT --binance-interval 1d --start-date 2025-01-01 --end-date 2025-12-31 --periods-per-year 365
```

## Quant Backtest From TWSE

```bash
python main.py backtest --price-source twse --twse-stock-nos 2330,2317,2454 --start-date 2025-01-01 --end-date 2025-12-31 --periods-per-year 252 --backtest-output output/backtest-twse.json
```

## Quant Backtest From TEJ

```bash
python main.py backtest --price-source tej --tej-symbols 2330,2317,2454 --tej-api-key YOUR_TEJ_API_KEY --start-date 2025-01-01 --end-date 2025-12-31 --periods-per-year 252 --backtest-output output/backtest-tej.json
```
