"""Spacing profiles for the layout engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Dict


@dataclass
class SpacingProfile:
    """User-facing spacing configuration for the layout engine."""

    name: str
    column_gap: float
    row_gap: float
    component_gap: float
    edge_to_node_gap: float
    edge_gap: float
    margin: float

    _PRESETS: ClassVar[Dict[str, Dict[str, float]]] = {
        "compact": {
            "column_gap": 180.0,
            "row_gap": 110.0,
            "component_gap": 260.0,
            "edge_to_node_gap": 26.0,
            "edge_gap": 18.0,
            "margin": 36.0,
        },
        "standard": {
            # Significantly larger than compact to provide much more breathing room
            "column_gap": 360.0,
            "row_gap": 225.0,
            "component_gap": 570.0,
            "edge_to_node_gap": 51.0,
            "edge_gap": 39.0,
            "margin": 72.0,
        },
        "spacious": {
            # Much larger spacing for very large schemas and review purposes
            "column_gap": 720.0,
            "row_gap": 450.0,
            "component_gap": 1140.0,
            "edge_to_node_gap": 102.0,
            "edge_gap": 78.0,
            "margin": 144.0,
        },
    }

    @classmethod
    def default(cls) -> "SpacingProfile":
        """Return the profile that matches production defaults."""
        return cls.from_name("standard")

    @classmethod
    def from_name(cls, name: str) -> "SpacingProfile":
        """Look up a named preset, raising if the user requested an unknown one."""
        key = (name or "standard").strip().lower()
        preset = cls._PRESETS.get(key)
        if preset is None:
            raise ValueError(
                f"Unknown spacing profile '{name}'. Expected one of: {', '.join(sorted(cls._PRESETS))}."
            )
        return cls(name=key, **preset)

    def derived(self) -> "SpacingDerived":
        """Convert user-facing spacing to ELK configuration values."""
        return SpacingDerived(
            horizontal_margin=self.margin,
            vertical_margin=self.margin,
            spacing_layer=self.column_gap,
            spacing_component=self.component_gap,
            spacing_node_node=self.row_gap,
            spacing_edge_node=self.edge_to_node_gap,
            spacing_edge_edge=self.edge_gap,
        )


@dataclass
class SpacingDerived:
    """ELK configuration values derived from user-facing SpacingProfile."""

    horizontal_margin: float
    vertical_margin: float
    spacing_layer: float
    spacing_component: float
    spacing_node_node: float
    spacing_edge_node: float
    spacing_edge_edge: float
