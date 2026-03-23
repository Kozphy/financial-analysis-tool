### Building and running the analysis container

Build and run the sample analysis workflow with:

`docker compose up --build`

The container runs the CLI against `data/financials.csv` and writes:

- `output/summary.json`
- `output/charts.svg`

The `output/` directory is mounted from the host so the generated files remain available after the container exits.

### Running a one-off Docker command

You can also build and run the image directly:

`docker build -t financial-analysis-tool .`

`docker run --rm -v "${PWD}/output:/app/output" financial-analysis-tool`
