"""Orchestrates WizERD operations."""

from __future__ import annotations

import logging
from typing import Any, Dict

from wizerd import config
from wizerd.graph.layout_graph import GraphEdge, GraphNode, LayoutGraph
from wizerd.layout.engine import ElkLayoutEngine, LayoutEngine, LayoutResult, SimpleLayoutEngine
from wizerd.model.schema import SchemaModel, Table, View
from wizerd.parser.ddl_parser import DDLParser
from wizerd.render.svg_renderer import SVGRenderer
from wizerd.theme import Theme
from wizerd.theme.loader import load_theme

logger = logging.getLogger(__name__)


DEFAULT_TABLE_MIN_WIDTH = 220.0
DEFAULT_TABLE_MAX_WIDTH = 460.0
DEFAULT_TABLE_HEADER_HEIGHT = 44.0
DEFAULT_TABLE_ROW_HEIGHT = 30.0
DEFAULT_TABLE_FOOTER_PADDING = 0.0
DEFAULT_CHAR_PIXEL_WIDTH = 7.6
DEFAULT_TABLE_SIDE_PADDING = 28.0
DEFAULT_MARKER_SIZE = 10.0


def _schema_to_graph(
    schema: SchemaModel,
    edge_color_mode: config.EdgeColorMode,
    theme: Theme,
    show_indexes: bool = False,
    show_views: bool = False,
    show_sequences: bool = False,
) -> tuple[LayoutGraph, dict[tuple[str, str | None], str]]:
    """Convert the parsed schema into a layout graph the renderer understands.

    The pipeline keeps parsing, layout, and rendering decoupled by expressing
    tables as lightweight `GraphNode` objects and foreign keys as `GraphEdge`
    instances.  This helper is responsible for translating semantic metadata
    (column widths, header heights, trunk coloring) into numbers that the
    layout engines can place on a canvas.
    """
    graph = LayoutGraph()

    table_min_width = theme.dimensions.table_min_width
    table_max_width = theme.dimensions.table_max_width
    header_height = theme.dimensions.header_height
    row_height = theme.dimensions.row_height
    side_padding = theme.dimensions.table_side_padding
    marker_size = theme.typography.font_size_secondary
    char_width = theme.typography.char_pixel_width

    for table in schema.tables.values():
        extra_rows = 0
        if show_indexes:
            extra_rows += len(table.indexes)
        if show_sequences:
            extra_rows += len(table.sequences)

        width, height, anchors = _measure_table(
            table,
            table_min_width=table_min_width,
            table_max_width=table_max_width,
            header_height=header_height,
            row_height=row_height,
            side_padding=side_padding,
            marker_size=marker_size,
            char_width=char_width,
            extra_rows=extra_rows,
        )
        graph.add_node(
            GraphNode(
                table_name=table.name,
                width=width,
                height=height,
                group=table.schema,
                column_anchors=anchors,
            )
        )

    if show_views:
        for view in schema.views.values():
            view_width, view_height, view_anchors = _measure_view(
                view,
                table_min_width=table_min_width,
                table_max_width=table_max_width,
                header_height=header_height,
                row_height=row_height,
                side_padding=side_padding,
                char_width=char_width,
            )
            view_full_name = f"{view.schema}.{view.name}" if view.schema else view.name
            graph.add_node(
                GraphNode(
                    table_name=view_full_name,
                    width=view_width,
                    height=view_height,
                    group=view.schema,
                    column_anchors=view_anchors,
                    is_view=True,
                )
            )

            referenced_tables = list(dict.fromkeys(view.referenced_tables)) if view.referenced_tables else []
            for ref_table in referenced_tables:
                if ref_table in schema.tables:
                    graph.add_edge(
                        GraphEdge(
                            source=ref_table,
                            target=view_full_name,
                            label="",
                            source_column=None,
                            target_column=None,
                            bundle_key=(view_full_name, None),
                            trunk_key=None,
                            is_view_reference=True,
                        )
                    )

    trunk_keys: set[tuple[str, str | None]] = set()
    for table in schema.tables.values():
        for fk in table.foreign_keys:
            if fk.target_columns and len(fk.target_columns) != len(fk.source_columns):
                raise ValueError(
                    f"Foreign key {fk.name or fk.source_table} has mismatched source/target columns"
                )

            target_columns = fk.target_columns or [None] * len(fk.source_columns)  # type: ignore[list-item]

            source_cols_str = [str(col) if col else "" for col in fk.source_columns]
            label = fk.name or f"{fk.source_table}_{'_'.join(source_cols_str)}_fkey"
            for source_col, target_col in zip(fk.source_columns, target_columns):
                bundle_key = (fk.target_table, target_col)

                trunk_key: tuple[str, str | None] | None = None
                if edge_color_mode == config.EdgeColorMode.BY_TRUNK and fk.target_columns:
                    trunk_key = (fk.target_table, fk.target_columns[0])
                    trunk_keys.add(trunk_key)

                graph.add_edge(
                    GraphEdge(
                        source=fk.target_table,
                        target=fk.source_table,
                        label=label,
                        source_column=target_col,
                        target_column=source_col,
                        bundle_key=bundle_key,
                        trunk_key=trunk_key,
                    )
                )

    trunk_colors: dict[tuple[str, str | None], str] = (
        _compute_trunk_colors(trunk_keys, theme) if trunk_keys else {}
    )

    return graph, trunk_colors


def _compute_trunk_colors(
    trunk_keys: set[tuple[str, str | None]],
    theme: Theme,
) -> dict[tuple[str, str | None], str]:
    """Assign colors to trunk keys deterministically based on their sorted order."""
    sorted_trunks = sorted(trunk_keys)
    colors = list(theme.edges.edge_color_palette)
    return {trunk: colors[i % len(colors)] for i, trunk in enumerate(sorted_trunks)}


