"""Tests for the theme system."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from wizerd.theme import Theme, ThemeColors
from wizerd.theme.loader import (
    _looks_like_file_path,
    cli_overrides_to_dict,
    get_builtin_theme,
    list_builtin_themes,
    load_theme,
    load_theme_from_file,
)


class TestTheme:
    """Validate core Theme serialization and merging behavior."""

    def test_theme_to_dict_roundtrip(self):
        """Theme serialization should faithfully round-trip complex objects."""
        theme = Theme(
            name="test-theme",
            description="Test theme",
            is_dark=True,
            colors=ThemeColors(canvas_background="#000000"),
        )
        data = theme.to_dict()
        restored = Theme.from_dict(data)

        assert restored.name == theme.name
        assert restored.description == theme.description
        assert restored.is_dark == theme.is_dark
        assert restored.colors.canvas_background == theme.colors.canvas_background

    def test_theme_merge_overrides(self):
        """`Theme.merge` should overlay overrides without dropping defaults."""
        theme = Theme(
            name="test-theme",
            description="Test theme",
            is_dark=True,
            colors=ThemeColors(canvas_background="#000000", table_background="#111111"),
        )

        merged = theme.merge({"colors": {"canvas_background": "#ffffff"}})

        assert merged.name == "test-theme"
        assert merged.colors.canvas_background == "#ffffff"
        assert merged.colors.table_background == "#111111"

    def test_theme_merge_rejects_unknown_keys(self):
        """Theme.merge should raise when overrides point to unknown keys."""
        theme = Theme(name="test", description="", is_dark=True)
        with pytest.raises(ValueError):
            theme.merge({"unknown": {}})


class TestThemePresets:
    """Ensure built-in presets stay registered and well-formed."""

    def test_get_builtin_theme(self):
        """Requesting default-dark should return the canonical dark theme."""
        theme = get_builtin_theme("default-dark")
        assert theme.name == "default-dark"
        assert theme.is_dark is True

    def test_get_builtin_theme_light(self):
        """Light preset should advertise itself as a light theme."""
        theme = get_builtin_theme("light")
        assert theme.name == "light"
        assert theme.is_dark is False

    def test_get_builtin_theme_unknown_raises(self):
        """Unknown theme names should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown theme"):
            get_builtin_theme("nonexistent")

    def test_list_builtin_themes(self):
        """The registry should expose a catalog of known presets."""
        themes = list_builtin_themes()
        assert "default-dark" in themes
        assert "light" in themes
        assert "monochrome" in themes
        assert len(themes) >= 5

    def test_all_preset_themes_have_required_fields(self):
        """Each preset must define colors, typography, dimensions, and edges."""
        themes = list_builtin_themes()
        for name, theme in themes.items():
            assert theme.name == name
            assert theme.description
            assert theme.colors is not None
            assert theme.typography is not None
            assert theme.dimensions is not None
            assert theme.edges is not None


class TestThemeLoader:
    """Cover the different theme loading code paths."""

    def test_load_theme_from_file(self, tmp_path):
        """Loading from JSON should hydrate a Theme with those values."""
        theme_data = {
            "name": "file-theme",
            "description": "From file",
            "is_dark": True,
            "colors": {"canvas_background": "#123456"},
        }
        theme_file = tmp_path / "theme.json"
        theme_file.write_text(json.dumps(theme_data))

        theme = load_theme_from_file(theme_file)
        assert theme.name == "file-theme"
        assert theme.colors.canvas_background == "#123456"

    def test_load_theme_from_yaml_file(self, tmp_path):
        """YAML theme files should also be supported."""
        theme_data = {
            "name": "yaml-theme",
            "description": "YAML",
            "colors": {"canvas_background": "#abcdef"},
        }
        theme_file = tmp_path / "theme.yaml"
        theme_file.write_text(yaml.dump(theme_data))

        theme = load_theme_from_file(theme_file)
        assert theme.name == "yaml-theme"
        assert theme.colors.canvas_background == "#abcdef"

    def test_load_theme_from_file_not_found(self):
        """Missing JSON files should raise a ValueError with context."""
        with pytest.raises(ValueError, match="Theme file not found"):
            load_theme_from_file(Path("/nonexistent/theme.json"))

    def test_load_theme_from_file_invalid_json(self, tmp_path):
        """Invalid JSON should surface a ValueError rather than crashing."""
        theme_file = tmp_path / "bad.json"
        theme_file.write_text("{invalid")

        with pytest.raises(ValueError, match="Invalid JSON"):
            load_theme_from_file(theme_file)

    def test_load_theme_by_name(self):
        """`load_theme` should resolve built-in names when no file is given."""
        theme = load_theme(theme_name="light")
        assert theme.name == "light"

    def test_load_theme_with_overrides(self):
        """Inline overrides should tweak the base theme colors."""
        theme = load_theme(
            theme_name="default-dark", theme_overrides={"colors": {"canvas_background": "#ff0000"}}
        )
        assert theme.colors.canvas_background == "#ff0000"

    def test_load_theme_file_not_found(self):
        """File-looking names should still throw when the file is absent."""
        with pytest.raises(ValueError, match="Theme file not found"):
            load_theme(theme_name="/nonexistent.json")

    def test_load_theme_default(self):
        """No arguments should yield the default-dark theme."""
        theme = load_theme()
        assert theme.name == "default-dark"


class TestPathDetection:
    """Verify heuristics that decide whether a string is a path."""

    def test_looks_like_file_path_absolute(self):
        """Absolute paths should be treated as file references."""
        assert _looks_like_file_path("/path/to/theme.json") is True
        assert _looks_like_file_path("/tmp/theme.json") is True

    def test_looks_like_file_path_relative(self):
        """Relative paths should also be considered file references."""
        assert _looks_like_file_path("./theme.json") is True
        assert _looks_like_file_path("../theme.json") is True

    def test_looks_like_file_path_json_suffix(self):
        """A .json suffix alone should trigger file detection."""
        assert _looks_like_file_path("theme.json") is True

    def test_looks_like_file_path_not(self):
        """Preset names should not be mistaken for file paths."""
        assert _looks_like_file_path("default-dark") is False
        assert _looks_like_file_path("light") is False
        assert _looks_like_file_path("monochrome") is False


class TestCLIOverrides:
    """Check how CLI overrides translate into nested theme updates."""

    def test_cli_overrides_basic(self):
        """Specified CLI colors should map into the nested override dict."""
        result = cli_overrides_to_dict(
            canvas_bg="#ff0000",
            body_text="#00ff00",
        )

        assert result["colors"]["canvas_background"] == "#ff0000"
        assert result["colors"]["table_body_text"] == "#00ff00"

    def test_cli_overrides_empty(self):
        """No CLI overrides should return an empty dict."""
        result = cli_overrides_to_dict()
        assert result == {}

    def test_cli_overrides_partial(self):
        """Unknown options should not populate unrelated override keys."""
        result = cli_overrides_to_dict(pk_color="#ff0000")

        assert result["colors"]["pk_marker"] == "#ff0000"
        assert "table_background" not in result.get("colors", {})


class TestThemeToRendererTheme:
    """Ensure `Theme.to_renderer_theme` mirrors the source theme."""

    def test_to_renderer_theme(self):
        """`Theme.to_renderer_theme` should mirror all key display properties."""
        theme = get_builtin_theme("default-dark")
        renderer_theme = theme.to_renderer_theme()

        assert renderer_theme.name == "default-dark"
        assert renderer_theme.canvas_background == theme.colors.canvas_background
        assert renderer_theme.font_size_header == theme.typography.font_size_header
        assert renderer_theme.row_height == theme.dimensions.row_height
