### Building and running the analysis container

Build and run the sample analysis workflow with:

`docker compose up --build financial`

The container runs the CLI against `data/financials.csv` and writes:

- `output/financial/summary.json`
- `output/charts/financial-trends.svg`

Run the bundled quant demo with:

`docker compose --profile backtest run --rm backtest`

That writes:

- `output/backtests/backtest.json`

The `output/` directory is mounted from the host so the generated files remain available after the container exits.

### Running a one-off Docker command

You can also build and run the image directly:

`docker build -t financial-analysis-tool .`

`docker run --rm -v "${PWD}/output:/app/output" financial-analysis-tool`
