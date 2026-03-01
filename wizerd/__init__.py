"""WizERD package initialization."""

from __future__ import annotations

from typing import Any

__all__ = ["app"]


def __getattr__(name: str) -> Any:
    if name == "app":
        from .cli import app as typer_app

        return typer_app
    raise AttributeError(f"module 'wizerd' has no attribute '{name}'")