def _measure_table(
    table: Table,
    table_min_width: float = DEFAULT_TABLE_MIN_WIDTH,
    table_max_width: float = DEFAULT_TABLE_MAX_WIDTH,
    header_height: float = DEFAULT_TABLE_HEADER_HEIGHT,
    row_height: float = DEFAULT_TABLE_ROW_HEIGHT,
    side_padding: float = DEFAULT_TABLE_SIDE_PADDING,
    marker_size: float = DEFAULT_MARKER_SIZE,
    char_width: float = DEFAULT_CHAR_PIXEL_WIDTH,
    extra_rows: int = 0,
) -> tuple[float, float, dict[str, float]]:
    """Return the on-canvas footprint for a table and lookup offsets.

    Layout engines only see rectangles, so we approximate width by counting the
    longest textual label and translating characters to pixels using the
    current theme's typography.  The returned anchor map tells downstream
    routing logic where each column sits vertically so edges can snap to the
    right row.
    """
    rows = max(1, len(table.columns) + extra_rows)
    height = header_height + rows * row_height + DEFAULT_TABLE_FOOTER_PADDING

    longest = len(table.name)
    for column in table.columns.values():
        label = f"{column.name}  {column.data_type}"
        longest = max(longest, len(label))

    if extra_rows > 0:
        for idx in table.indexes:
            unique_str = "unique " if idx.is_unique else ""
            cols_str = ", ".join(idx.columns) if idx.columns else ""
            type_str = f"({idx.index_type}, {unique_str}idx)" if idx.index_type != "btree" or idx.is_unique else f"({idx.index_type} idx)"
            label = f"{idx.name}({cols_str}) {type_str}".strip()
            longest = max(longest, len(label))
        for seq in table.sequences:
            label = f"{seq.name} (inc={seq.increment})"
            longest = max(longest, len(label))

    width = side_padding * 2 + longest * char_width + marker_size
    width = max(table_min_width, min(width, table_max_width))

    anchors: dict[str, float] = {}
    current = header_height + row_height / 2
    for column in table.columns.values():
        anchors[column.name] = current
        current += row_height

    return width, height, anchors


def _measure_view(
    view: View,
    table_min_width: float = DEFAULT_TABLE_MIN_WIDTH,
    table_max_width: float = DEFAULT_TABLE_MAX_WIDTH,
    header_height: float = DEFAULT_TABLE_HEADER_HEIGHT,
    row_height: float = DEFAULT_TABLE_ROW_HEIGHT,
    side_padding: float = DEFAULT_TABLE_SIDE_PADDING,
    char_width: float = DEFAULT_CHAR_PIXEL_WIDTH,
) -> tuple[float, float, dict[str, float]]:
    """Return the on-canvas footprint for a view and lookup offsets."""
    columns = view.columns if view.columns else []

    rows = max(1, len(columns))
    height = header_height + rows * row_height + DEFAULT_TABLE_FOOTER_PADDING

    longest = len(view.name)
    if columns:
        for col in columns:
            longest = max(longest, len(col))

    width = side_padding * 2 + longest * char_width
    width = max(table_min_width, min(width, table_max_width))

    anchors: dict[str, float] = {}
    current = header_height + row_height / 2
    if columns:
        for col in columns:
            anchors[col] = current
            current += row_height

    return width, height, anchors


def run(app_config: config.AppConfig) -> None:
    """Execute the end-to-end generation pipeline for a single invocation.

    The CLI resolves configuration before delegating here.  This function keeps
    orchestration centralized: load the theme, parse SQL into a schema model,
    build the layout graph, ask ELK for positions, and finally hand everything
    to the SVG renderer.  Raising exceptions here ensures the CLI can surface
    actionable errors without duplicating logic.
    """
    overrides: Dict[str, Any] | None = app_config.theme_overrides.to_dict() or None

    theme = load_theme(
        theme_name=app_config.theme_name,
        theme_inline=app_config.theme_inline,
        theme_overrides=overrides,
    )

    parser = DDLParser()
    schema: SchemaModel = parser.parse_file(app_config.input_path)

    if not schema.tables:
        raise ValueError(
            "No tables found in schema dump. Ensure the SQL contains CREATE TABLE statements."
        )

    graph, trunk_colors = _schema_to_graph(
        schema,
        app_config.edge_color_mode,
        theme,
        show_indexes=app_config.show_indexes,
        show_views=app_config.show_views,
        show_sequences=app_config.show_sequences,
    )

    layout_engine: LayoutEngine
    try:
        layout_engine = ElkLayoutEngine(
            spacing_profile=app_config.spacing_profile,
            show_edge_labels=app_config.show_edge_labels,
            font_size_edge_label=theme.typography.font_size_edge_label,
            char_pixel_width=theme.typography.char_pixel_width,
        )
    except RuntimeError as exc:
        logger.warning("Falling back to simple layout engine: %s", exc)
        layout_engine = SimpleLayoutEngine()

    layout_result: LayoutResult = layout_engine.layout(graph)

    renderer_theme = theme.to_renderer_theme()
    renderer = SVGRenderer(
        theme=renderer_theme,
        show_edge_labels=app_config.show_edge_labels,
        trunk_colors=trunk_colors if trunk_colors else None,
        show_indexes=app_config.show_indexes,
        show_views=app_config.show_views,
        show_sequences=app_config.show_sequences,
    )
    renderer.render(layout_result.diagram, schema, app_config.output_path)
