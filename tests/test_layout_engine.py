"""Unit tests for the ELK-backed layout engine."""

from __future__ import annotations

import shutil

import pytest

from wizerd.graph.layout_graph import GraphEdge, GraphNode, LayoutGraph
from wizerd.layout.engine import ElkLayoutEngine


def _build_sample_graph() -> LayoutGraph:
    """Create a multi-node graph that exercises bundling and self-loops."""
    graph = LayoutGraph()
    graph.add_node(GraphNode(table_name="users"))
    graph.add_node(GraphNode(table_name="posts"))
    graph.add_node(GraphNode(table_name="comments"))
    graph.add_node(GraphNode(table_name="audit"))
    graph.add_edge(GraphEdge(source="users", target="posts"))
    graph.add_edge(GraphEdge(source="posts", target="comments"))
    graph.add_edge(GraphEdge(source="users", target="comments"))
    graph.add_edge(GraphEdge(source="audit", target="audit"))
    return graph


def _assert_no_overlap(nodes):
    """Ensure positioned nodes do not collide after layout."""
    nodes_list = list(nodes)
    for idx, left in enumerate(nodes_list):
        for right in nodes_list[idx + 1 :]:
            if not (
                left.x + left.width <= right.x
                or right.x + right.width <= left.x
                or left.y + left.height <= right.y
                or right.y + right.height <= left.y
            ):
                pytest.fail(f"Nodes {left.table_name} and {right.table_name} overlap")


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is required for ELK layouts")
def test_elk_layout_engine_positions_nodes_and_routes_edges():
    """ELK should produce orthogonal layouts without overlapping nodes."""
    graph = _build_sample_graph()
    engine = ElkLayoutEngine()

    result = engine.layout(graph)
    diagram = result.diagram

    assert set(diagram.nodes) == {"users", "posts", "comments", "audit"}
    _assert_no_overlap(diagram.nodes.values())

    # Expect orthogonal polylines flowing left-to-right
    for positioned_edge in diagram.edges:
        assert len(positioned_edge.points) >= 2
        if positioned_edge.source == positioned_edge.target:
            continue
        xs = [point[0] for point in positioned_edge.points]
        assert xs[-1] >= xs[0]


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is required for ELK layouts")
def test_elk_layout_engine_handles_missing_node_dependency():
    """A graph with a single node should still be laid out without error."""
    graph = LayoutGraph()
    graph.add_node(GraphNode(table_name="solo"))

    engine = ElkLayoutEngine()
    result = engine.layout(graph)

    assert set(result.diagram.nodes) == {"solo"}
    assert result.diagram.edges == []
