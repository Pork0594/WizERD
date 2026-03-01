"""Renderer regression tests."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from wizerd.graph.layout_graph import PositionedDiagram, PositionedEdge, PositionedNode
from wizerd.model.schema import Column, SchemaModel, Table
from wizerd.render.svg_renderer import RendererTheme, SVGRenderer


def _build_schema() -> SchemaModel:
    """Construct a tiny schema graph with users and posts tables."""
    users = Table(name="public.users", schema="public")
    users.add_column(Column(name="id", data_type="uuid", nullable=False, is_primary=True))
    users.add_column(Column(name="email", data_type="text", nullable=False))

    posts = Table(name="public.posts", schema="public")
    posts.add_column(Column(name="id", data_type="uuid", nullable=False, is_primary=True))
    posts.add_column(Column(name="user_id", data_type="uuid", nullable=False))
    posts.add_column(Column(name="title", data_type="text"))

    schema = SchemaModel(tables={"public.users": users, "public.posts": posts})
    return schema


def _build_diagram() -> PositionedDiagram:
    """Return positioned nodes that roughly mirror the example schema."""
    users_node = PositionedNode(table_name="public.users", width=320, height=150, x=60, y=60)
    posts_node = PositionedNode(table_name="public.posts", width=340, height=180, x=480, y=200)

    edge = PositionedEdge(
        source="public.posts",
        target="public.users",
        label="posts_user_id_fkey",
        points=[
            (posts_node.x + posts_node.width, posts_node.y + 60),
            (posts_node.x + posts_node.width + 80, posts_node.y + 60),
            (users_node.x - 80, users_node.y + 40),
            (users_node.x, users_node.y + 40),
        ],
    )

    return PositionedDiagram(
        nodes={
            users_node.table_name: users_node,
            posts_node.table_name: posts_node,
        },
        edges=[edge],
    )


def test_svg_renderer_outputs_styled_tables(tmp_path):
    """Baseline render should include tables, zebra rows, and edge paths."""
    schema = _build_schema()
    diagram = _build_diagram()
    theme = RendererTheme()

    renderer = SVGRenderer(theme=theme)
    output_path = tmp_path / "diagram.svg"
    renderer.render(diagram, schema, output_path)

    content = output_path.read_text()
    assert ">users<" in content
    assert "email" in content
    assert "marker" in content  # arrow definition
    assert "posts_user_id_fkey" not in content
    assert theme.table_header_bg in content

    tree = ET.parse(output_path)
    edge_paths = [
        elem.attrib.get("d", "")
        for elem in tree.findall(".//{http://www.w3.org/2000/svg}path")
        if elem.attrib.get("stroke") == theme.edge_color
    ]
    assert edge_paths, "expected at least one edge path in SVG"
    assert any(" A " in path for path in edge_paths)


def test_svg_renderer_allows_edge_labels(tmp_path):
    """When enabled, FK labels should be present in the SVG text nodes."""
    schema = _build_schema()
    diagram = _build_diagram()
    renderer = SVGRenderer(show_edge_labels=True)
    output_path = tmp_path / "diagram.svg"
    renderer.render(diagram, schema, output_path)

    content = output_path.read_text()
    assert "posts_user_id_fkey" in content


def test_svg_renderer_uses_trunk_colors(tmp_path):
    """Edges with trunk keys should pull colors from the provided palette."""
    schema = _build_schema()
    diagram = _build_diagram()

    trunk_colors: dict[tuple[str, str | None], str] = {("public.users", "id"): "#f472b6"}
    for edge in diagram.edges:
        edge.trunk_key = ("public.users", "id")

    renderer = SVGRenderer(trunk_colors=trunk_colors)
    output_path = tmp_path / "diagram.svg"
    renderer.render(diagram, schema, output_path)

    content = output_path.read_text()
    assert "#f472b6" in content


def test_svg_renderer_falls_back_to_default_color_without_trunk_colors(tmp_path):
    """Without trunk overrides the renderer should use the theme palette."""
    schema = _build_schema()
    diagram = _build_diagram()
    theme = RendererTheme()

    renderer = SVGRenderer(theme=theme)
    output_path = tmp_path / "diagram.svg"
    renderer.render(diagram, schema, output_path)

    content = output_path.read_text()
    assert theme.edge_color in content
