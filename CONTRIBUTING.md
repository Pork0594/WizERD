# Contributing to WizERD

WizERD transforms PostgreSQL schema dumps into clean SVG ER diagrams. Contributions are welcome.

## Quick Start

```bash
make install-all   # Create venv, install deps, set up Node.js
make check         # Run lint, typecheck, and tests
make example       # Generate a demo diagram
```

## Development Setup

```bash
# Or step-by-step:
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
cd wizerd/layout && npm ci && cd ../..
```

Node.js 18+ is required for the ELK layout engine. Without it, WizERD falls back to a simple vertical layout.

## Running Tests

```bash
make test
# or directly:
pytest
```

## Code Quality

```bash
make check    # lint + typecheck + test
make lint     # ruff check
make format   # ruff format
make typecheck
```

## Project Structure

- `wizerd/cli.py` — CLI entry point using Typer
- `wizerd/parser/ddl_parser.py` — PostgreSQL DDL parser (CREATE TABLE, ALTER TABLE)
- `wizerd/pipeline.py` — Orchestrates parsing → layout → rendering
- `wizerd/layout/engine.py` — ELK layout integration + fallback engine
- `wizerd/render/svg_renderer.py` — SVG generation
- `wizerd/theme/` — Theme system with built-in presets
- `wizerd/config_loader.py` — Multi-source config (file, env, CLI)

## Key Concepts

**Pipeline**: Schema file → DDLParser → SchemaModel → LayoutGraph → ELK → PositionedDiagram → SVGRenderer → SVG

**Configuration**: CLI args override config files, which override defaults. Config loads from: defaults → `~/.wizerd.yaml` → project `.wizerd.yaml` → `--config` file → CLI args. Environment variables (`WIZERD_*`) sit between config files and CLI.

**Themes**: Define colors, typography, and dimensions. Themes can be built-in, loaded from JSON/YAML, or specified inline. See `wizerd/theme/presets.json` for the schema.

**Layout**: The ELK engine produces orthogonal edges with optional edge labels. A simple fallback stacks tables vertically when Node.js is unavailable.

## Adding a New Theme

1. Edit `wizerd/theme/presets.json`
2. Add a theme object with `name`, `description`, `is_dark`, and nested `colors`, `typography`, `dimensions`, `edges` objects

Test locally:
```bash
wizerd generate schema.sql -o out.svg -t your-new-theme
```

## Adding a New Spacing Profile

Edit `wizerd/layout/spacing.py` — add an entry to `SpacingProfile._PRESETS`.

## Submitting Changes

1. Fork and create a feature branch
2. Add tests for new functionality
3. Run `make check`
4. Submit a PR using conventional commits: `feat:`, `fix:`, `docs:`, `BREAKING CHANGE:`

## Other Useful Commands

```bash
make example        # Generate demo diagram
make docs-images    # Regenerate documentation images
make build          # Build Python package
make build-binary   # Build standalone binary
make clean          # Remove build artifacts
```
