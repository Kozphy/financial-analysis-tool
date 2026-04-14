PYTHON ?= python

.PHONY: help install-dev install-ui test coverage build run streamlit docker

help:
	@echo "Available targets:"
	@echo "  install-dev    Install the package in editable mode with dev tools"
	@echo "  install-ui     Install the optional Streamlit UI dependencies"
	@echo "  test           Run the unit test suite"
	@echo "  coverage       Run the test suite with coverage"
	@echo "  build          Build the package"
	@echo "  run            Run the bundled financial analysis demo"
	@echo "  streamlit      Launch the Streamlit dashboard"
	@echo "  docker         Run the Docker financial demo"

install-dev:
	$(PYTHON) -m pip install -e .[dev]

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

streamlit:
	$(PYTHON) -m streamlit run streamlit_app.py

docker:
	docker compose up --build financial
