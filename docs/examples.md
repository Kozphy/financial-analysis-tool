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
