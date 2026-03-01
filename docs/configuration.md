# Configuration

WizERD offers flexible configuration through multiple sources with a clear precedence order.

## Configuration Precedence

Configuration is resolved in this order (later sources override earlier):

1. Built-in defaults
2. Home config (`~/.wizerd.yaml` or `~/.wizerd.json`)
3. Project config (`.wizerd.yaml` next to input file or in CWD)
4. Explicit `--config` file
5. Environment variables (`WIZERD_*`)
6. CLI flags

## Config File Format

WizERD supports both YAML and JSON config files.

### YAML Example

```yaml
# .wizerd.yaml
output: my-diagram.svg
theme: light
show-edge-labels: true
spacing-profile: spacious
color-by-trunk: true
```

### JSON Example

```json
{
  "output": "my-diagram.svg",
  "theme": "light",
  "show-edge-labels": true,
  "spacing-profile": "spacious",
  "color-by-trunk": true
}
```

## Creating a Config File

Use the built-in init command:

```bash
# Create default config
wizerd init

# Create with minimal options
wizerd init -t minimal

# Create with all options documented
wizerd init -t full

# Overwrite existing
wizerd init -f
```

## Environment Variables

All CLI options map to environment variables:

| CLI Option | Environment Variable |
|------------|----------------------|
| `--output` | `WIZERD_OUTPUT` |
| `--theme` | `WIZERD_THEME` |
| `--show-edge-labels` | `WIZERD_SHOW_EDGE_LABELS` |
| `--spacing-profile` | `WIZERD_SPACING_PROFILE` |
| `--color-by-trunk` | `WIZERD_COLOR_BY_TRUNK` |
| `--config` | `WIZERD_CONFIG` |

### Example

```bash
export WIZERD_OUTPUT=diagram.svg
export WIZERD_THEME=dracula
export WIZERD_SPACING_PROFILE=spacious

wizerd generate schema.sql
```

## Config Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output` | string | `diagram.svg` | Output file path |
| `theme` | string | `default-dark` | Theme name |
| `show-edge-labels` | boolean | `false` | Show FK names on connectors |
| `spacing-profile` | string | `compact, standard, spacious` | Spacing preset |
| `color-by-trunk` | boolean | `false` | Color edges by FK target |

## Validating Configuration

Check if your config is valid without generating a diagram:

```bash
wizerd validate .wizerd.yaml
wizerd validate config.yaml --schema schema.sql
```

## Showing Defaults

View the default configuration values:

```bash
# YAML format (default)
wizerd defaults

# JSON format
wizerd defaults --format json

# Environment variables format
wizerd defaults --format env
```

Output:

```yaml
output: diagram.svg
show-edge-labels: false
spacing-profile: standard
color-by-trunk: false
theme: default-dark
edge-color-mode: single
```

## Config Templates

### Minimal

```yaml
output: diagram.svg
theme: default-dark
```

### Standard

```yaml
output: diagram.svg
theme: default-dark
show-edge-labels: false
spacing-profile: standard
```

### Full

```yaml
output: diagram.svg
theme: default-dark
show-edge-labels: false
spacing-profile: standard
color-by-trunk: false
```

## Next Steps

- [Themes](themes.md) — Customize the visual appearance
- [Spacing Profiles](spacing-profiles.md) — Control layout density
- [CLI Reference](cli-reference.md) — Complete command reference
