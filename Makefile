.PHONY: all setup test lint format check clean install install-dev build publish

# Default target
all: setup lint test

# Setup development environment
setup:
	uv sync --extra dev

# Run tests
test:
	uv run pytest tests/ -v

# Run all linting and type checking
lint: format-check lint-check type-check

# Format code
format:
	uv run ruff format .

# Check formatting
format-check:
	uv run ruff check . --fix --diff --exit-zero

# Run linting
lint-check:
	uv run ruff check .

# Run type checking
type-check:
	uv run mypy src/

# Clean up
clean:
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build package
build: clean
	uv build

# Install package locally
install:
	uv sync

# Install development dependencies
install-dev:
	uv sync --extra dev

# Export requirements
requirements:
	uv export > requirements.txt
	uv export --extra dev > requirements-dev.txt

# Run the server
run:
	uv run python -m mockllm

# Help target
help:
	@echo "Available targets:"
	@echo "  all          : Run setup, lint, and test"
	@echo "  setup        : Set up development environment with uv"
	@echo "  test         : Run tests"
	@echo "  lint         : Run all code quality checks"
	@echo "  format       : Format code with black and isort"
	@echo "  format-check : Check code formatting"
	@echo "  lint-check   : Run ruff linter"
	@echo "  type-check   : Run mypy type checker"
	@echo "  clean        : Clean up build artifacts"
	@echo "  build        : Build package"
	@echo "  install      : Install package with uv"
	@echo "  install-dev  : Install package with development dependencies"
	@echo "  requirements : Export requirements.txt files"
	@echo "  run          : Run the server"