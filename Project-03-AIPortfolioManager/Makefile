.PHONY: install test lint demo api

install:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src tests

demo:
	portfolio-demo

api:
	uvicorn ai_portfolio.api:app --reload

