## Docker

Automated container publishing is documented in [docs/deployment_automation.md](C:/Users/Zixsa/Kozphy/financial-analysis-tool/docs/deployment_automation.md).

Build and run the financial analysis workflow:

```bash
docker compose up --build financial
```

The container writes:

- `output/reports/financial_summary.json`
- `output/reports/executive_summary.md`
- `output/charts/profitability_trends.svg`
- `output/charts/financial_position_trends.svg`

To run the image directly:

```bash
docker build -t financial-analysis-tool .
docker run --rm -v "${PWD}/output:/app/output" financial-analysis-tool
```
