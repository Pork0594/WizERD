# WizERD

[![CI](https://github.com/Pork0594/WizERD/actions/workflows/ci.yml/badge.svg)](https://github.com/Pork0594/WizERD/actions)
[![PyPI Version](https://img.shields.io/pypi/v/wizerd.svg)](https://pypi.org/project/wizerd/)
[![Python Versions](https://img.shields.io/pypi/pyversions/wizerd.svg)](https://pypi.org/project/wizerd/)
[![License](https://img.shields.io/pypi/l/wizerd.svg)](https://github.com/Pork0594/WizERD/blob/main/LICENSE)

**WizERD** generates beautiful, readable ER diagrams from PostgreSQL schema dumps. Point it at a `pg_dump` file and get a perfectly organized SVG — no manual layout, no line mess, no overlap. Ever.

![WizERD Output](docs/images/sample-hero-image.png)

---

## Why WizERD?

Most ER diagram tools produce unreadable tangles the moment your schema grows past a handful of tables. WizERD uses the [ELK layout engine](https://eclipse.dev/elk/) to guarantee zero overlap and minimize edge crossings at any scale.

- **Zero overlap** — tables never render on top of each other
- **Smart routing** — orthogonal edges with minimal crossings
- **13 built-in themes** — dark, light, monochrome, and more
- **Flexible spacing** — compact, standard, or spacious
- **Comprehensive schema support** — includes tables, views, indexes, and sequences
- **Column details** — shows data types and PK/FK/IDX/SEQ markers
- **CI-friendly** — runs unattended in pipelines or scripts


## Installation

### Requirements

- Python 3.9+
- Node.js 18+ *(used by the ELK layout engine)*

### Homebrew (macOS)

```bash
brew tap Pork0594/WizERD
brew install wizerd
```

### pip

```bash
pip install wizerd
```

### From Source

```bash
git clone https://github.com/Pork0594/WizERD.git
cd WizERD
pip install -e ".[dev]"
cd wizerd/layout && npm ci && cd ../..
```

---

## Quick Start

```bash
wizerd generate schema.sql -o diagram.svg
```

Point it at a `pg_dump` or `pg_dumpall` output and you're done.

---

## Usage

### Generate a Diagram

```bash
wizerd generate schema.sql -o diagram.svg
```

### Themes

WizERD ships with 13 built-in themes.

```bash
# See all available themes
wizerd themes

# Apply a theme
wizerd generate schema.sql -t light
wizerd generate schema.sql -t dracula
wizerd generate schema.sql -t nord
```

### Layout Density

```bash
wizerd generate schema.sql -w compact    # Tight layout
wizerd generate schema.sql -w standard   # Default
wizerd generate schema.sql -w spacious   # More breathing room
```

### Foreign Key Labels

```bash
wizerd generate schema.sql --show-edge-labels
```

### Color by Relationship Target

Highlights edges by which table they point to, making complex schemas easier to trace.

```bash
wizerd generate schema.sql --color-by-trunk
```

### Parse & Inspect

Useful for debugging your schema or piping into other tools.

```bash
wizerd parse schema.sql > schema.json
```

---

## Configuration

### Generate a Config File

```bash
wizerd init             # Creates .wizerd.yaml with common options
wizerd init -t full     # Full template with every available option
```

### Config Precedence

Settings are resolved in this order, with later sources taking priority:

1. Built-in defaults
2. `~/.wizerd.yaml` — home directory global config
3. `.wizerd.yaml` — project directory config
4. `--config <path>` — explicit config file
5. CLI flags — always win

### Environment Variables

```bash
export WIZERD_THEME=light
export WIZERD_OUTPUT=diagram.svg
export WIZERD_SPACING_PROFILE=compact
```

### Validate Your Config

```bash
wizerd validate .wizerd.yaml
```

### Show Defaults

```bash
wizerd defaults
wizerd defaults --format json
wizerd defaults --format env
```

---

## Configuration Reference

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--output` | `-o` | path | `diagram.svg` | Output file path |
| `--theme` | `-t` | string | `default-dark` | Theme name (run `wizerd themes` for options) |
| `--spacing-profile` | `-w` | string | `standard` | Layout density: `compact`, `standard`, `spacious` |
| `--show-edge-labels` | `-l` | bool | `false` | Show FK constraint names on edges |
| `--color-by-trunk` | `-e` | bool | `false` | Color edges by FK target table |
| `--indexes` | — | bool | `false` | Include indexes in the diagram |
| `--views` | — | bool | `false` | Include views as separate nodes |
| `--sequences` | — | bool | `false` | Include sequences for auto-increment columns |
| `--config` | `-c` | path | — | Explicit path to a config file |

---

## Example Schemas

WizERD ships with example schemas in `dev/dumps/examples/`:

| File | Tables | Description |
|---|---|---|
| `simple_schema.sql` | 2 | Users and posts — good for getting started |
| `schema.sql` | 20+ | Music streaming platform |
| `large_schema.sql` | 50+ | Complex multi-domain schema |

---

## Development

```bash
make install-all   # Set up venv, Python deps, and Node.js
make check         # Lint + typecheck + tests
make example       # Generate a demo diagram
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full contribution guidelines.

---

## License

MIT — see [LICENSE](LICENSE).
