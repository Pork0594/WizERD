# Getting Started

This guide walks through generating your first ER diagram with WizERD.

## Prerequisites

- WizERD installed (see [Installation](installation.md))
- A PostgreSQL schema dump file

## Step 1: Prepare Your Schema

Dump your PostgreSQL database schema:

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

## Step 6: Convert to PNG (optional)

WizERD outputs SVG by default. To convert to PNG, use a tool like `rsvg-convert` or `cairosvg`:

```bash
# Install rsvg-convert (macOS)
brew install librsvg

# Convert SVG to PNG
rsvg-convert -h 800 diagram.svg -o diagram.png
```

## What the Diagram Shows

Each table in the diagram includes:

- **Header** — Table name with schema prefix (if applicable)
- **Columns** — Column name, data type, and constraints
- **PK marker** — Primary key indicator (yellow star)
- **FK marker** — Foreign key indicator (blue circle)
- **IDX marker** — Index indicator (purple diamond, if enabled)
- **SEQ marker** — Sequence indicator (green square, if enabled)
- **Relationships** — Connectors showing foreign key relationships

## Next Steps

- [Configuration](configuration.md) — Use config files for repeatable setups
- [Themes](themes.md) — Explore all 13 themes
- [Examples](examples.md) — More command examples
- [CLI Reference](cli-reference.md) — Complete command documentation
