"""Tests for the theme system."""

from __future__ import annotations

import pytest

from wizerd.theme import Theme, ThemeColors
from wizerd.theme.loader import (
    cli_overrides_to_dict,
    get_builtin_theme,
    list_builtin_themes,
    load_theme,
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

    def test_load_theme_default(self):
        """No arguments should yield the default-dark theme."""
        theme = load_theme()
        assert theme.name == "default-dark"

    def test_load_theme_inline(self):
        """Inline theme definition should be used directly."""
        inline_theme = {
            "name": "inline-theme",
            "is_dark": True,
            "colors": {"canvas_background": "#123456"},
        }
        theme = load_theme(theme_inline=inline_theme)
        assert theme.name == "inline-theme"
        assert theme.colors.canvas_background == "#123456"


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
