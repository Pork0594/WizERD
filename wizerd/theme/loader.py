"""Theme loading utilities for custom themes and CLI overrides."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from wizerd.theme import Theme, ThemeRegistry

logger = logging.getLogger(__name__)


def _ensure_builtin_themes_loaded() -> None:
    """Ensure built-in themes are loaded."""
    if not ThemeRegistry.names():
        ThemeRegistry.load_builtin_themes()


def get_builtin_theme(name: str) -> Theme:
    """Get a built-in theme by name.

    Args:
        name: Theme name (e.g., 'default-dark', 'light', 'monochrome')

    Returns:
        The Theme instance

    Raises:
        ValueError: If theme name is not found
    """
    _ensure_builtin_themes_loaded()
    return ThemeRegistry.get(name)


def list_builtin_themes() -> dict[str, Theme]:
    """List all available built-in themes.

    Returns:
        Dictionary of theme name to Theme
    """
    _ensure_builtin_themes_loaded()
    return ThemeRegistry.list_themes()


def load_theme_from_file(path: Path) -> Theme:
    """Load a theme from a JSON or YAML file.

    Args:
        path: Path to JSON theme file

    Returns:
        The loaded Theme

    Raises:
        ValueError: If file cannot be read or parsed
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()

        if path.suffix.lower() in {".yaml", ".yml"}:
            data = yaml.safe_load(raw)
        else:
            data = json.loads(raw)
    except FileNotFoundError as exc:
        raise ValueError(f"Theme file not found: {path}") from exc
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ValueError(f"Invalid JSON in theme file: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("Theme file must contain a mapping")

    return Theme.from_dict(data)


def _looks_like_file_path(value: str) -> bool:
    """Check if a string looks like a file path."""
    if not value:
        return False
    return (
        value.startswith("/")
        or value.startswith("./")
        or value.startswith("../")
        or value.endswith(".json")
        or ":" in value.split("/")[0]
    )


def load_theme(
    theme_name: str | None = None,
    *,
    theme_inline: dict[str, Any] | None = None,
    theme_overrides: dict[str, Any] | None = None,
) -> Theme:
    """Load a theme from various sources with optional overrides.

    Resolution order:
    1. Use inline theme definition (if provided)
    2. Load from file when theme_name looks like a path
    3. Load built-in theme by name (if provided)
    4. Fallback to the default theme

    Args:
        theme_name: Name of built-in theme (e.g., 'default-dark') or path to theme file
        theme_inline: Inline theme definition (same schema as theme JSON)
        theme_overrides: Dictionary of theme values to override

    Returns:
        The resolved Theme

    Raises:
        ValueError: If referenced theme files are missing or inline definitions are invalid
    """
    theme: Theme

    if theme_inline is not None:
        theme = Theme.from_dict(theme_inline)
    elif theme_name:
        if _looks_like_file_path(theme_name):
            theme_file_path = Path(theme_name)
            if theme_file_path.exists():
                theme = load_theme_from_file(theme_file_path)
            else:
                raise ValueError(f"Theme file not found: {theme_file_path}")
        else:
            theme = get_builtin_theme(theme_name)
    else:
        theme = get_builtin_theme("default-dark")

    if theme_overrides:
        theme = theme.merge(theme_overrides)

    return theme


def export_theme(theme: Theme, output_path: Path) -> None:
    """Export a theme to a JSON file.

    Args:
        theme: Theme to export
        output_path: Path to write JSON file
    """
    data = theme.to_dict()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


COLOR_OVERRIDE_MAPPING: dict[str, tuple[str, str]] = {
    "canvas_background": ("colors", "canvas_background"),
    "table_background": ("colors", "table_background"),
    "table_border": ("colors", "table_border"),
    "table_header_bg": ("colors", "table_header_bg"),
    "table_header_text": ("colors", "table_header_text"),
    "table_body_text": ("colors", "table_body_text"),
    "table_secondary_text": ("colors", "table_secondary_text"),
    "zebra_row": ("colors", "zebra_row"),
    "pk_marker": ("colors", "pk_marker"),
    "fk_marker": ("colors", "fk_marker"),
    "edge_color": ("edges", "edge_color"),
    "edge_secondary": ("edges", "edge_secondary"),
    "edge_width": ("edges", "edge_width"),
    "edge_trunk_width": ("edges", "edge_trunk_width"),
    "edge_corner_radius": ("edges", "edge_corner_radius"),
    "font_family": ("typography", "font_family"),
    "font_size_header": ("typography", "font_size_header"),
    "font_size_body": ("typography", "font_size_body"),
    "font_size_secondary": ("typography", "font_size_secondary"),
    "font_size_edge_label": ("typography", "font_size_edge_label"),
    "char_pixel_width": ("typography", "char_pixel_width"),
    "canvas_padding": ("dimensions", "canvas_padding"),
    "header_height": ("dimensions", "header_height"),
    "row_height": ("dimensions", "row_height"),
    "corner_radius": ("dimensions", "corner_radius"),
    "table_stroke_width": ("dimensions", "table_stroke_width"),
}


def cli_overrides_to_dict(
    canvas_bg: str | None = None,
    table_bg: str | None = None,
    header_bg: str | None = None,
    header_text: str | None = None,
    body_text: str | None = None,
    secondary_text: str | None = None,
    zebra: str | None = None,
    pk_color: str | None = None,
    fk_color: str | None = None,
    edge_color: str | None = None,
    edge_secondary: str | None = None,
    font_family: str | None = None,
    font_size_edge: float | None = None,
) -> dict[str, Any]:
    """Convert CLI color/typography overrides to a nested dict.

    This helper converts flat CLI options like --canvas-bg into the
    nested structure expected by Theme.merge().

    Args:
        CLI override arguments

    Returns:
        Nested dictionary for theme merging
    """
    overrides: dict[str, Any] = {}

    mapping: dict[str, Any] = {
        "canvas_background": canvas_bg,
        "table_background": table_bg,
        "table_header_bg": header_bg,
        "table_header_text": header_text,
        "table_body_text": body_text,
        "table_secondary_text": secondary_text,
        "zebra_row": zebra,
        "pk_marker": pk_color,
        "fk_marker": fk_color,
        "edge_color": edge_color,
        "edge_secondary": edge_secondary,
        "font_family": font_family,
        "font_size_edge_label": font_size_edge,
    }

    for key, value in mapping.items():
        if value is not None:
            if key in COLOR_OVERRIDE_MAPPING:
                section, field = COLOR_OVERRIDE_MAPPING[key]
                if section not in overrides:
                    overrides[section] = {}
                overrides[section][field] = value
            else:
                overrides[key] = value

    return overrides
