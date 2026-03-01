"""Tests for configuration loading."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import cast
from unittest.mock import patch

import pytest
import yaml

from wizerd import config
from wizerd.config_loader import ConfigLoader
from wizerd.layout.spacing import SpacingProfile


class TestConfigLoaderDefaults:
    """Tests for default configuration loading."""

    def test_load_returns_default_values(self):
        """Ensure loader falls back to baked-in defaults when no inputs exist."""
        loader = ConfigLoader()
        cfg = loader.load()

        assert cfg.output_path == Path("diagram.svg")
        assert cfg.show_edge_labels is False
        assert cfg.spacing_profile.name == "standard"
        assert cfg.edge_color_mode == config.EdgeColorMode.SINGLE
        assert cfg.theme_name == "default-dark"

    def test_load_with_cli_args_overrides_defaults(self):
        """CLI switches should win over the default dataclass values."""
        loader = ConfigLoader()
        cfg = loader.load(
            cli_args={
                "output": Path("custom.svg"),
                "show_edge_labels": True,
                "spacing_profile": "compact",
                "theme": "light",
            }
        )

        assert cfg.output_path == Path("custom.svg")
        assert cfg.show_edge_labels is True
        assert cfg.spacing_profile.name == "compact"
        assert cfg.theme_name == "light"


class TestConfigLoaderHomeConfig:
    """Tests for home config file loading."""

    def test_loads_home_config_when_exists(self):
        """Home-level dotfile should seed configuration before other sources."""
        with tempfile.TemporaryDirectory() as tmpdir:
            home_config_path = Path(tmpdir) / ".wizerd.yaml"
            with open(home_config_path, "w") as f:
                yaml.dump({"output": "home-output.svg", "theme": "light"}, f)

            loader = ConfigLoader()
            loader.set_home_dir(Path(tmpdir))
            # Create dummy input file in temp dir to avoid picking up other configs
            dummy_input = Path(tmpdir) / "dummy.sql"
            dummy_input.touch()
            cfg = loader.load(input_path=dummy_input)

            assert cfg.output_path == Path("home-output.svg")
            assert cfg.theme_name == "light"

    def test_home_config_priority(self):
        """Explicit CLI args should override a discovered home config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            home_config_path = Path(tmpdir) / ".wizerd.yaml"
            with open(home_config_path, "w") as f:
                yaml.dump({"output": "home.svg"}, f)

            loader = ConfigLoader()
            loader.set_home_dir(Path(tmpdir))
            # Create dummy input file to avoid picking up other configs
            dummy_input = Path(tmpdir) / "dummy.sql"
            dummy_input.touch()
            cfg = loader.load(
                cli_args={"output": Path("cli.svg")},
                input_path=dummy_input,
            )

            assert cfg.output_path == Path("cli.svg")


class TestConfigLoaderProjectConfig:
    """Tests for project config file loading."""

    def test_loads_project_config_near_input(self):
        """Project configs sitting next to the schema should be picked up."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()

            project_config = project_dir / ".wizerd.yaml"
            with open(project_config, "w") as f:
                yaml.dump({"output": "project-output.svg"}, f)

            schema_file = project_dir / "schema.sql"
            schema_file.touch()

            loader = ConfigLoader()
            loader.set_home_dir(Path("/nonexistent"))  # Don't find home config
            cfg = loader.load(input_path=schema_file)

            assert cfg.output_path == Path("project-output.svg")

    def test_loads_project_config_from_cwd(self):
        """If no schema-adjacent config exists, fall back to the working dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cwd_config = Path(tmpdir) / ".wizerd.yaml"
            with open(cwd_config, "w") as f:
                yaml.dump({"output": "cwd-output.svg"}, f)

            original_cwd = Path.cwd()
            try:
                os.chdir(tmpdir)
                loader = ConfigLoader()
                loader.set_home_dir(Path("/nonexistent"))  # Don't find home config
                # Create dummy input to avoid cwd config again
                dummy = Path(tmpdir) / "input.sql"
                dummy.touch()
                cfg = loader.load(input_path=dummy)
                assert cfg.output_path == Path("cwd-output.svg")
            finally:
                os.chdir(original_cwd)


