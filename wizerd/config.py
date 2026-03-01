"""Application configuration models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from wizerd.layout.spacing import SpacingProfile


class EdgeColorMode(str, Enum):
    """Controls whether foreign key trunks share colors or get unique hues."""

    SINGLE = "single"
    BY_TRUNK = "by-trunk"


@dataclass
class ThemeOverrides:
    """Theme override values that can be set via config file."""

    colors: dict[str, Any] = field(default_factory=dict)
    typography: dict[str, Any] = field(default_factory=dict)
    dimensions: dict[str, Any] = field(default_factory=dict)
    edges: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert overrides to a nested dictionary for Theme.merge()."""
        overrides: dict[str, Any] = {}
        if self.colors:
            overrides["colors"] = self.colors
        if self.typography:
            overrides["typography"] = self.typography
        if self.dimensions:
            overrides["dimensions"] = self.dimensions
        if self.edges:
            overrides["edges"] = self.edges
        return overrides


@dataclass
class CustomSpacing:
    """Custom spacing values that override the profile."""

    column_gap: float | None = None
    row_gap: float | None = None
    component_gap: float | None = None
    edge_to_node_gap: float | None = None
    edge_gap: float | None = None
    margin: float | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "CustomSpacing":
        """Build a CustomSpacing object from a mapping using the canonical keys.

        Accepts keys with hyphens or underscores but does not support legacy names.
        """
        kwargs: dict[str, float] = {}
        allowed = {
            "column_gap",
            "row_gap",
            "component_gap",
            "edge_to_node_gap",
            "edge_gap",
            "margin",
        }
        for raw_key, value in data.items():
            if value is None:
                continue
            key = raw_key.replace("-", "_")
            if key not in allowed:
                continue
            kwargs[key] = float(value)
        return cls(**kwargs)

    def to_dict(self) -> dict[str, float]:
        """Serialize only the spacing values that were explicitly set."""
        result: dict[str, float] = {}
        if self.column_gap is not None:
            result["column_gap"] = self.column_gap
        if self.row_gap is not None:
            result["row_gap"] = self.row_gap
        if self.component_gap is not None:
            result["component_gap"] = self.component_gap
        if self.edge_to_node_gap is not None:
            result["edge_to_node_gap"] = self.edge_to_node_gap
        if self.edge_gap is not None:
            result["edge_gap"] = self.edge_gap
        if self.margin is not None:
            result["margin"] = self.margin
        return result


