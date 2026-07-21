.PHONY: help sync run run-historic test lint format clean

help:
	@echo "Targets:"
	@echo "  sync         Install/sync project dependencies with uv"
	@echo "  run          Run the forecaster, writing CSV output to stdout"
	@echo "  run-historic Run the forecaster in --historic mode"
	@echo "  test         Run the test suite"
	@echo "  lint         Run ruff check"
	@echo "  format       Run ruff format"
	@echo "  clean        Remove caches and generated output"

sync:
	uv sync

run:
	uv run src/main.py

run-historic:
	uv run src/main.py --historic --progress_bar

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

clean:
	rm -rf .ruff_cache .pytest_cache dspf_output
	find . -type d -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} +