class TestConfigLoaderExplicitConfig:
    """Tests for explicit config file loading."""

    def test_loads_explicit_config_file(self):
        """Explicit --config should override discovery and track its origin."""
        with tempfile.TemporaryDirectory() as tmpdir:
            explicit_config = Path(tmpdir) / "explicit.yaml"
            with open(explicit_config, "w") as f:
                yaml.dump({"output": "explicit.svg", "theme": "monochrome"}, f)

            loader = ConfigLoader()
            loader.set_home_dir(Path("/nonexistent"))  # Don't find home config

            # Create dummy input to avoid picking up other configs
            dummy_input = Path(tmpdir) / "dummy.sql"
            dummy_input.touch()

            cfg = loader.load(config_file=explicit_config, input_path=dummy_input)

            assert cfg.output_path == Path("explicit.svg")
            assert cfg.theme_name == "monochrome"
            assert cfg.config_file == explicit_config

    def test_missing_explicit_config_raises(self):
        """Surface a helpful FileNotFoundError when the user mis-types --config."""
        loader = ConfigLoader()
        loader.set_home_dir(Path("/nonexistent"))

        missing = Path("/tmp/does-not-exist-config.yaml")

        with pytest.raises(FileNotFoundError):
            loader.load(config_file=missing)

    def test_invalid_config_file_raises_value_error(self):
        """Config files must decode to mappings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_config = Path(tmpdir) / "broken.yaml"
            bad_config.write_text("- not-a-mapping\n")

            loader = ConfigLoader()
            with pytest.raises(ValueError, match="mapping"):
                loader._load_config_file(bad_config)


class TestConfigLoaderEnvVars:
    """Tests for environment variable loading."""

    def test_loads_env_vars(self):
        """Environment variables should override discovered config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_config_path = Path(tmpdir) / ".wizerd.yaml"
            env_config_path.touch()

            loader = ConfigLoader()
            loader.set_home_dir(Path(tmpdir))

            with patch.dict(
                os.environ,
                {
                    "WIZERD_OUTPUT": "env-output.svg",
                    "WIZERD_THEME": "dracula",
                    "WIZERD_SHOW_EDGE_LABELS": "true",
                    "WIZERD_COLOR_BY_TRUNK": "true",
                },
            ):
                cfg = loader.load()

            assert cfg.output_path == Path("env-output.svg")
            assert cfg.theme_name == "dracula"
            assert cfg.show_edge_labels is True
            assert cfg.edge_color_mode == config.EdgeColorMode.BY_TRUNK

    def test_env_color_by_trunk_can_be_disabled(self):
        """CLI flags should be able to turn off env-provided booleans."""
        loader = ConfigLoader()
        loader.set_home_dir(Path("/nonexistent"))

        with patch.dict(os.environ, {"WIZERD_COLOR_BY_TRUNK": "true"}):
            cfg = loader.load(cli_args={"color_by_trunk": False})

        assert cfg.edge_color_mode == config.EdgeColorMode.SINGLE

    def test_env_can_set_input_and_spacing(self):
        """Additional env vars should map to nested config structures."""
        loader = ConfigLoader()
        loader.set_home_dir(Path("/nonexistent"))

        with patch.dict(
            os.environ,
            {
                "WIZERD_INPUT": "data/schema.sql",
                "WIZERD_SPACING_LINE_GAP": "12.5",
                "WIZERD_SPACING_LINE_TABLE_GAP": "15.0",
            },
        ):
            cfg = loader.load()

        assert cfg.input_path == Path("data/schema.sql")
        assert cfg.custom_spacing is not None
        assert cfg.custom_spacing.line_gap == 12.5
        assert cfg.custom_spacing.line_table_gap == 15.0


