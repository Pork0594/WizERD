# Getting Started

This guide walks through generating your first ER diagram with WizERD.

## Prerequisites

- WizERD installed (see [Installation](installation.md))
- A PostgreSQL schema dump file

## Step 1: Prepare Your Schema

If you don't have a schema file, you can use the included example:

```bash
# The music streaming platform schema (20+ tables)
cp dev/dumps/examples/schema.sql ./my-schema.sql
```

Or dump your actual PostgreSQL database:

```bash
pg_dump --schema-only mydatabase > schema.sql
```

## Step 2: Generate Your First Diagram

```bash
wizerd generate schema.sql -o diagram.svg
```

This creates `diagram.svg` using the default dark theme.

## Step 3: View the Output

Open `diagram.svg` in any browser or image viewer:

```bash
# macOS
open diagram.svg

# Linux
xdg-open diagram.svg

# Windows
start diagram.svg
```

## Step 4: Try Different Themes

List available themes:

```bash
wizerd themes
```

Generate with a different theme:

```bash
# Light theme
wizerd generate schema.sql -o diagram-light.svg -t light

# Dracula theme
wizerd generate schema.sql -o diagram-dracula.svg -t dracula

# Minimal black & white
wizerd generate schema.sql -o diagram-minimal.svg -t minimal
```

## Step 5: Customize Spacing

Try different spacing profiles:

```bash
# Compact - tighter layout for smaller schemas
wizerd generate schema.sql -o diagram-compact.svg -w compact

# Spacious - more room for complex schemas
wizerd generate schema.sql -o diagram-spacious.svg -w spacious
```

## Step 6: Export to PNG

If you installed with export features:

```bash
wizerd generate schema.sql -o diagram.png
```

## Example: Music Streaming Platform

Let's walk through a complete example using the included music schema:

```bash
# Parse and inspect the schema first
wizerd parse dev/dumps/examples/schema.sql | head -100

# Generate default diagram
wizerd generate dev/dumps/examples/schema.sql -o music-erd.svg

# Generate with light theme and edge labels
wizerd generate dev/dumps/examples/schema.sql \
  -o music-erd-light.svg \
  -t light \
  --show-edge-labels

# Generate with color by FK target
wizerd generate dev/dumps/examples/schema.sql \
  -o music-erd-colored.svg \
  -t default-dark \
  --color-by-trunk
```

## What the Diagram Shows

Each table in the diagram includes:

- **Header** — Table name with schema prefix (if applicable)
- **Columns** — Column name, data type, and constraints
- **PK marker** — Primary key indicator (yellow star)
- **FK marker** — Foreign key indicator (blue circle)
- **Relationships** — Connectors showing foreign key relationships

## Next Steps

- [Configuration](configuration.md) — Use config files for repeatable setups
- [Themes](themes.md) — Explore all 14 themes
- [Examples](examples.md) — More command examples
- [CLI Reference](cli-reference.md) — Complete command documentation
