"""Tests for spacing profiles and derived layout config."""

from wizerd.layout.engine import ElkLayoutConfig
from wizerd.layout.spacing import SpacingProfile


def test_spacing_profile_from_name_returns_expected_values():
    """Named profiles should map to the documented spacing constants."""
    profile = SpacingProfile.from_name("compact")

    assert profile.name == "compact"
    assert profile.line_gap == 16.0
    assert profile.line_table_gap == 24.0
    assert profile.entry_zone_gap == 32.0


def test_spacing_profile_unknown_name_raises():
    """Requesting an undefined profile should raise a ValueError."""
    try:
        SpacingProfile.from_name("unknown")
    except ValueError as exc:
        assert "Unknown spacing profile" in str(exc)
    else:
        raise AssertionError("expected ValueError for unknown profile")


def test_elk_layout_config_reflects_spacing_profile():
    """Derived ELK config should inherit measurements from the profile."""
    profile = SpacingProfile.from_name("standard")
    config = ElkLayoutConfig.from_spacing_profile(profile)

    assert config.spacing_layer >= 200.0
    assert config.spacing_node_node >= 80.0
    assert config.spacing_edge_edge == profile.line_gap


def test_spacing_profiles_have_distinct_values():
    """Each preset should occupy a distinct place on the spacing spectrum."""
    compact = SpacingProfile.from_name("compact")
    standard = SpacingProfile.from_name("standard")
    spacious = SpacingProfile.from_name("spacious")

    assert compact.line_gap < standard.line_gap < spacious.line_gap
    assert compact.line_table_gap < standard.line_table_gap < spacious.line_table_gap
    assert compact.entry_zone_gap < standard.entry_zone_gap < spacious.entry_zone_gap
