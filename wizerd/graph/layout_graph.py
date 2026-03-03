"""Internal graph representation for layout engines."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class GraphNode:
    """Represents a table-sized rectangle before layout assigns positions."""

    table_name: str
    width: float = 240.0
    height: float = 120.0
    group: str | None = None
    column_anchors: Dict[str, float] = field(default_factory=dict)
    is_view: bool = False


@dataclass
class GraphEdge:
    """Represents a relationship between two nodes in the layout graph."""

    source: str
    target: str
    label: str | None = None
    weight: float = 1.0
    source_column: str | None = None
    target_column: str | None = None
    bundle_key: tuple[str, str | None] | None = None
    trunk_key: tuple[str, str | None] | None = None
    is_view_reference: bool = False


@dataclass
class LayoutGraph:
    """Mutable container for nodes and edges prior to layout."""

    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    edges: List[GraphEdge] = field(default_factory=list)

    def add_node(self, node: GraphNode) -> None:
        """Store or replace a node using its table name as the unique key."""
        self.nodes[node.table_name] = node

    def add_edge(self, edge: GraphEdge) -> None:
        """Append a directed edge representing a foreign-key relationship."""
        self.edges.append(edge)


@dataclass
class PositionedNode(GraphNode):
    """Graph node augmented with absolute coordinates from the layout engine."""

    x: float = 0.0
    y: float = 0.0


@dataclass
class PositionedEdge(GraphEdge):
    """Graph edge augmented with concrete routed points and label positions."""

    points: List[Tuple[float, float]] = field(default_factory=list)
    label_position: Tuple[float, float] | None = field(default=None)


@dataclass
class PositionedDiagram:
    """Final diagram returned by layout, ready for rendering."""

    nodes: Dict[str, PositionedNode]
    edges: List[PositionedEdge]
