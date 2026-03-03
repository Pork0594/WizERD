"""Theme system for WizERD diagrams."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from wizerd.theme.palette import EDGE_COLOR_PALETTE
from wizerd.theme.renderer_theme import RendererTheme


@dataclass
class ThemeTypography:
    """Typography settings that affect layout calculations."""

    font_family: str = "'Sora', 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif"
    font_size_header: float = 15.0
    font_size_body: float = 12.0
    font_size_secondary: float = 11.0
    font_size_edge_label: float = 11.0
    char_pixel_width: float = 6.5


@dataclass
class ThemeDimensions:
    """Dimension settings that affect layout calculations."""

    canvas_padding: float = 80.0
    header_height: float = 44.0
    row_height: float = 30.0
    corner_radius: float = 12.0
    table_stroke_width: float = 1.2
    table_min_width: float = 220.0
    table_max_width: float = 460.0
    table_side_padding: float = 28.0
    marker_size: float = 10.0


@dataclass
class ThemeEdgeStyling:
    """Edge styling configuration."""

    edge_color: str = "#7dd3fc"
    edge_secondary: str = "#164e63"
    edge_width: float = 2.0
    edge_corner_radius: float = 20.0
    edge_color_palette: tuple[str, ...] = field(default_factory=lambda: tuple(EDGE_COLOR_PALETTE))
    arrow_marker_id: str = "fk-arrow"


@dataclass
class ThemeColors:
    """Color palette for the theme."""

    canvas_background: str = "#0f172a"
    table_background: str = "#0b1120"
    table_border: str = "#1d283a"
    table_header_bg: str = "#1e1b4b"
    table_header_text: str = "#f8fafc"
    table_body_text: str = "#cbd5f5"
    table_secondary_text: str = "#94a3b8"
    zebra_row: str = "#101b2d"
    pk_marker: str = "#fbbf24"
    fk_marker: str = "#38bdf8"
    idx_marker: str = "#a78bfa"
    seq_marker: str = "#34d399"


@dataclass
class Theme:
    """Complete theme configuration for WizERD diagrams."""

    name: str = "default-dark"
    description: str = "Default dark theme with deep blue background"
    is_dark: bool = True

    colors: ThemeColors = field(default_factory=ThemeColors)
    typography: ThemeTypography = field(default_factory=ThemeTypography)
    dimensions: ThemeDimensions = field(default_factory=ThemeDimensions)
    edges: ThemeEdgeStyling = field(default_factory=ThemeEdgeStyling)

    def to_renderer_theme(self) -> RendererTheme:
        """Convert to RendererTheme for SVG rendering."""
        return RendererTheme(
            name=self.name,
            description=self.description,
            is_dark=self.is_dark,
            canvas_background=self.colors.canvas_background,
            table_background=self.colors.table_background,
            table_border=self.colors.table_border,
            table_header_bg=self.colors.table_header_bg,
            table_header_text=self.colors.table_header_text,
            table_body_text=self.colors.table_body_text,
            table_secondary_text=self.colors.table_secondary_text,
            zebra_row=self.colors.zebra_row,
            pk_marker=self.colors.pk_marker,
            fk_marker=self.colors.fk_marker,
            idx_marker=self.colors.idx_marker,
            seq_marker=self.colors.seq_marker,
            edge_color=self.edges.edge_color,
            edge_secondary=self.edges.edge_secondary,
            edge_color_palette=self.edges.edge_color_palette,
            font_family=self.typography.font_family,
            font_size_header=self.typography.font_size_header,
            font_size_body=self.typography.font_size_body,
            font_size_secondary=self.typography.font_size_secondary,
            font_size_edge_label=self.typography.font_size_edge_label,
            char_pixel_width=self.typography.char_pixel_width,
            arrow_marker_id=self.edges.arrow_marker_id,
            canvas_padding=self.dimensions.canvas_padding,
            header_height=self.dimensions.header_height,
            row_height=self.dimensions.row_height,
            corner_radius=self.dimensions.corner_radius,
            table_stroke_width=self.dimensions.table_stroke_width,
            table_side_padding=self.dimensions.table_side_padding,
            marker_size=self.dimensions.marker_size,
            edge_width=self.edges.edge_width,
            edge_corner_radius=self.edges.edge_corner_radius,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "is_dark": self.is_dark,
            "colors": {
                "canvas_background": self.colors.canvas_background,
                "table_background": self.colors.table_background,
                "table_border": self.colors.table_border,
                "table_header_bg": self.colors.table_header_bg,
                "table_header_text": self.colors.table_header_text,
                "table_body_text": self.colors.table_body_text,
                "table_secondary_text": self.colors.table_secondary_text,
                "zebra_row": self.colors.zebra_row,
                "pk_marker": self.colors.pk_marker,
                "fk_marker": self.colors.fk_marker,
                "idx_marker": self.colors.idx_marker,
                "seq_marker": self.colors.seq_marker,
            },
            "typography": {
                "font_family": self.typography.font_family,
                "font_size_header": self.typography.font_size_header,
                "font_size_body": self.typography.font_size_body,
                "font_size_secondary": self.typography.font_size_secondary,
                "font_size_edge_label": self.typography.font_size_edge_label,
                "char_pixel_width": self.typography.char_pixel_width,
            },
            "dimensions": {
                "canvas_padding": self.dimensions.canvas_padding,
                "header_height": self.dimensions.header_height,
                "row_height": self.dimensions.row_height,
                "corner_radius": self.dimensions.corner_radius,
                "table_stroke_width": self.dimensions.table_stroke_width,
                "table_min_width": self.dimensions.table_min_width,
                "table_max_width": self.dimensions.table_max_width,
                "table_side_padding": self.dimensions.table_side_padding,
                "marker_size": self.dimensions.marker_size,
            },
            "edges": {
                "edge_color": self.edges.edge_color,
                "edge_secondary": self.edges.edge_secondary,
                "edge_width": self.edges.edge_width,
                "edge_corner_radius": self.edges.edge_corner_radius,
                "edge_color_palette": list(self.edges.edge_color_palette),
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Theme:
        """Create theme from dictionary."""
        colors_data = data.get("colors", {})
        colors = ThemeColors(
            canvas_background=colors_data.get("canvas_background", ThemeColors().canvas_background),
            table_background=colors_data.get("table_background", ThemeColors().table_background),
            table_border=colors_data.get("table_border", ThemeColors().table_border),
            table_header_bg=colors_data.get("table_header_bg", ThemeColors().table_header_bg),
            table_header_text=colors_data.get("table_header_text", ThemeColors().table_header_text),
            table_body_text=colors_data.get("table_body_text", ThemeColors().table_body_text),
            table_secondary_text=colors_data.get(
                "table_secondary_text", ThemeColors().table_secondary_text
            ),
            zebra_row=colors_data.get("zebra_row", ThemeColors().zebra_row),
            pk_marker=colors_data.get("pk_marker", ThemeColors().pk_marker),
            fk_marker=colors_data.get("fk_marker", ThemeColors().fk_marker),
            idx_marker=colors_data.get("idx_marker", ThemeColors().idx_marker),
            seq_marker=colors_data.get("seq_marker", ThemeColors().seq_marker),
        )

        typ_data = data.get("typography", {})
        typography = ThemeTypography(
            font_family=typ_data.get("font_family", ThemeTypography().font_family),
            font_size_header=typ_data.get("font_size_header", ThemeTypography().font_size_header),
            font_size_body=typ_data.get("font_size_body", ThemeTypography().font_size_body),
            font_size_secondary=typ_data.get(
                "font_size_secondary", ThemeTypography().font_size_secondary
            ),
            font_size_edge_label=typ_data.get(
                "font_size_edge_label", ThemeTypography().font_size_edge_label
            ),
            char_pixel_width=typ_data.get("char_pixel_width", ThemeTypography().char_pixel_width),
        )

        dim_data = data.get("dimensions", {})
        dimensions = ThemeDimensions(
            canvas_padding=dim_data.get("canvas_padding", ThemeDimensions().canvas_padding),
            header_height=dim_data.get("header_height", ThemeDimensions().header_height),
            row_height=dim_data.get("row_height", ThemeDimensions().row_height),
            corner_radius=dim_data.get("corner_radius", ThemeDimensions().corner_radius),
            table_stroke_width=dim_data.get(
                "table_stroke_width", ThemeDimensions().table_stroke_width
            ),
            table_min_width=dim_data.get("table_min_width", ThemeDimensions().table_min_width),
            table_max_width=dim_data.get("table_max_width", ThemeDimensions().table_max_width),
            table_side_padding=dim_data.get(
                "table_side_padding", ThemeDimensions().table_side_padding
            ),
            marker_size=dim_data.get("marker_size", ThemeDimensions().marker_size)
        )

        edge_data = data.get("edges", {})
        edges = ThemeEdgeStyling(
            edge_color=edge_data.get("edge_color", ThemeEdgeStyling().edge_color),
            edge_secondary=edge_data.get("edge_secondary", ThemeEdgeStyling().edge_secondary),
            edge_width=edge_data.get("edge_width", ThemeEdgeStyling().edge_width),
            edge_corner_radius=edge_data.get(
                "edge_corner_radius", ThemeEdgeStyling().edge_corner_radius
            ),
            edge_color_palette=tuple(
                edge_data.get("edge_color_palette", list(ThemeEdgeStyling().edge_color_palette))
            ),
        )

        return cls(
            name=data.get("name", "custom"),
            description=data.get("description", "Custom theme"),
            is_dark=data.get("is_dark", True),
            colors=colors,
            typography=typography,
            dimensions=dimensions,
            edges=edges,
        )

    def merge(self, overrides: Dict[str, Any]) -> Theme:
        """Merge overrides into this theme and return a new theme."""
        base_dict = self.to_dict()

        def validate_keys(
            template: Dict[str, Any], data: Dict[str, Any], path: str = "theme"
        ) -> None:
            for key, value in data.items():
                if key not in template:
                    raise ValueError(f"Unknown theme override key '{path}.{key}'")
                template_value = template[key]
                if isinstance(value, dict):
                    if not isinstance(template_value, dict):
                        raise ValueError(
                            f"Cannot override nested key '{path}.{key}' with a non-dict value"
                        )
                    validate_keys(template_value, value, f"{path}.{key}")

        validate_keys(base_dict, overrides)

        def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
            result = base.copy()
            for key, value in override.items():
                if isinstance(value, dict) and isinstance(result.get(key), dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        merged = deep_merge(base_dict, overrides)
        return Theme.from_dict(merged)


class ThemeRegistry:
    """Registry of built-in themes."""

    _themes: Dict[str, Theme] = {}

    @classmethod
    def register(cls, theme: Theme) -> None:
        """Register a theme."""
        cls._themes[theme.name] = theme

    @classmethod
    def get(cls, name: str) -> Theme:
        """Get a theme by name."""
        if name not in cls._themes:
            raise ValueError(
                f"Unknown theme '{name}'. Available themes: {', '.join(cls._themes.keys())}"
            )
        return cls._themes[name]

    @classmethod
    def list_themes(cls) -> Dict[str, Theme]:
        """List all registered themes."""
        return cls._themes.copy()

    @classmethod
    def names(cls) -> list[str]:
        """List all theme names."""
        return list(cls._themes.keys())

    @classmethod
    def load_builtin_themes(cls) -> None:
        """Load all built-in themes."""
        from wizerd.theme.presets import load_presets

        for theme in load_presets():
            cls.register(theme)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered themes (primarily for tests)."""
        cls._themes.clear()
