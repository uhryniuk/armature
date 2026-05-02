.PHONY: test

test:
	uv sync --extra dev --extra test
	uv run pytest
