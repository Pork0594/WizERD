#!/usr/bin/env python3
"""
Generate all documentation sample images for WizERD.
Creates SVG and PNG versions of various theme/spacing/feature combinations.

Usage:
    python3 scripts/generate_docs_images.py

Or via Makefile:
    make docs-images

Requirements:
    - Virtual environment with wizerd and cairosvg installed
    - Run 'make install-all' first to set up the environment
"""

import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
SCHEMA_PATH = PROJECT_DIR / "dev/dumps/examples/simple_schema.sql"
HERO_SCHEMA_PATH = PROJECT_DIR / "dev/dumps/examples/schema.sql"
OUTPUT_DIR = PROJECT_DIR / "docs/images"
VENV_PYTHON = PROJECT_DIR / ".venv/bin/python"
VENV_WIZERD = PROJECT_DIR / ".venv/bin/wizerd"


THEMES = [
    "default-dark",
    "dracula",
    "forest",
    "hacker",
    "high-contrast",
    "light",
    "minimal",
    "monochrome",
    "nord",
    "ocean",
    "soft",
    "solarized",
    "sunset",
]

SPACING_PROFILES = [
    "compact",
    "standard",
    "spacious",
]


FEATURES = [
    ("default", []),
    ("edge-labels", ["--show-edge-labels"]),
    ("color-by-trunk", ["--color-by-trunk"]),
]


def run_wizerd(args: list[str]) -> bool:
    """Run wizerd command and return success status."""
    cmd = [str(VENV_WIZERD)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_DIR)
    if result.returncode != 0:
        print(f"  ERROR: {' '.join(cmd)}")
        print(f"  {result.stderr}")
        return False
    return True


def convert_svg_to_png(svg_path: Path) -> None:
    """Convert SVG to PNG using cairosvg via venv python."""
    png_path = svg_path.with_suffix(".png")
    convert_script = f"""
import cairosvg
cairosvg.svg2png(url="{svg_path}", write_to="{png_path}", scale=2)
"""
    result = subprocess.run(
        [str(VENV_PYTHON), "-c", convert_script], capture_output=True, text=True, cwd=PROJECT_DIR
    )
    if result.returncode != 0:
        print(f"  ERROR converting {svg_path}: {result.stderr}")
    else:
        print(f"  Converted: {png_path.name}")


def generate_sample(
    schema_path: str,
    name: str,
    theme: str,
    spacing: str = "standard",
    extra_args: list[str] | None = None,
) -> list[Path]:
    """Generate a single sample image."""
    extra_args = extra_args or []

    svg_name = f"sample-{name}.svg"
    svg_path = OUTPUT_DIR / svg_name

    args = [
        "generate",
        str(schema_path),
        "-o",
        str(svg_path),
        "-t",
        theme,
        "-w",
        spacing,
    ] + extra_args

    print(f"Generating: {name} (theme={theme}, spacing={spacing})")

    if not run_wizerd(args):
        return []

    convert_svg_to_png(svg_path)

    os.remove(svg_path)

    return [svg_path, svg_path.with_suffix(".png")]


def main():
    os.chdir(PROJECT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("WizERD Documentation Image Generator")
    print("=" * 60)
    print()

    generated = []

    # Hero Image
    generated.extend(generate_sample(HERO_SCHEMA_PATH, "hero-image", "default-dark"))

    # Key theme showcases
    for theme in THEMES:
        name = theme.replace("-", "-")
        generated.extend(generate_sample(SCHEMA_PATH, name, theme))

    # Spacing profiles with default theme
    for spacing in SPACING_PROFILES:
        name = f"spacing-{spacing}"
        generated.extend(generate_sample(SCHEMA_PATH, name, "default-dark", spacing))

    # Feature showcases
    for feature_name, feature_args in FEATURES:
        if feature_args:  # Skip "default"
            generated.extend(
                generate_sample(
                    SCHEMA_PATH, f"feature-{feature_name}", "default-dark", "standard", feature_args
                )
            )

    print()
    print("=" * 60)
    print(f"Generated {len(generated)} images:")
    for f in sorted(generated):
        print(f"  {f}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