class TestConfigLoaderPriority:
    """Tests for configuration precedence."""

    def test_cli_args_override_everything(self):
        """Command-line args must sit at the top of the precedence ladder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump({"output": "config.svg"}, f)

            env_config_path = Path(tmpdir) / ".wizerd.yaml"
            with open(env_config_path, "w") as f:
                yaml.dump({"output": "env.svg"}, f)

            loader = ConfigLoader()
            loader.set_home_dir(Path(tmpdir))

            with patch.dict(os.environ, {"WIZERD_OUTPUT": "env-var.svg"}):
                cfg = loader.load(
                    cli_args={"output": Path("cli.svg")},
                    config_file=config_file,
                )

            assert cfg.output_path == Path("cli.svg")


class TestConfigLoaderSpacing:
    """Tests for custom spacing loading."""

    def test_custom_spacing_overrides_profile(self):
        """Explicit spacing values should override the derived preset numbers."""
        loader = ConfigLoader()
        cfg = loader.load(
            cli_args={
                "spacing_profile": "standard",
            }
        )

        config_dict = {
            "spacing": {
                "line_gap": 50.0,
                "line_table_gap": 40.0,
            }
        }

        result = loader._merge_dict_into_config(cfg, config_dict)

        assert result.spacing_profile.name == "standard"
        assert result.spacing_profile.line_gap == 50.0
        assert result.spacing_profile.line_table_gap == 40.0

    def test_spacing_profile_reset_clears_custom_spacing(self):
        """Switching profiles should drop lingering custom spacing overrides."""
        loader = ConfigLoader()
        base_cfg = config.AppConfig(
            input_path=Path("input.sql"),
            output_path=Path("diagram.svg"),
            spacing_profile=SpacingProfile.from_name("standard"),
            edge_color_mode=config.EdgeColorMode.SINGLE,
            theme_name="default-dark",
        )

        with_custom = loader._merge_dict_into_config(base_cfg, {"spacing": {"line_gap": 80.0}})
        reset = loader._merge_dict_into_config(with_custom, {"spacing_profile": "compact"})

        assert reset.custom_spacing is None
        assert reset.spacing_profile.name == "compact"
        assert reset.spacing_profile.line_gap == SpacingProfile.from_name("compact").line_gap


class TestConfigLoaderThemeOverrides:
    """Tests for merging theme overrides."""

    def test_theme_overrides_merge_sections(self):
        """Merging overrides twice should accumulate changes per section."""
        loader = ConfigLoader()
        base_cfg = config.AppConfig(
            input_path=Path("input.sql"),
            output_path=Path("diagram.svg"),
            spacing_profile=SpacingProfile.from_name("standard"),
            edge_color_mode=config.EdgeColorMode.SINGLE,
            theme_name="default-dark",
        )

        first = loader._merge_dict_into_config(
            base_cfg,
            {"theme_overrides": {"colors": {"canvas_background": "#111111"}}},
        )
        merged = loader._merge_dict_into_config(
            first,
            {"theme_overrides": {"dimensions": {"table_min_width": 200.0}}},
        )

        assert merged.theme_overrides.colors["canvas_background"] == "#111111"
        assert merged.theme_overrides.dimensions["table_min_width"] == 200.0

    def test_inline_theme_definition(self):
        """Config files may embed full theme definitions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_path = Path(tmpdir) / ".wizerd.yaml"
            cfg_path.write_text(
                """
theme:
  name: inline-theme
  colors:
    canvas_background: "#222222"
                """.strip()
            )
            dummy_input = Path(tmpdir) / "input.sql"
            dummy_input.touch()

            loader = ConfigLoader()
            loader.set_home_dir(Path("/nonexistent"))
            cfg = loader.load(config_file=cfg_path, input_path=dummy_input)

            assert cfg.theme_inline is not None
            assert cfg.theme_inline["colors"]["canvas_background"] == "#222222"


