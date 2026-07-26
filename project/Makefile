.PHONY: install test lint format format-check typecheck check

# Install the package and locked development dependencies via uv.
install:
	uv sync

# Run the pytest suite (includes coverage via pyproject.toml addopts).
test:
	uv run pytest

# Lint the project with Ruff (no file modifications).
lint:
	uv run ruff check .

# Apply Ruff formatting to source and tests.
format:
	uv run ruff format .

# Verify Ruff formatting without writing changes.
format-check:
	uv run ruff format --check .

# Run mypy static type checks over src and tests.
typecheck:
	uv run mypy src tests

# Run all non-mutating quality checks (format, lint, types, tests).
check: format-check lint typecheck test
