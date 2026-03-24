# Architecture

This project is organized into clear layers so financial analysis, quant logic, and command-line behavior can evolve independently.

## Layers

- `cli/`: argument parsing and user-facing command dispatch
- `core/`: shared config, exceptions, I/O helpers, and utility functions
- `financial/`: financial statement models, CSV and MOPS loading, metrics, reporting, and visualization
- `quant/`: price loading, Binance/TWSE/TEJ ingestion, factor calculation, portfolio construction, and backtesting
- `services/`: orchestration workflows that connect domain logic to outputs

## Flow

Financial analysis flow:

`cli.financial_cli -> services.financial_service -> financial.loader/metrics/reporting/visualization`

`financial.loader` can pull local CSV data or remote Taiwan MOPS statement summaries before normalizing the records into the shared financial model.

Quant backtest flow:

`cli.backtest_cli -> services.backtest_service -> quant.loader/factors/strategy/portfolio/backtest/reporting`

`quant.loader` can pull local CSV data, Binance spot klines, TWSE daily reports, or TEJ datatable results before handing the normalized prices to the factor and backtest pipeline.
