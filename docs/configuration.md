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

Spacing environment variables for fine-grained control:

| Env Var | Config Key |
|---------|------------|
| `WIZERD_SPACING_COLUMN_GAP` | `spacing.column_gap` |
| `WIZERD_SPACING_ROW_GAP` | `spacing.row_gap` |
| `WIZERD_SPACING_COMPONENT_GAP` | `spacing.component_gap` |
| `WIZERD_SPACING_EDGE_TO_NODE_GAP` | `spacing.edge_to_node_gap` |
| `WIZERD_SPACING_EDGE_GAP` | `spacing.edge_gap` |
| `WIZERD_SPACING_MARGIN` | `spacing.margin` |

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
| `theme` | string or dict | `default-dark` | Theme name (string) or [full theme definition](themes.md#custom-themes) (dict) |
| `theme-overrides` | dict | — | Partial theme customizations (colors, typography, etc.) |
| `show-edge-labels` | boolean | `false` | Show FK names on connectors |
| `spacing-profile` | string | `compact, standard, spacious` | Spacing preset |
| `color-by-trunk` | boolean | `false` | Color edges by FK target |

### Custom Spacing Keys (advanced)

If you need finer control than the `spacing-profile` presets provide, you can set `spacing` in your config file. These keys map directly to the ELK layout knobs and control horizontal/vertical gaps, component separation, and canvas margins.

| Key | Type | Default (standard) | Description |
|-----|------|--------------------:|-------------|
| `column_gap` | number | `360.0` | Horizontal gap between table columns (controls X-axis spacing) |
| `row_gap` | number | `225.0` | Vertical gap between tables within a column (controls Y-axis spacing) |
| `component_gap` | number | `570.0` | Gap between disconnected groups of tables |
| `edge_to_node_gap` | number | `51.0` | Clearance between edges and table boxes |
| `edge_gap` | number | `39.0` | Clearance between parallel edges (lane spacing) |
| `margin` | number | `72.0` | Canvas margin applied on both axes |

Example (YAML):

```yaml
# .wizerd.yaml
spacing:
  column_gap: 200.0
  edge_gap: 18.0
  margin: 32.0
```

Use the canonical keys above when setting `spacing` in your config file or via environment variables. Legacy keys are not supported.

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
