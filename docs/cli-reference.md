# CLI Reference

Complete reference for all WizERD commands and options.

## Commands

### generate

Generate an ER diagram from a PostgreSQL schema dump.

```bash
wizerd generate <schema> [options]
wizerd g <schema> [options]
wizerd render <schema> [options]
wizerd r <schema> [options]
```

**Arguments:**
- `schema` — Path to PostgreSQL schema dump (.sql file) [required]

**Options:**
- `-o, --output PATH` — Output diagram path (default: diagram.svg)
- `-l, --show-edge-labels` — Render FK names along connector lines
- `-w, --spacing-profile [compact|standard|spacious]` — Spacing preset (default: standard)
- `-e, --color-by-trunk` — Use unique color per FK target
- `--indexes` — Include indexes in the diagram
- `--views` — Include views as separate nodes in the diagram
- `--sequences` — Include sequences for auto-increment columns in the diagram
- `-t, --theme TEXT` — Built-in theme name
- `-c, --config PATH` — Path to config file (YAML or JSON)

**Examples:**

```bash
# Basic usage
wizerd generate schema.sql -o diagram.svg

# Light theme with edge labels
wizerd generate schema.sql -o diagram.svg -t light --show-edge-labels

# Using config file
wizerd generate schema.sql --config my-config.yaml
```

---

### parse

Parse a PostgreSQL schema and print JSON representation.

```bash
wizerd parse <schema>
wizerd p <schema>
```

**Arguments:**
- `schema` — Path to PostgreSQL schema dump (.sql file) [required]

**Examples:**

```bash
# Parse and view
wizerd parse schema.sql

# Parse to JSON file
wizerd parse schema.sql > schema.json

# View parsed structure
wizerd parse schema.sql | jq '.tables[0]'
```

---

### themes

List all available themes.

```bash
wizerd themes
wizerd t
```

**Examples:**

```bash
wizerd themes
```

Output:
```
Available themes:
  default-dark (dark) - Default dark theme with deep blue background
  dracula (dark) - Dracula color palette theme
  light (light) - Clean light theme with white background
  ...
```

---

### init

Create a config file with default values.

```bash
wizerd init [options]
```

**Options:**
- `-o, --output PATH` — Path where to create the config file (default: .wizerd.yaml)
- `-t, --template [default|minimal|full]` — Template to use (default: default)
- `-f, --force` — Overwrite existing config file

**Examples:**

```bash
# Create default config
wizerd init

# Create with full options
wizerd init -t full -o config-full.yaml

# Overwrite existing
wizerd init -f
```

---

### validate

Validate a config file without generating a diagram.

```bash
wizerd validate <config_file> [options]
```

**Arguments:**
- `config_file` — Path to config file to validate [required]

**Options:**
- `-s, --schema PATH` — Also validate against a schema file

**Examples:**

```bash
# Validate config
wizerd validate .wizerd.yaml

# Validate with schema
wizerd validate config.yaml --schema schema.sql
```

---

### defaults

Show default configuration values.

```bash
wizerd defaults [options]
```

**Options:**
- `-f, --format [yaml|json|env]` — Output format (default: yaml)

**Examples:**

```bash
# YAML format
wizerd defaults

# JSON format
wizerd defaults --format json

# Environment variables
wizerd defaults --format env
```

---

## Global Options

### Logging

Set `WIZERD_LOG_LEVEL` environment variable:

```bash
WIZERD_LOG_LEVEL=DEBUG wizerd generate schema.sql
```

Levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`

### Version

Show the installed WizERD version and exit. This option is eager and can be used without a subcommand.

```bash
# Print version
wizerd --version
# or
wizerd -v
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (invalid input, config error, etc.) |

## Configuration Precedence

When options are specified in multiple places, this order applies:

1. Built-in defaults
2. Home config (`~/.wizerd.yaml`)
3. Project config (`.wizerd.yaml`)
4. Explicit `--config` file
5. Environment variables
6. CLI flags

## Aliases

| Command | Aliases |
|---------|---------|
| generate | g, render, r |
| parse | p |
| themes | t |

## Next Steps

- [Configuration](configuration.md) — Configuration guide
- [Themes](themes.md) — Theme gallery
- [Spacing Profiles](spacing-profiles.md) — Layout options
- [Examples](examples.md) — Practical examples
