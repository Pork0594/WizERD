"""Packaged template assets for WizERD."""

from __future__ import annotations

from importlib import resources


def read_text(relative_path: str) -> str:
    """Return the contents of a template file shipped with the package."""

    package = resources.files(__name__)
    template_path = package.joinpath(relative_path)
    return template_path.read_text(encoding="utf-8")
