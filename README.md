# WizERD

<p align="center">
  <a href="https://pypi.org/project/wizerd/">
    <img src="https://img.shields.io/pypi/v/wizerd.svg" alt="PyPI Version">
  </a>
  <a href="https://pypi.org/project/wizerd/">
    <img src="https://img.shields.io/pypi/pyversions/wizerd.svg" alt="Python Versions">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/wizerd.svg" alt="License: MIT">
  </a>
  <a href="https://github.com/Pork0594/wizerd/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/Pork0594/wizerd/ci.yml" alt="CI">
  </a>
</p>

WizERD is a PostgreSQL ER diagram generator that creates beautiful, readable diagrams with zero table overlap and minimal edge crossings.

<p align="center">
  <img src="docs/images/sample-hero-image.png" alt="WizERD Example Output" width="800">
</p>

## Why WizERD?

Most ER diagram generators fail with large databases (100+ tables). They produce overlapping tables and "line messes" that are impossible to parse. WizERD prioritizes visual legibility over compactness, ensuring your diagrams remain navigable regardless of database size.

## Features

- **Zero Overlap** — Tables never render on top of each other
- **Smart Routing** — Minimal relationship line crossovers
- **14 Built-in Themes** — From dark mode to minimal
- **Flexible Spacing** — Compact, standard, or spacious layouts
- **Column Details** — Shows data types, PKs, and FKs
- **Multiple Formats** — SVG and PNG output
- **Flexible Configuration** — YAML, JSON, environment variables, or CLI flags

## Quick Start

```bash
# Install
pip install wizerd

# Generate diagram
wizerd generate schema.sql -o diagram.svg

# Or with export features (PNG)
pip install wizerd[export]
wizerd generate schema.sql -o diagram.png
```

## Installation

See the [Installation Guide](docs/installation.md) for detailed instructions.

### Requirements

- Python 3.9+
- Node.js 18+ (for layout engine)

### From PyPI

```bash
pip install wizerd
pip install wizerd[export]  # For PNG/PDF output
```

### From Source

```bash
git clone https://github.com/Pork0594/wizerd.git
cd wizerd
pip install -r requirements.txt
cd wizerd/layout && npm ci
```

## Usage

### Basic Usage

```bash
wizerd generate schema.sql -o diagram.svg
```

### Themes

```bash
# List available themes
wizerd themes

# Use a different theme
wizerd generate schema.sql -o diagram.svg -t light
wizerd generate schema.sql -o diagram.svg -t dracula
```

### Spacing Profiles

```bash
# Compact for small schemas
wizerd generate schema.sql -o diagram.svg -w compact

# Spacious for large schemas
wizerd generate schema.sql -o diagram.svg -w spacious
```

### Show Foreign Key Labels

```bash
wizerd generate schema.sql -o diagram.svg --show-edge-labels
```

### Color by Relationship Target

```bash
wizerd generate schema.sql -o diagram.svg --color-by-trunk
```

## Configuration

Create a config file:

```bash
wizerd init
```

This creates `.wizerd.yaml`:

```yaml
output: diagram.svg
theme: default-dark
show-edge-labels: false
spacing-profile: standard
color-by-trunk: false
```

See [Configuration](docs/configuration.md) for full details.

## Documentation

- [Getting Started](docs/getting-started.md) — Your first diagram
- [Configuration](docs/configuration.md) — Customization options
- [Themes](docs/themes.md) — All 14 themes with previews
- [Spacing Profiles](docs/spacing-profiles.md) — Layout controls
- [Examples](docs/examples.md) — Practical examples
- [CLI Reference](docs/cli-reference.md) — Complete command reference

## Example Schemas

WizERD includes example schemas:

| File | Tables | Description |
|------|--------|-------------|
| `dev/dumps/examples/simple_schema.sql` | 2 | Users and posts |
| `dev/dumps/examples/schema.sql` | 20+ | Music streaming platform |
| `dev/dumps/examples/large_schema.sql` | 50+ | Complex relationships |

## Project Goals

- Parse large PostgreSQL schemas from dump files
- Build constraint-aware graph layouts optimized for clarity
- Render high-quality SVG diagrams suitable for documentation

## License

MIT License — see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please open an issue or PR at https://github.com/Pork0594/wizerd
