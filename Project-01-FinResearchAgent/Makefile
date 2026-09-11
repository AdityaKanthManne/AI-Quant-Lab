.PHONY: install test lint run research

install:
	python -m pip install -e '.[dev,live]'

test:
	pytest

lint:
	ruff check .

run:
	uvicorn fin_research.api.app:create_app --factory --reload

research:
	python main.py --ticker AMD

