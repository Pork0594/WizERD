"""Renderer-facing theme representation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from wizerd.theme.palette import EDGE_COLOR_PALETTE


@dataclass
class RendererTheme:
    """Theme configuration consumed by the SVG renderer."""

    name: str = "default-dark"
    description: str = "Default dark theme with deep blue background"
    is_dark: bool = True
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
    edge_color: str = "#7dd3fc"
    edge_secondary: str = "#164e63"
    edge_color_palette: Tuple[str, ...] = tuple(EDGE_COLOR_PALETTE)
    font_family: str = "'Sora', 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif"
    font_size_header: float = 15.0
    font_size_body: float = 12.0
    font_size_secondary: float = 11.0
    font_size_edge_label: float = 11.0
    char_pixel_width: float = 6.5
    arrow_marker_id: str = "fk-arrow"
    canvas_padding: float = 80.0
    header_height: float = 44.0
    row_height: float = 30.0
    corner_radius: float = 12.0
    table_stroke_width: float = 1.2
    table_min_width: float = 220.0
    table_max_width: float = 460.0
    table_side_padding: float = 28.0
    edge_width: float = 2.0
    edge_trunk_width: float = 3.0
    edge_corner_radius: float = 20.0