class TestConfigLoaderFindFiles:
    """Tests for finding config files."""

    def test_finds_home_config(self):
        """`find_config_files` should list home config paths when present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            home_config = Path(tmpdir) / ".wizerd.yaml"
            home_config.touch()

            loader = ConfigLoader()
            loader.set_home_dir(Path(tmpdir))
            files = loader.find_config_files()

            assert home_config in files


class TestEnvVarSubstitution:
    """Tests for environment variable substitution in config files."""

    def test_substitutes_env_var(self):
        """Config loader should expand ${VAR} placeholders from the environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            with open(config_file, "w") as f:
                f.write("output: ${MY_OUTPUT}\n")

            with patch.dict(os.environ, {"MY_OUTPUT": "substituted.svg"}):
                loader = ConfigLoader()
                result = loader._load_config_file(config_file)

            assert result["output"] == "substituted.svg"

    def test_substitutes_env_var_with_default(self):
        """Placeholders with :-default should resolve even when env var missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            with open(config_file, "w") as f:
                f.write("output: ${NONEXISTENT:-default.svg}\n")

            loader = ConfigLoader()
            result = loader._load_config_file(config_file)

            assert result["output"] == "default.svg"


class TestConfigLoaderBoolParsing:
    """Tests for boolean parsing from strings."""

    def test_parses_true_values(self):
        """True-like strings should parse to True for env toggles."""
        loader = ConfigLoader()
        assert loader._parse_bool("true") is True
        assert loader._parse_bool("yes") is True
        assert loader._parse_bool("1") is True
        assert loader._parse_bool("on") is True
        assert loader._parse_bool("enabled") is True

    def test_parses_false_values(self):
        """False-like strings should parse to False for env toggles."""
        loader = ConfigLoader()
        assert loader._parse_bool("false") is False
        assert loader._parse_bool("no") is False
        assert loader._parse_bool("0") is False
        assert loader._parse_bool("off") is False
        assert loader._parse_bool("disabled") is False


class TestConfigValidation:
    """Tests for configuration validation."""

    def test_valid_config(self):
        """A well-formed config should be reported as valid."""
        validator = config.ConfigValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test.sql"
            input_file.touch()

            cfg = config.AppConfig(
                input_path=input_file,
                output_path=Path("output.svg"),
                spacing_profile=SpacingProfile.from_name("standard"),
                edge_color_mode=config.EdgeColorMode.SINGLE,
                theme_name="default-dark",
            )

            result = validator.validate(cfg)
            assert result.is_valid is True
            assert len(result.errors) == 0

    def test_invalid_spacing_profile(self):
        """Unknown spacing presets should register as validation errors."""
        validator = config.ConfigValidator()

        class CustomSpacingProfile:
            """Stub spacing profile with an invalid name for validation tests."""

            name = "invalid-profile"

        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test.sql"
            input_file.touch()

            cfg = config.AppConfig(
                input_path=input_file,
                output_path=Path("output.svg"),
                spacing_profile=cast(config.SpacingProfile, CustomSpacingProfile()),
                edge_color_mode=config.EdgeColorMode.SINGLE,
                theme_name="default-dark",
            )

            result = validator.validate(cfg)
            assert result.is_valid is False
            assert any("spacing profile" in err for err in result.errors)

    def test_invalid_edge_color_mode(self):
        """Validator should reject unexpected edge color values."""
        validator = config.ConfigValidator()

        class CustomEdgeColorMode:
            """Stub edge color mode with unsupported value for validation tests."""

            value = "invalid"

        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test.sql"
            input_file.touch()

            cfg = config.AppConfig(
                input_path=input_file,
                output_path=Path("output.svg"),
                spacing_profile=SpacingProfile.from_name("standard"),
                edge_color_mode=cast(config.EdgeColorMode, CustomEdgeColorMode()),
                theme_name="default-dark",
            )

            result = validator.validate(cfg)
            assert result.is_valid is False
            assert any("edge color mode" in err for err in result.errors)

    def test_missing_input_file(self):
        """Missing input files should surface in the error list."""
        validator = config.ConfigValidator()
        cfg = config.AppConfig(
            input_path=Path("nonexistent.sql"),
            output_path=Path("output.svg"),
            spacing_profile=SpacingProfile.from_name("standard"),
            edge_color_mode=config.EdgeColorMode.SINGLE,
            theme_name="default-dark",
        )

        result = validator.validate(cfg)
        assert result.is_valid is False
        assert any("not found" in err for err in result.errors)

    def test_validation_can_skip_path_checks(self):
        """Callers should be able to bypass filesystem validation when desired."""
        validator = config.ConfigValidator()
        cfg = config.AppConfig(
            input_path=Path("missing.sql"),
            output_path=Path("out/diagram.svg"),
            spacing_profile=SpacingProfile.from_name("standard"),
            edge_color_mode=config.EdgeColorMode.SINGLE,
            theme_name="default-dark",
        )

        result = validator.validate(cfg, strict_paths=False)
        assert result.is_valid is True

    def test_validation_creates_output_directory(self):
        """Validating with strict paths should create the output directory when missing."""
        validator = config.ConfigValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.sql"
            input_file.touch()
            output_path = Path(tmpdir) / "nested" / "diagram.svg"
            assert not output_path.parent.exists()

            cfg = config.AppConfig(
                input_path=input_file,
                output_path=output_path,
                spacing_profile=SpacingProfile.from_name("standard"),
                edge_color_mode=config.EdgeColorMode.SINGLE,
                theme_name="default-dark",
            )

            result = validator.validate(cfg)
            assert result.is_valid is True
            assert output_path.parent.exists()


class TestAppConfigSerialization:
    """Tests for AppConfig serialization."""

    def test_to_dict(self):
        """`AppConfig.to_dict` should mirror the dataclass field values."""
        cfg = config.AppConfig(
            input_path=Path("input.sql"),
            output_path=Path("output.svg"),
            show_edge_labels=True,
            spacing_profile=SpacingProfile.from_name("compact"),
            edge_color_mode=config.EdgeColorMode.BY_TRUNK,
            theme_name="custom-theme",
        )

        d = cfg.to_dict()

        assert d["input_path"] == "input.sql"
        assert d["output_path"] == "output.svg"
        assert d["show_edge_labels"] is True
        assert d["spacing_profile"] == "compact"
        assert d["edge_color_mode"] == "by-trunk"
        assert d["theme_name"] == "custom-theme"

    def test_from_dict(self):
        """`AppConfig.from_dict` should hydrate a dataclass from raw values."""
        data = {
            "input_path": "input.sql",
            "output_path": "output.svg",
            "show_edge_labels": True,
            "spacing_profile": "spacious",
            "edge_color_mode": "by-trunk",
            "theme_name": "my-theme",
        }

        cfg = config.AppConfig.from_dict(data)

        assert cfg.input_path == Path("input.sql")
        assert cfg.output_path == Path("output.svg")
        assert cfg.show_edge_labels is True
        assert cfg.spacing_profile.name == "spacious"
        assert cfg.edge_color_mode == config.EdgeColorMode.BY_TRUNK
        assert cfg.theme_name == "my-theme"

    def test_roundtrip(self):
        """Serializing and re-parsing must preserve all key fields."""
        original = config.AppConfig(
            input_path=Path("input.sql"),
            output_path=Path("output.svg"),
            show_edge_labels=True,
            spacing_profile=SpacingProfile.from_name("standard"),
            edge_color_mode=config.EdgeColorMode.SINGLE,
            theme_name="default-dark",
        )

        restored = config.AppConfig.from_dict(original.to_dict())

        assert restored.input_path == original.input_path
        assert restored.output_path == original.output_path
        assert restored.show_edge_labels == original.show_edge_labels
        assert restored.spacing_profile.name == original.spacing_profile.name
        assert restored.edge_color_mode == original.edge_color_mode
        assert restored.theme_name == original.theme_name
