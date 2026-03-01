"""Integration smoke tests for the generation pipeline."""

from pathlib import Path

from wizerd import config, pipeline

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "dev/dumps/examples"


def test_pipeline_renders_svg(tmp_path):
    """Smoke test: running the pipeline should create a valid SVG file."""
    output_path = tmp_path / "diagram.svg"
    pipeline.run(
        config.AppConfig(
            input_path=EXAMPLES_DIR / "simple_schema.sql",
            output_path=output_path,
        )
    )

    assert output_path.exists()
    content = output_path.read_text()
    assert "<svg" in content
    assert "users" in content
    assert "posts" in content
    assert "fk-arrow" in content
    assert "username" in content  # column name rendered


def test_pipeline_can_include_edge_labels(tmp_path):
    """Enabling edge labels should cause FK names to appear in the SVG."""
    output_path = tmp_path / "diagram.svg"
    pipeline.run(
        config.AppConfig(
            input_path=EXAMPLES_DIR / "simple_schema.sql",
            output_path=output_path,
            show_edge_labels=True,
        )
    )

    content = output_path.read_text()
    assert "posts_user_id_fkey" in content


def test_pipeline_by_trunk_edge_color_mode(tmp_path):
    """By-trunk mode should introduce multiple edge colors in the output."""
    output_path = tmp_path / "diagram.svg"
    pipeline.run(
        config.AppConfig(
            input_path=EXAMPLES_DIR / "large_schema.sql",
            output_path=output_path,
            edge_color_mode=config.EdgeColorMode.BY_TRUNK,
        )
    )

    assert output_path.exists()
    content = output_path.read_text()
    assert "<svg" in content
    unique_colors = set()
    for line in content.split("\n"):
        if 'stroke="' in line and not line.strip().startswith("<?xml"):
            import re

            match = re.search(r'stroke="([^"]+)"', line)
            if match:
                unique_colors.add(match.group(1))
    assert len(unique_colors) > 1, "Expected multiple edge colors with by-trunk mode"


def test_pipeline_with_theme_overrides(tmp_path):
    """Theme overrides should influence the rendered canvas background."""
    output_path = tmp_path / "overridden.svg"
    overrides = config.ThemeOverrides(colors={"canvas_background": "#123456"})
    pipeline.run(
        config.AppConfig(
            input_path=EXAMPLES_DIR / "simple_schema.sql",
            output_path=output_path,
            theme_overrides=overrides,
        )
    )

    assert output_path.exists()
    content = output_path.read_text()
    assert 'fill="#123456"' in content  # Background rectangle should have this color
