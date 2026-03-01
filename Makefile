.PHONY: venv install test lint format clean example node-install build build-binary release check docs-images docs-clean

# Default target
.DEFAULT_GOAL := help

help:
	@echo "WizERD Makefile"
	@echo ""
	@echo "Development:"
	@echo "  make venv       - Create virtual environment"
	@echo "  make install    - Install wizerd in development mode"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linter"
	@echo "  make format     - Format code"
	@echo "  make example    - Run example diagram generation"
	@echo ""
	@echo "Building:"
	@echo "  make build         - Build Python package (sdist + wheel)"
	@echo "  make build-binary  - Build standalone binary"
	@echo "  make check         - Run all checks (lint, typecheck, test)"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs-images   - Generate all documentation sample images"
	@echo "  make docs-clean    - Remove generated documentation images"
	@echo ""
	@echo "Releasing (via semantic-release):"
	@echo "  make release       - Run semantic-release locally"
	@echo ""
	@echo "Note: Push to main to trigger automatic release via GitHub Actions."
	@echo "      Use conventional commits: feat:, fix:, docs:, BREAKING CHANGE:"
	@echo ""
	@echo "Cleaning:"
	@echo "  make clean       - Remove build artifacts"
	@echo "  make deep-clean  - Remove all generated files"

venv:
	python3 -m venv .venv

install: venv
	. .venv/bin/activate && pip install -e ".[dev]"

node-install:
	cd wizerd/layout && npm ci

install-all: venv node-install install
	@echo "Development environment ready!"

test:
	. .venv/bin/activate && pytest -v

lint:
	. .venv/bin/activate && ruff check .

format:
	. .venv/bin/activate && ruff format .

typecheck:
	. .venv/bin/activate && mypy wizerd

check: lint typecheck test

example: install node-install
	. .venv/bin/activate && python3 wizerd.py generate dev/dumps/examples/schema.sql -o dev/outputs/demo.svg

build:
	. .venv/bin/activate && python3 -m build

build-binary:
	. .venv/bin/activate && pyinstaller wizerd.spec --name wizerd-$$(uname -s | tr '[:upper:]' '[:lower:]')-$$(uname -m)

release:
	. .venv/bin/activate && semantic-release publish

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

deep-clean: clean
	git clean -fdX

docs-images: install node-install
	python3 scripts/generate_docs_images.py

docs-clean:
	rm -f docs/images/sample-*.svg docs/images/sample-*.png

.PHONY: help venv install test lint format clean example node-install build build-binary release check docs-images docs-clean
