"""Layout engine interfaces and implementations."""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Protocol, Tuple

from wizerd.graph.layout_graph import (
    LayoutGraph,
    PositionedDiagram,
    PositionedEdge,
    PositionedNode,
)
from wizerd.layout.spacing import SpacingProfile

logger = logging.getLogger(__name__)

DEFAULT_EDGE_LABEL_FONT_SIZE = 11
DEFAULT_EDGE_LABEL_CHAR_WIDTH = 6.5


def _estimate_text_size(
    text: str,
    font_size: int | float = DEFAULT_EDGE_LABEL_FONT_SIZE,
    char_width: float = DEFAULT_EDGE_LABEL_CHAR_WIDTH,
) -> Tuple[float, float]:
    """Return an estimated width/height box for an edge label.

    ELK needs rough bounding boxes to avoid overlapping labels with other
    routes.  We do not have font metrics here, so we approximate using a
    fixed character width—good enough for layout and incredibly fast.
    """
    width = len(text) * char_width
    height = font_size * 1
    return (width, height)


@dataclass
class LayoutResult:
    """Wrapper for the positioned diagram plus any spacing diagnostics."""

    diagram: PositionedDiagram
    spacing_violations: List[str] = field(default_factory=list)


class LayoutEngine(Protocol):
    """Interface that both the ELK and simple layout engines satisfy."""

    def layout(self, graph: LayoutGraph) -> LayoutResult:
        """Compute diagram coordinates for the given layout graph."""
        raise NotImplementedError


class SimpleLayoutEngine:
    """Deterministic placeholder layout to keep the CLI functional."""

    def layout(self, graph: LayoutGraph) -> LayoutResult:
        """Place tables in a vertical stack so we can still render in dev."""
        nodes = {}
        x = 40.0
        y = 40.0
        spacing_y = 60.0

        for _, node in sorted(graph.nodes.items()):
            positioned = PositionedNode(
                table_name=node.table_name,
                width=node.width,
                height=node.height,
                group=node.group,
                x=x,
                y=y,
            )
            nodes[node.table_name] = positioned
            y += node.height + spacing_y

        edges = [
            PositionedEdge(
                source=edge.source,
                target=edge.target,
                label=edge.label,
                weight=edge.weight,
                points=[],
            )
            for edge in graph.edges
        ]
        diagram = PositionedDiagram(nodes=nodes, edges=edges)
        return LayoutResult(diagram=diagram)


@dataclass
class ElkLayoutConfig:
    """Configuration for ELK layout engine."""

    direction: str = "RIGHT"
    horizontal_margin: float = 56.0
    vertical_margin: float = 56.0
    spacing_layer: float = 280.0
    spacing_component: float = 400.0
    spacing_node_node: float = 100.0
    spacing_edge_node: float = 40.0
    spacing_edge_edge: float = 24.0

    @classmethod
    def from_spacing_profile(cls, profile: SpacingProfile) -> "ElkLayoutConfig":
        """Derive ELK-specific spacing knobs from a user-facing profile."""
        derived = profile.derived()
        return cls(
            horizontal_margin=derived.horizontal_margin,
            vertical_margin=derived.vertical_margin,
            spacing_layer=derived.spacing_layer,
            spacing_component=derived.spacing_component,
            spacing_node_node=derived.spacing_node_node,
            spacing_edge_node=derived.spacing_edge_node,
            spacing_edge_edge=derived.spacing_edge_edge,
        )


