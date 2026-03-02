# Examples

This page provides practical examples for common use cases.

## Basic Usage

### Generate SVG from schema

```bash
wizerd generate schema.sql -o diagram.svg
```

### Convert SVG to PNG

WizERD outputs SVG. Convert to PNG using `rsvg-convert` or `cairosvg`:

```bash
# Generate SVG first
wizerd generate schema.sql -o diagram.svg

# Convert to PNG
rsvg-convert -h 800 diagram.svg -o diagram.png
```

### Use a different theme

```bash
wizerd generate schema.sql -o diagram.svg -t light
wizerd generate schema.sql -o diagram.svg -t dracula
wizerd generate schema.sql -o diagram.svg -t ocean
```

## Working with Large Schemas

### Spacious layout for large databases

```bash
wizerd generate large-schema.sql -o large-diagram.svg -w spacious
```

### Compact for quick overview

```bash
wizerd generate schema.sql -o compact.svg -w compact
```

## Relationship Visualization

### Show FK names on edges

```bash
wizerd generate schema.sql -o diagram.svg --show-edge-labels
```

This displays constraint names along the connector lines.

### Color edges by target table

```bash
wizerd generate schema.sql -o diagram.svg --color-by-trunk
```

Each foreign key target gets a unique color, making it easier to trace relationships.

## Configuration Files

### Use a config file

```bash
wizerd generate schema.sql --config my-config.yaml
```

### Create a config file

```bash
# Interactive creation
wizerd init

# From template
wizerd init -t full -o my-config.yaml
```

### Config file example

```yaml
# production-config.yaml
output: erd.svg
theme: dracula
show-edge-labels: true
spacing-profile: spacious
color-by-trunk: true
```

## Environment Variables

### Set defaults via environment

```bash
export WIZERD_THEME=light
export WIZERD_SPACING_PROFILE=spacious
export WIZERD_OUTPUT=diagram.svg

wizerd generate schema.sql
```

### CI/CD usage

```bash
WIZERD_OUTPUT=docs/schema.svg \
WIZERD_THEME=minimal \
WIZERD_SPACING_PROFILE=compact \
  wizerd generate schema.sql
```

## Parsing and Debugging

### View parsed schema as JSON

```bash
wizerd parse schema.sql > schema.json
```

Useful for debugging or integrating with other tools.

### Enable debug logging

```bash
WIZERD_LOG_LEVEL=DEBUG wizerd generate schema.sql -o diagram.svg
```

This shows parser debug logs about skipped statements.

## Theme Combinations

### Professional dark theme

```bash
wizerd generate schema.sql \
  -o diagram.svg \
  -t default-dark \
  -w standard
```

### Print-friendly light theme

```bash
wizerd generate schema.sql \
  -o diagram.svg \
  -t light \
  -w standard \
  --show-edge-labels
```

### High contrast for accessibility

```bash
wizerd generate schema.sql \
  -o diagram.svg \
  -t high-contrast \
  -w spacious
```

### Monochrome for documentation

```bash
wizerd generate schema.sql \
  -o diagram.svg \
  -t minimal
```

## Using Example Schemas

WizERD includes example schemas in `dev/dumps/examples/`:

### Simple (2 tables)

```bash
wizerd generate dev/dumps/examples/simple_schema.sql -o simple.svg
```

### Music Platform (20+ tables)

```bash
wizerd generate dev/dumps/examples/schema.sql -o music.svg
```

### Large Schema (50+ tables)

```bash
wizerd generate dev/dumps/examples/large_schema.sql -o large.svg
```

## Validation

### Validate a config file

```bash
wizerd validate .wizerd.yaml
```

### Validate with schema file

```bash
wizerd validate config.yaml --schema schema.sql
```

## Showing Defaults

### View default configuration

```bash
wizerd defaults
wizerd defaults --format json
wizerd defaults --format env
```

## Common Workflows

### Git pre-commit diagram update

```yaml
# .github/pre-commit-config.yaml
- repo: local
  hooks:
    - id: generate-erd
      name: Generate ER Diagram
      entry: wizerd generate
      args: [schema.sql, -o, docs/erd.svg, -t, minimal]
      files: schema.sql
```

### GitHub Actions

```yaml
name: Update ER Diagram
on:
  pull_request:
    paths:
      - 'schema.sql'
jobs:
  update-diagram:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install wizerd
      - run: wizerd generate schema.sql -o docs/erd.svg
      - run: git config --global user.name "GitHub Actions"
      - run: git config --global user.email "actions@github.com"
      - run: git add docs/erd.svg && git diff --staged --quiet || git commit -m "Update ER diagram"
      - run: git push
```

## Next Steps

- [Configuration](configuration.md) — Full configuration reference
- [CLI Reference](cli-reference.md) — Complete command documentation
- [Themes](themes.md) — Theme gallery
