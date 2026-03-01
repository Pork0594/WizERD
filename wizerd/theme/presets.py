"""Built-in theme presets for WizERD."""

from __future__ import annotations

import json
from importlib import resources

from wizerd.theme import Theme


def load_presets() -> list[Theme]:
    """Load all built-in theme presets from the packaged JSON file."""

    data_path = resources.files(__package__).joinpath("presets.json")
    payload = json.loads(data_path.read_text(encoding="utf-8"))
    return [Theme.from_dict(item) for item in payload]
