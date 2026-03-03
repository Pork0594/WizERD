"""SVG rendering primitives."""

from __future__ import annotations

import logging
import math
import re
from pathlib import Path
from typing import Any, List, Sequence, Tuple

import svgwrite

from wizerd.graph.layout_graph import PositionedDiagram, PositionedEdge, PositionedNode
from wizerd.model.schema import SchemaModel, Table, View
from wizerd.theme.renderer_theme import RendererTheme

logger = logging.getLogger(__name__)


class SVGRenderer:
    """Production-grade SVG renderer for positioned diagrams."""

    def __init__(
        self,
        theme: RendererTheme | None = None,
        *,
        show_edge_labels: bool = False,
        trunk_colors: dict[tuple[str, str | None], str] | None = None,
        show_indexes: bool = False,
        show_views: bool = False,
        show_sequences: bool = False,
    ) -> None:
        """Store rendering options; heavy lifting happens inside `render`."""
        self.theme = theme or RendererTheme()
        self.show_edge_labels = show_edge_labels
        self.trunk_colors = trunk_colors or {}
        self.show_indexes = show_indexes
        self.show_views = show_views
        self.show_sequences = show_sequences
        # Default arrow marker id (sanitized for use in DOM)
        self._arrow_marker_id = self._sanitize_dom_id(self.theme.arrow_marker_id)
        # Map of color -> marker id for quick lookup when coloring arrows per-edge
        self._color_marker_map: dict[str, str] = {}

    @staticmethod
    def _sanitize_dom_id(value: str) -> str:
        """Return a DOM-safe identifier for use in clip paths and markers."""
        sanitized = re.sub(r"[^a-zA-Z0-9_-]", "-", value)
        return sanitized or "wizerd-id"

    def render(self, diagram: PositionedDiagram, schema: SchemaModel, output_path: Path) -> None:
        """Draw the positioned diagram to disk, respecting the active theme."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        width, height = self._compute_canvas(diagram)
        dwg = svgwrite.Drawing(
            str(output_path),
            size=(f"{width}px", f"{height}px"),
            profile="full",
            viewBox=f"0 0 {width} {height}",
        )

        self._define_markers(dwg)
        dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill=self.theme.canvas_background))

        edges_layer = dwg.add(dwg.g(id="edges"))
        nodes_layer = dwg.add(dwg.g(id="tables"))

        self._draw_edges(dwg, edges_layer, diagram)

        for node in sorted(diagram.nodes.values(), key=lambda n: (n.y, n.x)):
            is_view = getattr(node, "is_view", False)
            if is_view:
                view = schema.views.get(node.table_name)
                self._draw_table(dwg, nodes_layer, node, view)
            else:
                table = schema.tables.get(node.table_name)
                self._draw_table(dwg, nodes_layer, node, table)

        dwg.save(pretty=True)

    def _define_markers(self, dwg: svgwrite.Drawing) -> None:
        """Register arrow markers once so multiple edges can reference them."""
        # Create a default marker using the theme's edge color
        default_marker = dwg.marker(
            id=self._arrow_marker_id,
            insert=(10, 5),
            size=(10, 10),
            orient="auto",
            markerUnits="strokeWidth",
        )
        default_marker.add(
            dwg.path(d="M 0 0 L 10 5 L 0 10 z", fill=self.theme.edge_color, stroke="none")
        )
        dwg.defs.add(default_marker)
        # Record mapping for the default color
        self._color_marker_map[self.theme.edge_color] = self._arrow_marker_id

        # If trunk colors are provided, create per-color markers so arrowheads
        # can match the colored strokes applied to edges.
        unique_colors = set(self.trunk_colors.values()) if self.trunk_colors else set()
        # Avoid recreating a marker for the theme color
        unique_colors.discard(self.theme.edge_color)

        for color in sorted(unique_colors):
            # Build a DOM-safe id for this color-specific marker
            color_id = f"{self._arrow_marker_id}-{self._sanitize_dom_id(color)}"
            marker = dwg.marker(
                id=color_id,
                insert=(10, 5),
                size=(10, 10),
                orient="auto",
                markerUnits="strokeWidth",
            )
            marker.add(dwg.path(d="M 0 0 L 10 5 L 0 10 z", fill=color, stroke="none"))
            dwg.defs.add(marker)
            self._color_marker_map[color] = color_id

    def _get_edge_color(self, edge: PositionedEdge) -> tuple[str, str]:
        """Get the edge color and secondary color for a given edge.

        Returns a tuple of (primary_color, secondary_color).
        """
        if edge.trunk_key and edge.trunk_key in self.trunk_colors:
            primary = self.trunk_colors[edge.trunk_key]
            return (primary, primary)
        return (self.theme.edge_color, self.theme.edge_secondary)

    def _draw_edges(self, dwg: svgwrite.Drawing, layer: Any, diagram: PositionedDiagram) -> None:
        """Render routed edges before tables so nodes sit above the wiring if overlap occurs."""
        for edge in diagram.edges:
            points = self._edge_points(diagram, edge)
            if len(points) < 2:
                continue
            path = self._path_from_points(points)
            edge_color, edge_secondary = self._get_edge_color(edge)
            marker_id = self._color_marker_map.get(edge_color, self._arrow_marker_id)
            layer.add(
                dwg.path(
                    d=path,
                    fill="none",
                    stroke=edge_color,
                    stroke_width=self.theme.edge_width,
                    stroke_linejoin="round",
                    marker_end=f"url(#{marker_id})",
                )
            )

            if self.show_edge_labels and edge.label:
                if edge.label_position:
                    label_point = edge.label_position
                else:
                    label_point = points[len(points) // 2]
                layer.add(
                    dwg.text(
                        edge.label,
                        insert=(label_point[0], label_point[1]),
                        font_size=f"{self.theme.font_size_edge_label}px",
                        font_family=self.theme.font_family,
                        fill=self.theme.table_secondary_text,
                    )
                )

    def _draw_table(
        self,
        dwg: svgwrite.Drawing,
        layer: Any,
        node: PositionedNode,
        table: Table | View | None,
    ) -> None:
        """Render a table card with header, zebra rows, and column markers."""
        isView = isinstance(table, View)
        theme = self.theme
        group = dwg.g(class_="table" if not isView else "view")
        stroke_width = theme.table_stroke_width * 2

        clip_id = self._sanitize_dom_id(f"header-clip-{node.table_name}")
        clip_path = dwg.defs.add(dwg.clipPath(id=clip_id))
        clip_path.add(
            dwg.rect(
                insert=(node.x, node.y),
                size=(node.width, node.height),
                rx=theme.corner_radius,
                ry=theme.corner_radius,
            )
        )

        stroke_rect = dwg.rect(
            insert=(node.x, node.y),
            size=(node.width, node.height),
            rx=theme.corner_radius,
            ry=theme.corner_radius,
            stroke=theme.table_border,
            stroke_width=stroke_width,
            stroke_dasharray="0" if not isView else "8,4",
        )
        group.add(stroke_rect)

        bg_fill_rect = dwg.rect(
            insert=(node.x, node.y),
            size=(node.width, node.height),
            rx=theme.corner_radius,
            ry=theme.corner_radius,
            fill=theme.table_background,
            clip_path=f"url(#{clip_id})",
        )
        group.add(bg_fill_rect)

        header_rect = dwg.rect(
            insert=(node.x, node.y),
            size=(node.width, theme.header_height),
            rx=theme.corner_radius,
            ry=theme.corner_radius,
            fill=theme.table_header_bg,
            clip_path=f"url(#{clip_id})",
        )
        group.add(header_rect)
        header_text = node.table_name if not table else table.name
        marker_size = theme.font_size_secondary
        group.add(
            dwg.text(
                header_text,
                insert=(node.x + theme.table_side_padding + (marker_size if not isView else 0), node.y + theme.header_height / 2),
                dominant_baseline="middle",
                font_size=f"{theme.font_size_header}px",
                font_family=theme.font_family,
                fill=theme.table_header_text,
            )
        )

        body_group = dwg.g(clip_path=f"url(#{clip_id})")
        group.add(body_group)

        if table is None:
            logger.warning("No metadata for node '%s'", node.table_name)
        if isinstance(table, View):
            if table and (table.columns or table.referenced_tables):
                self._draw_view_columns(dwg, body_group, node, table)
            elif not table:
                self._draw_empty_state(dwg, body_group, node)
        else:
            columns = list(table.columns.values()) if table else []
            if not columns:
                self._draw_empty_state(dwg, body_group, node)
            elif table is not None:
                assert table is not None
                self._draw_columns(dwg, body_group, node, table)

        layer.add(group)

    def _draw_empty_state(self, dwg: svgwrite.Drawing, group: Any, node: PositionedNode) -> None:
        """Fallback for tables with zero parsed columns (common in partial dumps)."""
        theme = self.theme
        group.add(
            dwg.text(
                "No columns parsed",
                insert=(node.x + theme.table_side_padding, node.y + theme.header_height + theme.row_height / 2),
                font_size=f"{theme.font_size_body}px",
                font_family=theme.font_family,
                fill=theme.table_secondary_text,
            )
        )

    def _draw_columns(
        self, dwg: svgwrite.Drawing, group: Any, node: PositionedNode, table: Table
    ) -> None:
        """Render zebra rows, PK/FK markers, and type labels for each column."""
        theme = self.theme
        fk_columns = self._fk_columns(table)
        y = node.y + theme.header_height
        row_idx = 0

        for column in table.columns.values():
            row_top = y + row_idx * theme.row_height
            if row_idx % 2 == 1:
                group.add(
                    dwg.rect(
                        insert=(node.x, row_top),
                        size=(node.width, theme.row_height),
                        fill=theme.zebra_row,
                    )
                )

            marker_color = None
            if column.is_primary:
                marker_color = theme.pk_marker
            elif column.name in fk_columns:
                marker_color = theme.fk_marker

            marker_size = theme.font_size_secondary
            if marker_color:
                group.add(
                    dwg.circle(
                        center=(node.x + (theme.table_side_padding + marker_size) / 2, row_top + theme.row_height / 2),
                        r=marker_size/2,
                        fill=marker_color,
                    )
                )

            group.add(
                dwg.text(
                    column.name,
                    insert=(node.x + theme.table_side_padding + marker_size, row_top + theme.row_height / 2),
                    dominant_baseline="middle",
                    font_size=f"{theme.font_size_body}px",
                    font_family=theme.font_family,
                    fill=theme.table_body_text,
                )
            )

            group.add(
                dwg.text(
                    column.data_type,
                    insert=(node.x + node.width - theme.table_side_padding, row_top + theme.row_height / 2),
                    text_anchor="end",
                    dominant_baseline="middle",
                    font_size=f"{theme.font_size_secondary}px",
                    font_family=theme.font_family,
                    fill=theme.table_secondary_text,
                )
            )

            row_idx += 1

        if self.show_indexes:
            for idx in table.indexes:
                row_top = y + row_idx * theme.row_height
                if row_idx % 2 == 1:
                    group.add(
                        dwg.rect(
                            insert=(node.x, row_top),
                            size=(node.width, theme.row_height),
                            fill=theme.zebra_row,
                        )
                    )

                unique_str = "unique " if idx.is_unique else ""
                cols_str = ", ".join(idx.columns) if idx.columns else ""
                type_str = f"({idx.index_type}, {unique_str}idx)" if idx.index_type != "btree" or idx.is_unique else f"({idx.index_type} idx)"
                label = f"{idx.name}({cols_str}) {type_str}".strip()

                group.add(
                    dwg.circle(
                        center=(node.x + (theme.table_side_padding + marker_size) / 2, row_top + theme.row_height / 2),
                        r=marker_size/2,
                        fill=theme.idx_marker,
                    )
                )

                group.add(
                    dwg.text(
                        label,
                        insert=(node.x + theme.table_side_padding + marker_size, row_top + theme.row_height / 2),
                        dominant_baseline="middle",
                        font_size=f"{theme.font_size_secondary}px",
                        font_family=theme.font_family,
                        fill=theme.table_secondary_text,
                    )
                )
                row_idx += 1

        if self.show_sequences:
            for seq in table.sequences:
                row_top = y + row_idx * theme.row_height
                if row_idx % 2 == 1:
                    group.add(
                        dwg.rect(
                            insert=(node.x, row_top),
                            size=(node.width, theme.row_height),
                            fill=theme.zebra_row,
                        )
                    )

                label = f"{seq.name}({seq.increment})"

                group.add(
                    dwg.circle(
                        center=(node.x + (theme.table_side_padding + marker_size) / 2, row_top + theme.row_height / 2),
                        r=marker_size/2,
                        fill=theme.seq_marker,
                    )
                )

                group.add(
                    dwg.text(
                        label,
                        insert=(node.x + theme.table_side_padding, row_top + theme.row_height / 2),
                        dominant_baseline="middle",
                        font_size=f"{theme.font_size_secondary}px",
                        font_family=theme.font_family,
                        fill=theme.table_secondary_text,
                    )
                )
                row_idx += 1

    def _draw_view_columns(
        self, dwg: svgwrite.Drawing, group: Any, node: PositionedNode, view: View
    ) -> None:
        """Render view columns like a table."""
        theme = self.theme
        y = node.y + theme.header_height
        row_idx = 0

        columns = view.columns if view.columns else []

        if columns:
            for col in columns:
                row_top = y + row_idx * theme.row_height
                if row_idx % 2 == 1:
                    group.add(
                        dwg.rect(
                            insert=(node.x, row_top),
                            size=(node.width, theme.row_height),
                            fill=theme.zebra_row,
                        )
                    )

                group.add(
                    dwg.text(
                        col,
                        insert=(node.x + theme.table_side_padding, row_top + theme.row_height / 2),
                        dominant_baseline="middle",
                        font_size=f"{theme.font_size_body}px",
                        font_family=theme.font_family,
                        fill=theme.table_body_text,
                    )
                )

                row_idx += 1
        else:
            self._draw_empty_state(dwg, group, node)

    def _fk_columns(self, table: Table) -> set[str]:
        """Return the set of column names that participate in any FK."""
        names: set[str] = set()
        for fk in table.foreign_keys:
            names.update(fk.source_columns)
        return names

    def _edge_points(
        self, diagram: PositionedDiagram, edge: PositionedEdge
    ) -> List[Tuple[float, float]]:
        """Return explicit points for an edge, falling back to node centers."""
        if edge.points:
            return list(edge.points)
        if edge.source not in diagram.nodes or edge.target not in diagram.nodes:
            return []
        src = diagram.nodes[edge.source]
        tgt = diagram.nodes[edge.target]
        return [
            (src.x + src.width / 2, src.y + src.height / 2),
            (tgt.x + tgt.width / 2, tgt.y + tgt.height / 2),
        ]

    def _path_from_points(self, points: Sequence[Tuple[float, float]]) -> str:
        """Convert orthogonal polyline points into an SVG path string."""
        if len(points) < 2:
            return ""

        radius = getattr(self.theme, "edge_corner_radius", 0.0) or 0.0
        if radius <= 0:
            path_commands = [f"M {points[0][0]:.2f},{points[0][1]:.2f}"]
            for point in points[1:]:
                path_commands.append(f"L {point[0]:.2f},{point[1]:.2f}")
            return " ".join(path_commands)

        corner_radii = self._compute_corner_radii(points, radius)

        path_commands = [f"M {points[0][0]:.2f},{points[0][1]:.2f}"]
        current_pos = points[0]

        for idx in range(1, len(points)):
            target = points[idx]
            is_last = idx == len(points) - 1
            if is_last:
                if not self._points_close(current_pos, target):
                    path_commands.append(f"L {target[0]:.2f},{target[1]:.2f}")
                current_pos = target
                continue

            next_point = points[idx + 1]
            dir_in = self._unit_vector(current_pos, target)
            dir_out = self._unit_vector(target, next_point)

            if dir_in is None or dir_out is None or self._is_straight(dir_in, dir_out):
                if not self._points_close(current_pos, target):
                    path_commands.append(f"L {target[0]:.2f},{target[1]:.2f}")
                current_pos = target
                continue

            corner_radius = corner_radii[idx]
            if corner_radius <= 0:
                if not self._points_close(current_pos, target):
                    path_commands.append(f"L {target[0]:.2f},{target[1]:.2f}")
                current_pos = target
                continue

            corner_start = (
                target[0] - dir_in[0] * corner_radius,
                target[1] - dir_in[1] * corner_radius,
            )
            corner_end = (
                target[0] + dir_out[0] * corner_radius,
                target[1] + dir_out[1] * corner_radius,
            )

            if not self._points_close(current_pos, corner_start):
                path_commands.append(f"L {corner_start[0]:.2f},{corner_start[1]:.2f}")
            sweep_flag = 1 if self._cross(dir_in, dir_out) > 0 else 0
            path_commands.append(
                " ".join(
                    [
                        f"A {corner_radius:.2f},{corner_radius:.2f}",
                        "0 0",
                        str(sweep_flag),
                        f"{corner_end[0]:.2f},{corner_end[1]:.2f}",
                    ]
                )
            )
            current_pos = corner_end

        return " ".join(path_commands)

    def _compute_corner_radii(
        self, points: Sequence[Tuple[float, float]], max_radius: float
    ) -> List[float]:
        """Compute effective radius for each corner point, preventing overlap."""
        if len(points) < 3:
            return [0.0] * len(points)

        radii = [0.0] * len(points)

        for idx in range(1, len(points) - 1):
            prev_point = points[idx - 1]
            curr_point = points[idx]
            next_point = points[idx + 1]

            dir_in = self._unit_vector(prev_point, curr_point)
            dir_out = self._unit_vector(curr_point, next_point)

            if dir_in is None or dir_out is None or self._is_straight(dir_in, dir_out):
                continue

            dist_in = self._distance(prev_point, curr_point)
            dist_out = self._distance(curr_point, next_point)

            if dist_in < 1e-3 or dist_out < 1e-3:
                continue

            available_in = dist_in / 2
            available_out = dist_out / 2

            radii[idx] = min(max_radius, available_in, available_out)

        return radii

    def _points_close(
        self, a: Tuple[float, float], b: Tuple[float, float], eps: float = 1e-3
    ) -> bool:
        """Return True when two points are visually indistinguishable."""
        return self._distance(a, b) <= eps

    def _unit_vector(
        self, start: Tuple[float, float], end: Tuple[float, float], eps: float = 1e-6
    ) -> Tuple[float, float] | None:
        """Return the normalized direction from start to end, if any."""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        if length <= eps:
            return None
        return dx / length, dy / length

    def _is_straight(
        self, v1: Tuple[float, float], v2: Tuple[float, float], eps: float = 1e-3
    ) -> bool:
        """Check if two direction vectors continue in a straight line."""
        cross = self._cross(v1, v2)
        return abs(cross) <= eps

    def _cross(self, v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
        """2D cross product helper for arc sweep calculations."""
        return v1[0] * v2[1] - v1[1] * v2[0]

    def _distance(self, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        """Euclidean distance between two points."""
        return math.hypot(b[0] - a[0], b[1] - a[1])

    def _compute_canvas(self, diagram: PositionedDiagram) -> Tuple[float, float]:
        """Compute the overall canvas dimensions including padding."""
        padding = self.theme.canvas_padding
        xs: List[float] = []
        ys: List[float] = []

        for node in diagram.nodes.values():
            xs.extend([node.x, node.x + node.width])
            ys.extend([node.y, node.y + node.height])

        for edge in diagram.edges:
            xs.extend(point[0] for point in edge.points)
            ys.extend(point[1] for point in edge.points)
            if edge.label_position:
                xs.append(edge.label_position[0])
                ys.append(edge.label_position[1])

        if not xs or not ys:
            width = height = padding * 2
        else:
            width = max(xs) + padding
            height = max(ys) + padding

        return width, height
