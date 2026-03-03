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
| `--indexes` | `WIZERD_INDEXES` |
| `--views` | `WIZERD_VIEWS` |
| `--sequences` | `WIZERD_SEQUENCES` |
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
| `theme` | string or dict | `default-dark` | Theme name (string) or full theme definition (dict) |
| `theme-overrides` | dict | — | Partial theme customizations (colors, typography, etc.) |
| `show-edge-labels` | boolean | `false` | Show FK names on connectors |
| `spacing-profile` | string | `compact, standard, spacious` | Spacing preset |
| `color-by-trunk` | boolean | `false` | Color edges by FK target |
| `indexes` | boolean | `false` | Include indexes in the diagram |
| `views` | boolean | `false` | Include views as separate nodes |
| `sequences` | boolean | `false` | Include sequences for auto-increment columns |

### Custom Spacing Keys (advanced)

If you need finer control than the `spacing-profile` presets provide, you can set `spacing` in your config file. These keys map directly to the ELK layout knobs and control horizontal/vertical gaps, component separation, and canvas margins.

| Key | Type | Default (standard) | Description |
|-----|------|--------------------:|-------------|
| `spacing.column_gap` | number | `360.0` | Horizontal gap between table columns (controls X-axis spacing) |
| `spacing.row_gap` | number | `225.0` | Vertical gap between tables within a column (controls Y-axis spacing) |
| `spacing.component_gap` | number | `570.0` | Gap between disconnected groups of tables |
| `spacing.edge_to_node_gap` | number | `51.0` | Clearance between edges and table boxes |
| `spacing.edge_gap` | number | `39.0` | Clearance between parallel edges (lane spacing) |
| `spacing.margin` | number | `72.0` | Canvas margin applied on both axes |

Example (YAML):

```yaml
# .wizerd.yaml
spacing:
  column_gap: 200.0
  edge_gap: 18.0
  margin: 32.0
```

Use the canonical keys above when setting `spacing` in your config file or via environment variables. Legacy keys are not supported.

## Theme Configuration

You can customize the visual appearance of your diagrams by defining a custom theme or overriding specific properties of a built-in theme.

- **`theme`**: Accepts a built-in theme name (e.g., `default-dark`) or a full theme definition object.
- **`theme-overrides`**: Modifies specific values of the currently selected theme without defining everything from scratch.

Both `theme` (when defined as an object) and `theme-overrides` share the same property tree. Use the dot notation below when writing your YAML/JSON config.

### Colors

| Key | Type | Description |
|-----|------|-------------|
| `theme.colors.canvas_background` | string | Background color of the entire diagram |
| `theme.colors.table_background` | string | Background color of the table body |
| `theme.colors.table_border` | string | Border color of the table |
| `theme.colors.table_header_bg` | string | Background color of the table header |
| `theme.colors.table_header_text` | string | Text color for the table name |
| `theme.colors.table_body_text` | string | Text color for column names and types |
| `theme.colors.table_secondary_text`| string | Text color for secondary information (like type size) |
| `theme.colors.zebra_row` | string | Background color for alternating rows |
| `theme.colors.pk_marker` | string | Color of the Primary Key (PK) marker |
| `theme.colors.fk_marker` | string | Color of the Foreign Key (FK) marker |
| `theme.colors.idx_marker` | string | Color of the Index (IDX) marker |
| `theme.colors.seq_marker` | string | Color of the Sequence (SEQ) marker |

### Typography

| Key | Type | Description |
|-----|------|-------------|
| `theme.typography.font_family` | string | CSS font-family string (e.g., `'Inter', sans-serif`) |
| `theme.typography.font_size_header` | number | Font size for the table name |
| `theme.typography.font_size_body` | number | Font size for column names and types |
| `theme.typography.font_size_secondary` | number | Font size for secondary text |
| `theme.typography.font_size_edge_label`| number | Font size for relationship labels on edges |
| `theme.typography.char_pixel_width` | number | Estimated pixel width of a character (used for layout calculations) |

### Dimensions

| Key | Type | Description |
|-----|------|-------------|
| `theme.dimensions.canvas_padding` | number | Padding around the edge of the canvas |
| `theme.dimensions.header_height` | number | Height of the table header |
| `theme.dimensions.row_height` | number | Height of each column row |
| `theme.dimensions.corner_radius` | number | Border radius for the table corners |
| `theme.dimensions.table_stroke_width` | number | Width of the table border stroke |
| `theme.dimensions.table_min_width` | number | Minimum width of a table |
| `theme.dimensions.table_max_width` | number | Maximum width of a table before truncating text |
| `theme.dimensions.table_side_padding` | number | Horizontal padding inside the table rows |
| `theme.dimensions.marker_size` | number | Size of the PK/FK/IDX/SEQ markers |

### Edges

| Key | Type | Description |
|-----|------|-------------|
| `theme.edges.edge_color` | string | Default color for relationship lines |
| `theme.edges.edge_secondary` | string | Secondary color for relationships |
| `theme.edges.edge_width` | number | Stroke width of relationship lines |
| `theme.edges.edge_corner_radius` | number | Radius for the orthogonal bends in the lines |
| `theme.edges.edge_color_palette` | list[str] | List of hex colors used when `color-by-trunk` is enabled |
| `theme.edges.arrow_marker_id` | string | SVG marker ID for the edge arrow |

### Example

```yaml
# .wizerd.yaml
theme: default-dark
theme-overrides:
  colors:
    canvas_background: "#1a1a2e"
    table_header_bg: "#e94560"
  typography:
    font_family: "'JetBrains Mono', monospace"
```

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
indexes: false
views: false
sequences: false
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
indexes: false
views: false
sequences: false
```

## Next Steps

- [Themes](themes.md) — Customize the visual appearance
- [Spacing Profiles](spacing-profiles.md) — Control layout density
- [CLI Reference](cli-reference.md) — Complete command reference
