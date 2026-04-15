PYTHON ?= python

.PHONY: help install-dev install-esg install-ui test coverage build run run-esg streamlit docker

help:
	@echo "Available targets:"
	@echo "  install-dev    Install the package in editable mode with dev tools"
	@echo "  install-esg    Install the ESG analysis dependencies"
	@echo "  install-ui     Install the optional Streamlit UI dependencies"
	@echo "  test           Run the unit test suite"
	@echo "  coverage       Run the test suite with coverage"
	@echo "  build          Build the package"
	@echo "  run            Run the bundled financial analysis demo"
	@echo "  run-esg        Run the bundled ESG analysis demo"
	@echo "  streamlit      Launch the Streamlit dashboard"
	@echo "  docker         Run the Docker financial demo"

install-dev:
	$(PYTHON) -m pip install -e .[dev]

install-esg:
	$(PYTHON) -m pip install -e .[esg]

install-ui:
	$(PYTHON) -m pip install -e .[ui]

test:
	$(PYTHON) -m unittest discover -s tests -v

coverage:
	$(PYTHON) -m coverage run -m unittest discover -s tests -v
	$(PYTHON) -m coverage report

build:
	$(PYTHON) -m build

run:
	$(PYTHON) main.py

run-esg:
	$(PYTHON) main.py esg

streamlit:
	$(PYTHON) -m streamlit run streamlit_app.py

docker:
	docker compose up --build financial
