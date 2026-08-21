.PHONY: install test lint run compose

install:
	python -m pip install -e '.[dev]'

test:
	pytest

lint:
	ruff check src tests

run:
	uvicorn prediction_market_agents.api:app --reload

compose:
	docker compose up --build

