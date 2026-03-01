"""Spacing profiles for the layout engine."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SpacingProfile:
    """User-facing spacing configuration for ELK layout.

    Attributes:
        name: Profile identifier (compact, standard, spacious)
        line_gap: Minimum gap between parallel edge segments
        line_table_gap: Minimum gap between edges and tables
        entry_zone_gap: Gap between table and incoming edge bends
    """

    name: str
    line_gap: float
    line_table_gap: float
    entry_zone_gap: float

    @classmethod
    def default(cls) -> "SpacingProfile":
        """Return the profile that matches production defaults."""
        return cls(
            name="standard",
            line_gap=40.0,
            line_table_gap=36.0,
            entry_zone_gap=40.0,
        )

    @classmethod
    def from_name(cls, name: str) -> "SpacingProfile":
        """Look up a named preset, raising if the user requested an unknown one."""
        key = (name or "standard").strip().lower()
        profiles = {
            "compact": cls(
                name="compact",
                line_gap=16.0,
                line_table_gap=24.0,
                entry_zone_gap=32.0,
            ),
            "standard": cls.default(),
            "spacious": cls(
                name="spacious",
                line_gap=64.0,
                line_table_gap=48.0,
                entry_zone_gap=64.0,
            ),
        }
        if key not in profiles:
            raise ValueError(
                f"Unknown spacing profile '{name}'. Expected one of: {', '.join(profiles.keys())}."
            )
        return profiles[key]

    def derived(self) -> "SpacingDerived":
        """Convert user-facing spacing to ELK configuration values."""
        horizontal_margin = max(56.0, self.line_table_gap + 20.0)

        return SpacingDerived(
            horizontal_margin=horizontal_margin,
            vertical_margin=horizontal_margin,
            spacing_layer=max(
                350.0, self.entry_zone_gap * 6.0
            ),  # Distance between columns of tables horizontally (X-axis spacing)
            spacing_component=max(
                500.0, self.line_table_gap * 12.0
            ),  # Distance between unconnected components (groups of tables)
            spacing_node_node=max(150.0, self.line_table_gap * 4.0),  # Distance between two nodes
            spacing_edge_node=max(
                60.0, self.line_table_gap * 2.0
            ),  # Distance between an edge and a node
            spacing_edge_edge=max(20.0, self.line_gap),  # Distance between two edges
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
