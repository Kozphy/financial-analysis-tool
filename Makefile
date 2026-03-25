PYTHON ?= python

.PHONY: help install-dev test coverage build run-financial run-backtest docker-financial docker-backtest

help:
	@echo "Available targets:"
	@echo "  install-dev    Install the package in editable mode with dev tools"
	@echo "  test           Run the unit test suite"
	@echo "  coverage       Run the test suite with coverage"
	@echo "  build          Build the package"
	@echo "  run-financial  Run the bundled financial analysis demo"
	@echo "  run-backtest   Run the bundled quant backtest demo"
	@echo "  docker-financial  Run the Docker financial demo"
	@echo "  docker-backtest   Run the Docker backtest demo"

install-dev:
	$(PYTHON) -m pip install -e .[dev]

test:
	$(PYTHON) -m unittest discover -s tests -v

coverage:
	coverage run -m unittest discover -s tests -v
	coverage report

build:
	$(PYTHON) -m build

run-financial:
	$(PYTHON) main.py --summary-output output/financial/summary.json --chart-output output/charts/financial-trends.svg

run-backtest:
	$(PYTHON) main.py backtest --prices data/prices.csv --backtest-output output/backtests/sample-backtest.json

docker-financial:
	docker compose up --build financial

docker-backtest:
	docker compose --profile backtest run --rm backtest