class ElkLayoutEngine:
    """Production layout engine backed by ELK (layered, orthogonal)."""

    def __init__(
        self,
        runner_path: Path | None = None,
        node_executable: str | None = None,
        config: ElkLayoutConfig | None = None,
        spacing_profile: SpacingProfile | None = None,
        *,
        show_edge_labels: bool = False,
        font_size_edge_label: float = DEFAULT_EDGE_LABEL_FONT_SIZE,
        char_pixel_width: float = DEFAULT_EDGE_LABEL_CHAR_WIDTH,
    ) -> None:
        """Wire up the ELK runner script and resolution strategy.

        The constructor accepts optional overrides so tests can point to a
        fake Node binary or a custom spacing preset.  We eagerly validate the
        Node.js executable so misconfigured environments fail fast.
        """
        self.spacing_profile = spacing_profile or SpacingProfile.default()
        self.config = config or ElkLayoutConfig.from_spacing_profile(self.spacing_profile)
        self.runner_path = runner_path or Path(__file__).with_name("elk_runner.mjs")
        self.show_edge_labels = show_edge_labels
        self.font_size_edge_label = font_size_edge_label
        self.char_pixel_width = char_pixel_width

        node_path = node_executable or shutil.which("node")
        if not node_path:
            raise RuntimeError(
                "Node.js executable not found on PATH. Install Node 18+ to enable the ELK layout engine."
            )
        self.node_executable = node_path

    def layout(self, graph: LayoutGraph) -> LayoutResult:
        """Call the ELK runner and convert the result back into Python models."""
        payload = self._build_payload(graph)
        # print(payload)
        elk_result = self._invoke_elk(payload)
        diagram = self._build_diagram(graph, elk_result)
        return LayoutResult(diagram=diagram, spacing_violations=[])

    def _build_payload(self, graph: LayoutGraph) -> Dict:
        """Serialize our LayoutGraph into the JSON structure ELK expects."""
        layout_options = {
            "elk.direction": self.config.direction,
            "elk.layered.crossingMinimization.strategy": "LAYER_SWEEP",  # "LAYER_SWEEP" or "MEDIAN_LAYER_SWEEP" idk the difference, or "NONE" to disable
            "elk.layered.layering.strategy": "LONGEST_PATH_SOURCE",  # right side heavy "LONGEST_PATH" or left side heavy "LONGEST_PATH_SOURCE" or weighted grouping "COFFMAN_GRAHAM"
            "elk.layered.thoroughness": "100",  # Self explanatory
            "elk.layered.spacing.nodeNodeBetweenLayers": str(self.config.spacing_layer),
            "elk.layered.spacing.edgeNodeBetweenLayers": str(self.config.spacing_edge_node),
            "elk.layered.spacing.edgeEdgeBetweenLayers": str(
                self.config.spacing_edge_edge
            ),  # Minimum distance between vertical lines (x-axis spacing)
            "elk.layered.nodePlacement.favorStraightEdges": "true",
            "elk.layered.compaction.postCompaction.strategy": "NONE",  # "NONE" for clean rows or "EDGE_LENGTH" for shortest edges
            "elk.spacing.componentComponent": str(self.config.spacing_component),
            "elk.spacing.nodeNode": str(self.config.spacing_node_node),
            "elk.spacing.edgeNode": str(self.config.spacing_edge_node),
            "elk.spacing.nodeSelfLoop": str(
                self.config.spacing_edge_node
            ),  # Distance between the line and the node when its a self reference
            "elk.spacing.edgeEdge": str(
                self.config.spacing_edge_edge
            ),  # Minimum distance between horizontal lines (y-axis spacing)
            "elk.edgeRouting": "ORTHOGONAL",
            "elk.layered.edgeLabels.sideSelection": "ALWAYS_UP",
            "elk.layered.edgeLabels.centerLabelPlacementStrategy": "HEAD_LAYER",  # "HEAD_LAYER" for the label at the end, "TAIL_LAYER" for the label at the start, "MEDIAN_LAYER" for middle
            "elk.edge.thickness": "2",
            "org.eclipse.elk.activateHandleSelfLoops": "true",
        }

        children = []
        for node in graph.nodes.values():
            ports = []
            if node.column_anchors:
                for col_name, y_offset in node.column_anchors.items():
                    ports.append(
                        {
                            "id": f"{node.table_name}::{col_name}::east",
                            "x": node.width,
                            "y": y_offset,
                            "layoutOptions": {"org.eclipse.elk.port.side": "EAST"},
                        }
                    )
                    ports.append(
                        {
                            "id": f"{node.table_name}::{col_name}::west",
                            "x": 0.0,
                            "y": y_offset,
                            "layoutOptions": {"org.eclipse.elk.port.side": "WEST"},
                        }
                    )
            else:
                ports.append(
                    {
                        "id": f"{node.table_name}::east",
                        "x": node.width,
                        "y": node.height / 2,
                        "layoutOptions": {"org.eclipse.elk.port.side": "EAST"},
                    }
                )
                ports.append(
                    {
                        "id": f"{node.table_name}::west",
                        "x": 0.0,
                        "y": node.height / 2,
                        "layoutOptions": {"org.eclipse.elk.port.side": "WEST"},
                    }
                )

            children.append(
                {
                    "id": node.table_name,
                    "width": node.width,
                    "height": node.height,
                    "layoutOptions": {
                        "org.eclipse.elk.portConstraints": "FIXED_POS",
                    },
                    "ports": ports,
                }
            )

        edges_payload = []
        for idx, edge in enumerate(graph.edges):
            src_col = edge.source_column
            tgt_col = edge.target_column

            src_node = graph.nodes.get(edge.source)
            tgt_node = graph.nodes.get(edge.target)

            has_src_col = (
                src_node and src_node.column_anchors and src_col in src_node.column_anchors
            )
            has_tgt_col = (
                tgt_node and tgt_node.column_anchors and tgt_col in tgt_node.column_anchors
            )

            src_port = f"{edge.source}::{src_col}::east" if has_src_col else f"{edge.source}::east"
            tgt_port = f"{edge.target}::{tgt_col}::west" if has_tgt_col else f"{edge.target}::west"

            label_entry: Dict = {}
            if self.show_edge_labels and edge.label:
                width, height = _estimate_text_size(
                    edge.label,
                    font_size=self.font_size_edge_label,
                    char_width=self.char_pixel_width,
                )
                label_entry = {
                    "labels": [
                        {
                            "text": edge.label,
                            "width": width,
                            "height": height,
                        }
                    ]
                }

            edges_payload.append(
                {
                    "id": f"edge_{idx}",
                    "sources": [src_port],
                    "targets": [tgt_port],
                    **label_entry,
                }
            )

        return {
            "id": "root",
            "layoutOptions": layout_options,
            "children": children,
            "edges": edges_payload,
        }

    def _invoke_elk(self, payload: Dict) -> Dict:
        """Run the Node-based ELK bridge and return its JSON response."""
        completed = subprocess.run(
            [self.node_executable, str(self.runner_path)],
            input=json.dumps(payload).encode("utf-8"),
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            stderr = completed.stderr.decode("utf-8", errors="ignore")
            raise RuntimeError(f"ELK layout failed: {stderr.strip() or 'unknown error'}")
        try:
            return json.loads(completed.stdout.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError("ELK layout produced invalid JSON output") from exc

    def _build_diagram(self, graph: LayoutGraph, elk_result: Dict) -> PositionedDiagram:
        """Map ELK coordinates back onto `PositionedDiagram` objects."""
        nodes: Dict[str, PositionedNode] = {}
        for child in elk_result.get("children", []):
            table_name = child["id"]
            original = graph.nodes.get(table_name)
            if not original:
                continue
            nodes[table_name] = PositionedNode(
                table_name=table_name,
                width=original.width,
                height=original.height,
                group=original.group,
                column_anchors=original.column_anchors,
                x=float(child.get("x", 0.0)),
                y=float(child.get("y", 0.0)),
            )

        offset_x, offset_y = self._normalize_nodes(nodes)

        positioned_edges: List[PositionedEdge] = []

        edge_id_map = {f"edge_{i}": edge for i, edge in enumerate(graph.edges)}

        for e in elk_result.get("edges", []):
            original_edge = edge_id_map.get(e["id"])
            if not original_edge:
                continue

            points = []
            sections = e.get("sections", [])
            for section in sections:
                start = section.get("startPoint")
                if start:
                    points.append((float(start["x"]) + offset_x, float(start["y"]) + offset_y))
                for bp in section.get("bendPoints", []):
                    points.append((float(bp["x"]) + offset_x, float(bp["y"]) + offset_y))
                end = section.get("endPoint")
                if end:
                    points.append((float(end["x"]) + offset_x, float(end["y"]) + offset_y))

            deduped: list[tuple[float, float]] = []
            for p in points:
                if not deduped or (
                    abs(deduped[-1][0] - p[0]) > 1e-3 or abs(deduped[-1][1] - p[1]) > 1e-3
                ):
                    deduped.append(p)

            label_position = None
            if self.show_edge_labels:
                labels = e.get("labels", [])
                if labels:
                    lbl = labels[0]
                    label_position = (float(lbl["x"]) + offset_x, float(lbl["y"]) + offset_y)

            positioned_edges.append(
                PositionedEdge(
                    source=original_edge.source,
                    target=original_edge.target,
                    label=original_edge.label,
                    weight=original_edge.weight,
                    source_column=original_edge.source_column,
                    target_column=original_edge.target_column,
                    bundle_key=original_edge.bundle_key,
                    trunk_key=original_edge.trunk_key,
                    points=deduped,
                    label_position=label_position,
                )
            )

        diagram = PositionedDiagram(nodes=nodes, edges=positioned_edges)

        for edge in diagram.edges:
            if not edge.points:
                source_node = diagram.nodes.get(edge.source)
                target_node = diagram.nodes.get(edge.target)
                if source_node and target_node:
                    sy = source_node.y + source_node.column_anchors.get(
                        edge.source_column or "", source_node.height / 2
                    )
                    ty = target_node.y + target_node.column_anchors.get(
                        edge.target_column or "", target_node.height / 2
                    )
                    sx = source_node.x + source_node.width
                    tx = target_node.x
                    edge.points = [(sx, sy), (tx, ty)]

        return diagram

    def _normalize_nodes(self, nodes: Dict[str, PositionedNode]) -> Tuple[float, float]:
        """Shift nodes so the final diagram has positive coordinates and margins."""
        if not nodes:
            return (0.0, 0.0)
        min_x = min(node.x for node in nodes.values())
        min_y = min(node.y for node in nodes.values())
        offset_x = (
            (self.config.horizontal_margin - min_x)
            if min_x < self.config.horizontal_margin
            else 0.0
        )
        offset_y = (
            (self.config.vertical_margin - min_y) if min_y < self.config.vertical_margin else 0.0
        )
        if offset_x == 0.0 and offset_y == 0.0:
            return (0.0, 0.0)
        for node in nodes.values():
            node.x += offset_x
            node.y += offset_y
        return (offset_x, offset_y)