@dataclass
class AppConfig:
    """Represents runtime configuration for a diagram generation job.

    Attributes:
        input_path: Path to the input SQL schema file.
        output_path: Path for the output diagram file.
        show_edge_labels: Whether to render FK names along connector lines.
        spacing_profile: Spacing preset (compact, standard, spacious) or custom values.
        edge_color_mode: How to color edges (single color or by trunk).
        theme_name: Name of built-in theme or path to custom theme.
        theme_overrides: Inline theme customization values.
        custom_spacing: Custom spacing values that override the profile.
        config_file: Path to the config file that was loaded (if any).
    """

    input_path: Path
    output_path: Path
    show_edge_labels: bool = False
    spacing_profile: SpacingProfile = field(default_factory=SpacingProfile.default)
    edge_color_mode: EdgeColorMode = EdgeColorMode.SINGLE
    theme_name: str = "default-dark"
    theme_inline: dict[str, Any] | None = None
    theme_overrides: ThemeOverrides = field(default_factory=ThemeOverrides)
    custom_spacing: CustomSpacing | None = None
    config_file: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary for serialization."""
        result: dict[str, Any] = {
            "input_path": str(self.input_path),
            "output_path": str(self.output_path),
            "show_edge_labels": self.show_edge_labels,
            "spacing_profile": self.spacing_profile.name,
            "edge_color_mode": self.edge_color_mode.value,
            "theme_name": self.theme_name,
            "config_file": str(self.config_file) if self.config_file else None,
        }
        if self.theme_inline is not None:
            result["theme_inline"] = self.theme_inline
        if self.custom_spacing:
            spacing_payload = self.custom_spacing.to_dict()
            if spacing_payload:
                result["spacing"] = spacing_payload

        overrides_dict = self.theme_overrides.to_dict()
        if overrides_dict:
            result["theme_overrides"] = overrides_dict
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfig":
        """Create config from dictionary."""
        spacing_profile = SpacingProfile.from_name(data.get("spacing_profile", "standard"))

        if "spacing" in data:
            spacing_data = data["spacing"]
            custom_spacing = CustomSpacing.from_mapping(spacing_data)
            spacing_profile = cls._apply_custom_spacing(spacing_profile, custom_spacing)
        else:
            custom_spacing = None

        theme_overrides_data = data.get("theme_overrides", {})
        theme_overrides = ThemeOverrides(
            colors=theme_overrides_data.get("colors", {}),
            typography=theme_overrides_data.get("typography", {}),
            dimensions=theme_overrides_data.get("dimensions", {}),
            edges=theme_overrides_data.get("edges", {}),
        )

        return cls(
            input_path=Path(data["input_path"]),
            output_path=Path(data["output_path"]),
            show_edge_labels=data.get("show_edge_labels", False),
            spacing_profile=spacing_profile,
            edge_color_mode=EdgeColorMode(data.get("edge_color_mode", "single")),
            theme_name=data.get("theme_name", "default-dark"),
            theme_inline=data.get("theme_inline"),
            theme_overrides=theme_overrides,
            custom_spacing=custom_spacing,
            config_file=Path(data["config_file"]) if data.get("config_file") else None,
        )

    @staticmethod
    def _apply_custom_spacing(profile: SpacingProfile, custom: CustomSpacing) -> SpacingProfile:
        """Apply custom spacing values to a profile."""
        return SpacingProfile(
            name=profile.name,
            column_gap=custom.column_gap if custom.column_gap is not None else profile.column_gap,
            row_gap=custom.row_gap if custom.row_gap is not None else profile.row_gap,
            component_gap=(
                custom.component_gap if custom.component_gap is not None else profile.component_gap
            ),
            edge_to_node_gap=(
                custom.edge_to_node_gap
                if custom.edge_to_node_gap is not None
                else profile.edge_to_node_gap
            ),
            edge_gap=custom.edge_gap if custom.edge_gap is not None else profile.edge_gap,
            margin=custom.margin if custom.margin is not None else profile.margin,
        )


@dataclass
class ConfigValidationResult:
    """Result of configuration validation."""

    is_valid: bool
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def has_issues(self) -> bool:
        """Check if there are any warnings or errors."""
        return len(self.warnings) > 0 or len(self.errors) > 0


class ConfigValidator:
    """Validates configuration and provides helpful error messages."""

    VALID_SPACING_PROFILES = {"compact", "standard", "spacious"}
    VALID_EDGE_COLOR_MODES = {"single", "by-trunk"}

    def validate(self, config: AppConfig, *, strict_paths: bool = True) -> ConfigValidationResult:
        """Validate configuration and return result with warnings/errors."""
        warnings: list[str] = []
        errors: list[str] = []

        self._validate_input_file(config, errors, strict_paths)
        self._validate_output_path(config, errors, warnings, strict_paths)
        self._validate_theme(config, errors, warnings)
        self._validate_spacing_profile(config, errors)
        self._validate_edge_color_mode(config, errors)

        return ConfigValidationResult(
            is_valid=len(errors) == 0,
            warnings=warnings,
            errors=errors,
        )

    def _validate_input_file(self, config: AppConfig, errors: list[str], strict: bool) -> None:
        """Validate input file exists and is readable."""
        if not strict:
            return
        if config.input_path and not config.input_path.exists():
            errors.append(f"Input file not found: {config.input_path}")
        elif config.input_path and not config.input_path.is_file():
            errors.append(f"Input path is not a file: {config.input_path}")

    def _validate_output_path(
        self,
        config: AppConfig,
        errors: list[str],
        warnings: list[str],
        strict: bool,
    ) -> None:
        """Validate output path is writable."""
        if config.output_path:
            parent = config.output_path.parent
            if not parent.exists():
                if strict:
                    try:
                        parent.mkdir(parents=True, exist_ok=True)
                    except OSError as exc:
                        errors.append(f"Failed to create output directory {parent}: {exc}")
                else:
                    warnings.append(f"Output directory does not exist yet: {parent}")
            elif not parent.is_dir():
                errors.append(f"Output path parent is not a directory: {parent}")

    def _validate_theme(self, config: AppConfig, errors: list[str], warnings: list[str]) -> None:
        """Validate theme configuration."""
        if config.theme_inline is not None:
            from wizerd.theme import Theme  # Local import to avoid cycle

            try:
                Theme.from_dict(config.theme_inline)
            except ValueError as exc:
                errors.append(f"Invalid inline theme definition: {exc}")

    def _validate_spacing_profile(self, config: AppConfig, errors: list[str]) -> None:
        """Validate spacing profile name."""
        if config.spacing_profile.name not in self.VALID_SPACING_PROFILES:
            errors.append(
                f"Invalid spacing profile '{config.spacing_profile.name}'. "
                f"Expected one of: {', '.join(sorted(self.VALID_SPACING_PROFILES))}."
            )

    def _validate_edge_color_mode(self, config: AppConfig, errors: list[str]) -> None:
        """Validate edge color mode."""
        if config.edge_color_mode.value not in self.VALID_EDGE_COLOR_MODES:
            errors.append(
                f"Invalid edge color mode '{config.edge_color_mode.value}'. "
                f"Expected one of: {', '.join(sorted(self.VALID_EDGE_COLOR_MODES))}."
            )

    def validate_or_raise(self, config: AppConfig, *, strict_paths: bool = True) -> None:
        """Raise ValueError with helpful message if config is invalid."""
        result = self.validate(config, strict_paths=strict_paths)
        if result.errors:
            error_msg = self._format_errors(result.errors)
            raise ValueError(error_msg)

    def _format_errors(self, errors: list[str]) -> str:
        """Format validation errors with helpful context."""
        lines = ["Configuration validation failed:"]
        for error in errors:
            lines.append(f"  • {error}")
        lines.append("")
        lines.append("Run 'wizerd validate --help' for more information on configuration options.")
        return "\n".join(lines)
