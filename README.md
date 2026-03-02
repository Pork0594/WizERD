# WizERD

[![CI](https://github.com/Pork0594/WizERD/actions/workflows/ci.yml/badge.svg)](https://github.com/Pork0594/WizERD/actions) [![PyPI Version](https://img.shields.io/pypi/v/wizerd.svg)](https://pypi.org/project/wizerd/) [![Python Versions](https://img.shields.io/pypi/pyversions/wizerd.svg)](https://pypi.org/project/wizerd/) [![License](https://img.shields.io/pypi/l/wizerd.svg)](https://github.com/Pork0594/WizERD/blob/main/LICENSE)

Generate beautiful, readable ER diagrams from PostgreSQL schema dumps. Point it at a pg_dump file, run the CLI, get an SVG. No manual arrangement, no GUI, no interaction required.

![WizERD Output](docs/images/sample-hero-image.png)

## Quick Start

```bash
pip install wizerd
wizerd generate schema.sql -o diagram.svg
```

Point it at a PostgreSQL `pg_dump` or `pg_dumpall` output.

## Why WizERD?

Most ER diagram generators produce unreadable "line messes" with large schemas. WizERD uses the ELK layout algorithm to minimize edge crossings and guarantees zero table overlap — your diagrams stay navigable at any scale.

- **Zero overlap** — tables never render on top of each other
- **Smart routing** — orthogonal edges with minimal crossings
- **13 built-in themes** — dark, light, monochrome, and more
- **Flexible spacing** — compact, standard, or spacious
- **Column details** — shows data types, PK/FK markers
- **CI-friendly** — runs unattended in pipelines or scripts

## Installation

### Requirements

- Python 3.9+
- Node.js 18+ (for the ELK layout engine)

### From PyPI

```bash
pip install wizerd
```

Node.js is required for the layout engine. Without it, WizERD falls back to a simple vertical stack.

### From Source

```bash
git clone https://github.com/Pork0594/WizERD.git
cd WizERD
pip install -e ".[dev]"
cd wizerd/layout && npm ci && cd ../..
```

## Usage

### Basic

```bash
wizerd generate schema.sql -o diagram.svg
```

### Themes

```bash
wizerd themes  # List all themes
wizerd generate schema.sql -t light
wizerd generate schema.sql -t dracula
wizerd generate schema.sql -t nord
```

### Spacing

```bash
wizerd generate schema.sql -w compact    # Tight layout
wizerd generate schema.sql -w standard   # Default
wizerd generate schema.sql -w spacious   # More breathing room
```

### Show Foreign Key Names

```bash
wizerd generate schema.sql -o diagram.svg --show-edge-labels
```

### Color by Relationship Target

```bash
wizerd generate schema.sql -o diagram.svg --color-by-trunk
```

### Debugging

Parse and inspect your schema:

```bash
wizerd parse schema.sql > schema.json
```

### Configuration

Create a config file:

```bash
wizerd init            # Creates .wizerd.yaml
wizerd init -t full    # Full template with all options
```

Config precedence (later overrides earlier):

1. Defaults
2. `~/.wizerd.yaml` (home directory)
3. `.wizerd.yaml` (project directory)
4. `--config` file
5. CLI arguments

Environment variables also work:

```bash
export WIZERD_THEME=light
export WIZERD_OUTPUT=diagram.svg
export WIZERD_SPACING_PROFILE=compact
```

Validate your config:

```bash
wizerd validate .wizerd.yaml
```

Show default values:

```bash
wizerd defaults
wizerd defaults --format json
wizerd defaults --format env
```

## Configuration Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output`, `-o` | path | `diagram.svg` | Output file path |
| `--theme`, `-t` | string | `default-dark` | Theme name |
| `--spacing-profile`, `-w` | string | `standard` | Layout density: `compact`, `standard`, `spacious` |
| `--show-edge-labels`, `-l` | bool | `false` | Show FK names on connector lines |
| `--color-by-trunk`, `-e` | bool | `false` | Color edges by FK target table |
| `--config`, `-c` | path | — | Config file path |

## Example Schemas

WizERD ships with example schemas in `dev/dumps/examples/`:

| File | Tables | Description |
|------|--------|-------------|
| `simple_schema.sql` | 2 | Users and posts |
| `schema.sql` | 20+ | Music streaming platform |
| `large_schema.sql` | 50+ | Complex relationships |

## Development

```bash
make install-all   # Set up venv, Python deps, Node.js
make check         # lint + typecheck + tests
make example       # Generate demo diagram
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT — see [LICENSE](LICENSE).
