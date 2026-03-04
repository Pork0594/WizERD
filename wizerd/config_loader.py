"""Configuration loading from multiple sources with precedence rules."""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import replace
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from wizerd import config
from wizerd.layout.spacing import SpacingProfile

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Handles loading and merging configuration from multiple sources.

    Configuration precedence (later overrides earlier):
    1. Default values in AppConfig
    2. Home config: ~/.wizerd.yaml (or .json, .yml)
    3. Project config: .wizerd.yaml in directory of input file or cwd
    4. Explicit config file: --config <file>
    5. CLI arguments

    Environment variables with prefix WIZERD_ are also supported
    and take precedence over config files but not CLI arguments.
    """

    CONFIG_FILE_NAMES = [
        ".wizerd.yaml",
        ".wizerd.yml",
        ".wizerd.json",
        "wizerd.yaml",
        "wizerd.yml",
        "wizerd.json",
    ]

    ENV_VAR_PREFIX = "WIZERD_"

    def __init__(self) -> None:
        """Track the home directory so tests can override it deterministically."""
        self._home_config_dir: Path | None = None

    @property
    def HOME_CONFIG_DIR(self) -> Path:
        """Get the home config directory, allowing for mocking in tests."""
        if self._home_config_dir is not None:
            return self._home_config_dir
        return Path.home()

    def set_home_dir(self, path: Path) -> None:
        """Set the home directory (for testing)."""
        self._home_config_dir = path

    def load(
        self,
        cli_args: dict[str, Any] | None = None,
        config_file: Path | None = None,
        input_path: Path | None = None,
    ) -> config.AppConfig:
        """Load configuration with proper precedence.

        Args:
            cli_args: Dictionary of CLI argument values
            config_file: Explicit path to config file
            input_path: Path to input schema file (for finding project config)

        Returns:
            Fully resolved AppConfig
        """
        cli_args = cli_args or {}

        base_config = self._create_default_config(input_path)

        home_config = self._load_home_config()
        if home_config:
            base_config = self._merge_dict_into_config(base_config, home_config)

        project_config = self._load_project_config(input_path)
        if project_config:
            base_config = self._merge_dict_into_config(base_config, project_config)

        if config_file:
            if not config_file.exists():
                raise FileNotFoundError(f"Config file not found: {config_file}")
            explicit_config = self._load_config_file(config_file)
            base_config = self._merge_dict_into_config(base_config, explicit_config)
            base_config.config_file = config_file

        env_config = self._load_env_vars()
        if env_config:
            base_config = self._merge_dict_into_config(base_config, env_config)

        cli_config = self._convert_cli_args(cli_args)
        final_config = self._merge_dict_into_config(base_config, cli_config)

        return final_config

    def _create_default_config(self, input_path: Path | None = None) -> config.AppConfig:
        """Create default AppConfig."""
        return config.AppConfig(
            input_path=input_path or Path("input.sql"),
            output_path=Path("diagram.svg"),
            show_edge_labels=False,
            spacing_profile=SpacingProfile.from_name("standard"),
            edge_color_mode=config.EdgeColorMode.SINGLE,
            theme_name="default-dark",
        )

    def _load_home_config(self) -> dict[str, Any] | None:
        """Load config from user's home directory."""
        for name in self.CONFIG_FILE_NAMES:
            config_path = self.HOME_CONFIG_DIR / name
            if config_path.exists():
                logger.debug(f"Loading home config from {config_path}")
                return self._load_config_file(config_path)
        return None

    def _load_project_config(self, input_path: Path | None) -> dict[str, Any] | None:
        """Load config from project directory (near input file or cwd)."""
        search_dirs: list[Path] = []

        if input_path:
            search_dirs.append(input_path.parent)

        search_dirs.append(Path.cwd())

        for search_dir in search_dirs:
            for name in self.CONFIG_FILE_NAMES:
                config_path = search_dir / name
                if config_path.exists() and config_path != self.HOME_CONFIG_DIR / name:
                    logger.debug(f"Loading project config from {config_path}")
                    return self._load_config_file(config_path)

        return None

    def _load_config_file(self, path: Path) -> dict[str, Any]:
        """Load configuration from a YAML or JSON file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            content = self._substitute_env_vars(content)

            if path.suffix in {".yaml", ".yml"}:
                parsed = yaml.safe_load(content)
            elif path.suffix == ".json":
                parsed = json.loads(content)
            else:
                try:
                    parsed = yaml.safe_load(content)
                except yaml.YAMLError:
                    parsed = json.loads(content)

        except FileNotFoundError:
            logger.warning(f"Config file not found: {path}")
            return {}
        except (yaml.YAMLError, json.JSONDecodeError) as exc:
            raise ValueError(f"Failed to parse config file {path}: {exc}") from exc

        if parsed is None:
            return {}
        if not isinstance(parsed, dict):
            raise ValueError(f"Config file {path} must contain a mapping at the top level")

        return parsed

    def _substitute_env_vars(self, content: str) -> str:
        """Substitute ${VAR} and ${VAR:-default} patterns with env vars."""
        pattern = r"\$\{([^}:]+)(?::-([^}]*))?\}"

        def replacer(match: re.Match) -> str:
            """Return the environment variable value or the provided default."""
            var_name = match.group(1)
            default_value = match.group(2)
            env_value = os.getenv(var_name)
            return env_value if env_value is not None else (default_value or "")

        return re.sub(pattern, replacer, content)

    def _load_env_vars(self) -> dict[str, Any]:
        """Load configuration from environment variables."""
        env_config: dict[str, Any] = {}

        prefix = self.ENV_VAR_PREFIX
        env_mappings = {
            f"{prefix}OUTPUT": "output_path",
            f"{prefix}SHOW_EDGE_LABELS": "show_edge_labels",
            f"{prefix}SPACING_PROFILE": "spacing_profile",
            f"{prefix}EDGE_COLOR_MODE": "edge_color_mode",
            f"{prefix}COLOR_BY_TRUNK": "color_by_trunk",
            f"{prefix}THEME": "theme_name",
        }

        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if config_key in {"show_edge_labels", "color_by_trunk"}:
                    env_config[config_key] = self._parse_bool(value)
                else:
                    env_config[config_key] = value

        input_env = os.getenv(f"{prefix}INPUT")
        if input_env:
            env_config["input_path"] = input_env

        spacing_keys = {
            f"{prefix}SPACING_COLUMN_GAP": "column_gap",
            f"{prefix}SPACING_ROW_GAP": "row_gap",
            f"{prefix}SPACING_COMPONENT_GAP": "component_gap",
            f"{prefix}SPACING_EDGE_TO_NODE_GAP": "edge_to_node_gap",
            f"{prefix}SPACING_EDGE_GAP": "edge_gap",
            f"{prefix}SPACING_MARGIN": "margin",
        }
        spacing_values: dict[str, float] = {}
        for env_var, spacing_key in spacing_keys.items():
            raw_value = os.getenv(env_var)
            if raw_value is None:
                continue
            try:
                spacing_values[spacing_key] = float(raw_value)
            except ValueError as exc:
                raise ValueError(f"Invalid float for {env_var}: {raw_value}") from exc

        if spacing_values:
            env_config["spacing"] = spacing_values

        return env_config

    def _parse_bool(self, value: str) -> bool:
        """Parse boolean value from string."""
        return value.lower() in ("true", "yes", "1", "on", "enabled")

    def _convert_cli_args(self, cli_args: dict[str, Any]) -> dict[str, Any]:
        """Convert CLI args to config dict format."""
        converted: dict[str, Any] = {}

        if "output" in cli_args and cli_args["output"] is not None:
            converted["output_path"] = cli_args["output"]
        if "show_edge_labels" in cli_args:
            converted["show_edge_labels"] = cli_args["show_edge_labels"]
        if "spacing_profile" in cli_args and cli_args["spacing_profile"] is not None:
            converted["spacing_profile"] = cli_args["spacing_profile"]
        if "color_by_trunk" in cli_args:
            converted["edge_color_mode"] = "by-trunk" if cli_args["color_by_trunk"] else "single"
        if "theme" in cli_args and cli_args["theme"] is not None:
            converted["theme_name"] = cli_args["theme"]
        if "show_indexes" in cli_args:
            converted["show_indexes"] = cli_args["show_indexes"]
        if "show_views" in cli_args:
            converted["show_views"] = cli_args["show_views"]
        if "show_sequences" in cli_args:
            converted["show_sequences"] = cli_args["show_sequences"]

        return converted

    def _merge_dict_into_config(
        self,
        base: config.AppConfig,
        override: dict[str, Any],
    ) -> config.AppConfig:
        """Merge dict into AppConfig, with override taking precedence."""
        result = replace(
            base,
            spacing_profile=SpacingProfile(
                name=base.spacing_profile.name,
                column_gap=base.spacing_profile.column_gap,
                row_gap=base.spacing_profile.row_gap,
                component_gap=base.spacing_profile.component_gap,
                edge_to_node_gap=base.spacing_profile.edge_to_node_gap,
                edge_gap=base.spacing_profile.edge_gap,
                margin=base.spacing_profile.margin,
            ),
            theme_overrides=config.ThemeOverrides(
                colors=dict(base.theme_overrides.colors),
                typography=dict(base.theme_overrides.typography),
                dimensions=dict(base.theme_overrides.dimensions),
                edges=dict(base.theme_overrides.edges),
            ),
            theme_inline=dict(base.theme_inline) if base.theme_inline else None,
            custom_spacing=(
                config.CustomSpacing(
                    column_gap=base.custom_spacing.column_gap,
                    row_gap=base.custom_spacing.row_gap,
                    component_gap=base.custom_spacing.component_gap,
                    edge_to_node_gap=base.custom_spacing.edge_to_node_gap,
                    edge_gap=base.custom_spacing.edge_gap,
                    margin=base.custom_spacing.margin,
                )
                if base.custom_spacing
                else None
            ),
        )

        normalized_items = [(key, key.replace("-", "_"), value) for key, value in override.items()]

        for _, norm_key, value in normalized_items:
            if value is None:
                continue

            if norm_key == "spacing_profile":
                result.spacing_profile = SpacingProfile.from_name(str(value))
                result.custom_spacing = None

        for _original_key, norm_key, value in normalized_items:
            if value is None or norm_key == "spacing_profile":
                continue

            if norm_key in ("output", "output_path"):
                result.output_path = Path(value)
            elif norm_key in ("input", "input_path", "schema"):
                result.input_path = Path(value)
            elif norm_key == "show_edge_labels":
                result.show_edge_labels = bool(value)
            elif norm_key == "show_indexes":
                result.show_indexes = bool(value)
            elif norm_key == "show_views":
                result.show_views = bool(value)
            elif norm_key == "show_sequences":
                result.show_sequences = bool(value)
            elif norm_key == "edge_color_mode":
                if isinstance(value, bool):
                    result.edge_color_mode = (
                        config.EdgeColorMode.BY_TRUNK if value else config.EdgeColorMode.SINGLE
                    )
                else:
                    try:
                        result.edge_color_mode = config.EdgeColorMode(str(value))
                    except ValueError as exc:
                        raise ValueError(f"Invalid edge color mode '{value}'") from exc
            elif norm_key == "color_by_trunk":
                result.edge_color_mode = (
                    config.EdgeColorMode.BY_TRUNK if bool(value) else config.EdgeColorMode.SINGLE
                )
            elif norm_key in ("theme", "theme_name"):
                if isinstance(value, dict):
                    result.theme_inline = value
                    if "name" in value and isinstance(value["name"], str):
                        result.theme_name = value["name"]
                else:
                    result.theme_name = str(value)
                    result.theme_inline = None
            elif norm_key == "spacing" and isinstance(value, dict):
                incoming = config.CustomSpacing.from_mapping(value)
                if not incoming.to_dict():
                    continue

                if result.custom_spacing is None:
                    result.custom_spacing = config.CustomSpacing()

                for field_name in (
                    "column_gap",
                    "row_gap",
                    "component_gap",
                    "edge_to_node_gap",
                    "edge_gap",
                    "margin",
                ):
                    override_value = getattr(incoming, field_name)
                    if override_value is not None:
                        setattr(result.custom_spacing, field_name, override_value)

                base_profile = SpacingProfile.from_name(result.spacing_profile.name)
                result.spacing_profile = config.AppConfig._apply_custom_spacing(
                    base_profile,
                    result.custom_spacing,
                )
            elif norm_key == "theme_overrides" and isinstance(value, dict):
                if "colors" in value and isinstance(value["colors"], dict):
                    result.theme_overrides.colors.update(value["colors"])
                if "typography" in value and isinstance(value["typography"], dict):
                    result.theme_overrides.typography.update(value["typography"])
                if "dimensions" in value and isinstance(value["dimensions"], dict):
                    result.theme_overrides.dimensions.update(value["dimensions"])
                if "edges" in value and isinstance(value["edges"], dict):
                    result.theme_overrides.edges.update(value["edges"])
            elif norm_key == "config_file" and value:
                result.config_file = Path(value)

        return result

    def find_config_files(self, path: Path | None = None) -> list[Path]:
        """Find all available config files for a given path.

        Args:
            path: Input file path to search near (optional)

        Returns:
            List of config file paths in order they would be loaded
        """
        found: list[Path] = []

        for name in self.CONFIG_FILE_NAMES:
            home_config = self.HOME_CONFIG_DIR / name
            if home_config.exists():
                found.append(home_config)

        search_dirs: list[Path] = []
        if path and path.exists():
            search_dirs.append(path.parent)
        search_dirs.append(Path.cwd())

        for search_dir in search_dirs:
            for name in self.CONFIG_FILE_NAMES:
                config_path = search_dir / name
                if config_path.exists() and config_path not in found:
                    found.append(config_path)

        return found
