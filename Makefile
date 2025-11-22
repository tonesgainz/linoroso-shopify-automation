.PHONY: help install test coverage lint format type-check security clean run run-manual pre-commit all

# Default target
help:
	@echo "Linoroso Shopify Automation - Available Commands"
	@echo "================================================="
	@echo ""
	@echo "Installation & Setup:"
	@echo "  make install          Install all dependencies"
	@echo "  make install-dev      Install dependencies + dev tools"
	@echo "  make setup            Complete setup (install + pre-commit)"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-verbose     Run tests with verbose output"
	@echo "  make test-fast        Run tests without coverage"
	@echo "  make coverage         Run tests with HTML coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run all linters (flake8)"
	@echo "  make format           Format code (black + isort)"
	@echo "  make format-check     Check formatting without changes"
	@echo "  make type-check       Run type checker (mypy)"
	@echo "  make security         Run security checks (bandit)"
	@echo "  make pre-commit       Run all pre-commit hooks"
	@echo "  make quality          Run all quality checks"
	@echo ""
	@echo "Running the Application:"
	@echo "  make run              Start the automation scheduler"
	@echo "  make run-content      Generate daily content"
	@echo "  make run-seo          Run SEO audit"
	@echo "  make run-optimize     Optimize products"
	@echo "  make run-strategy     Generate SEO strategy report"
	@echo "  make run-all          Run all tasks once"
	@echo ""
	@echo "Cleaning:"
	@echo "  make clean            Remove build artifacts and caches"
	@echo "  make clean-test       Remove test artifacts"
	@echo "  make clean-all        Remove all generated files"

# Installation
install:
	pip install -r requirements.txt

install-dev: install
	pip install pre-commit black isort flake8 mypy bandit safety

setup: install-dev
	pre-commit install
	@echo "✅ Setup complete! Don't forget to configure .env"

# Testing
test:
	pytest

test-verbose:
	pytest -v

test-fast:
	pytest --no-cov

coverage:
	pytest --cov=. --cov-report=html --cov-report=term-missing
	@echo "📊 Coverage report generated in htmlcov/index.html"

# Code Quality
lint:
	@echo "Running flake8..."
	flake8 . --count --show-source --statistics

format:
	@echo "Formatting with black..."
	black . --line-length=100
	@echo "Sorting imports with isort..."
	isort . --profile black --line-length 100

format-check:
	@echo "Checking format with black..."
	black . --line-length=100 --check
	@echo "Checking imports with isort..."
	isort . --profile black --line-length 100 --check

type-check:
	@echo "Running mypy type checker..."
	mypy . --ignore-missing-imports --no-strict-optional

security:
	@echo "Running bandit security scanner..."
	bandit -r . -ll -i
	@echo "Checking dependencies with safety..."
	safety check --ignore 70612 || true

pre-commit:
	pre-commit run --all-files

quality: format-check lint type-check security
	@echo "✅ All quality checks passed!"

all: quality test
	@echo "✅ All checks and tests passed!"

# Running the application
run:
	python main.py --mode scheduler

run-content:
	python main.py --mode manual --task content

run-seo:
	python main.py --mode manual --task seo_audit

run-optimize:
	python main.py --mode manual --task product_optimization

run-strategy:
	python main.py --mode manual --task strategy

run-all:
	python main.py --mode manual --task all

# Individual module runs
run-content-engine:
	python content_engine.py

run-seo-engine:
	python seo_engine.py

run-optimizer:
	python optimizer.py

run-batch:
	python batch_generate.py

# Cleaning
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/
	rm -rf dist/

clean-test:
	@echo "Cleaning test artifacts..."
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f coverage.xml

clean-all: clean clean-test
	@echo "Cleaning all generated files..."
	rm -rf logs/
	rm -rf data/social_posts/
	rm -rf reports/
	@echo "✅ All clean!"

# Development helpers
init-env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file from .env.example"; \
		echo "⚠️  Please edit .env with your API keys"; \
	else \
		echo "⚠️  .env already exists, skipping..."; \
	fi

check-env:
	@echo "Checking environment configuration..."
	@python -c "from settings import config; print('✅ Configuration loaded successfully')" || \
		echo "❌ Configuration error - check your .env file"

# Quick development workflow
dev: format lint test
	@echo "✅ Development checks complete!"

# CI/CD simulation
ci: quality coverage
	@echo "✅ CI checks complete!"
