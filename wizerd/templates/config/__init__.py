"""Configuration templates bundled with WizERD."""

from __future__ import annotations

from importlib import resources
from typing import Dict

TEMPLATE_FILES: Dict[str, str] = {
    "default": "default.yaml",
    "minimal": "minimal.yaml",
    "full": "full.yaml",
}


def load_template(name: str) -> str:
    """Load a named configuration template as text."""

    if name not in TEMPLATE_FILES:
        raise ValueError(
            f"Unknown template '{name}'. Available templates: {', '.join(sorted(TEMPLATE_FILES))}."
        )

    package = resources.files(__name__)
    template_path = package.joinpath(TEMPLATE_FILES[name])
    return template_path.read_text(encoding="utf-8")
