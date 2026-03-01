"""Command-line interface for WizERD."""

from __future__ import annotations

import json
import logging
import os
from importlib import metadata as importlib_metadata
from pathlib import Path

import typer
from typer.core import TyperCommand, TyperGroup

from wizerd import config, pipeline
from wizerd.config_loader import ConfigLoader
from wizerd.parser.ddl_parser import DDLParser
from wizerd.templates.config import load_template
from wizerd.theme.loader import list_builtin_themes

LOGO = r"""
 █████   ███   █████  ███             ██████████ ███████████   ██████████
░░███   ░███  ░░███  ░░░             ░░███░░░░░█░░███░░░░░███ ░░███░░░░███
 ░███   ░███   ░███  ████   █████████ ░███  █ ░  ░███    ░███  ░███   ░░███
 ░███   ░███   ░███ ░░███  ░█░░░░███  ░██████    ░██████████   ░███    ░███
 ░░███  █████  ███   ░███  ░   ███░   ░███░░█    ░███░░░░░███  ░███    ░███
  ░░░█████░█████░    ░███    ███░   █ ░███ ░   █ ░███    ░███  ░███    ███
    ░░███ ░░███      █████  █████████ ██████████ █████   █████ ██████████
     ░░░   ░░░      ░░░░░  ░░░░░░░░░ ░░░░░░░░░░ ░░░░░   ░░░░░ ░░░░░░░░░░
"""


def _resolve_version() -> str:
    """Return the installed WizERD version or best-effort fallback."""

    package_name = "wizerd"
    try:
        return importlib_metadata.version(package_name)
    except importlib_metadata.PackageNotFoundError:
        fallback = _read_version_from_pyproject()
        return fallback or "unknown"


def _read_version_from_pyproject() -> str | None:
    """Read the project version from a local pyproject.toml if available."""

    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    try:
        contents = pyproject_path.read_text(encoding="utf-8")
    except OSError:
        return None

    in_project_section = False
    for raw_line in contents.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_project_section = line == "[project]"
            continue
        if in_project_section and line.startswith("version"):
            _, _, value = line.partition("=")
            version_candidate = value.strip().strip('"').strip("'")
            if version_candidate:
                return version_candidate
    return None


VERSION = _resolve_version()


def _print_logo() -> None:
    typer.echo(LOGO.rstrip("\n"))
    typer.echo("")


class LogoCommand(TyperCommand):
    def format_help(self, ctx, formatter) -> None:
        _print_logo()
        return super().format_help(ctx, formatter)


class LogoGroup(TyperGroup):
    def format_help(self, ctx, formatter) -> None:
        _print_logo()
        return super().format_help(ctx, formatter)


class LogoTyper(typer.Typer):
    def command(self, *args, **kwargs):
        kwargs.setdefault("cls", LogoCommand)
        return super().command(*args, **kwargs)


app = LogoTyper(
    cls=LogoGroup,
    help="""WizERD — PostgreSQL ER diagram generator

Generate beautiful ER diagrams from PostgreSQL schema dumps.

Examples:
  wizerd generate schema.sql -o diagram.svg
  wizerd render schema.sql -o diagram.svg -t light -l
  wizerd generate schema.sql --config my-config.yaml
  wizerd g schema.sql -o diagram.svg -wlte light
""",
)


SCHEMA_ARGUMENT = typer.Argument(
    ...,
    help="Path to PostgreSQL schema dump (.sql file)",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
)

OUTPUT_OPTION = typer.Option(
    Path("diagram.svg"),
    "--output",
    "-o",
    help="Output diagram path",
)

SHOW_EDGE_LABELS_OPTION = typer.Option(
    False,
    "--show-edge-labels",
    "-l",
    help="Render FK names along connector lines",
)

SPACING_PROFILE_OPTION = typer.Option(
    "standard",
    "--spacing-profile",
    "-w",
    help="Spacing preset: compact, standard, or spacious",
    show_default=True,
)

COLOR_BY_TRUNK_OPTION = typer.Option(
    False,
    "--color-by-trunk",
    "-e",
    help="Use unique color per FK target (default: single color)",
)

THEME_OPTION = typer.Option(
    "default-dark",
    "--theme",
    "-t",
    help="Theme name or path",
)

CONFIG_OPTION = typer.Option(
    None,
    "--config",
    "-c",
    help="Path to config file (YAML or JSON)",
)

CONFIG_FILE_ARGUMENT = typer.Argument(
    ...,
    help="Path to config file to validate",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
)

VALIDATE_SCHEMA_OPTION = typer.Option(
    None,
    "--schema",
    "-s",
    help="Also validate against a schema file (checks input/output paths)",
)

INIT_OUTPUT_OPTION = typer.Option(
    Path(".wizerd.yaml"),
    "--output",
    "-o",
    help="Path where to create the config file",
)

INIT_TEMPLATE_OPTION = typer.Option(
    "default",
    "--template",
    "-t",
    help="Template to use: default, minimal, or full",
)

INIT_FORCE_OPTION = typer.Option(
    False,
    "--force",
    "-f",
    help="Overwrite existing config file",
)


@app.callback(no_args_is_help=True, invoke_without_command=True)
def _bootstrap(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show WizERD version",
        is_eager=True,
    ),
) -> None:
    """Initialize logging before dispatching to command handlers."""

    if version:
        typer.echo(f"WizERD v{VERSION}")
        raise typer.Exit()

    _configure_logging()


def _configure_logging() -> None:
    """Initialize logging using the same rules as the CLI binary.

    We honor the `WIZERD_LOG_LEVEL` environment variable so developers can
    dial verbosity up when debugging without recompiling or editing the config
    file.  Keeping this in a helper makes it easy for tests to stub logging.
    """
    level_name = os.getenv("WIZERD_LOG_LEVEL", "WARNING").upper()
    level = getattr(logging, level_name, logging.WARNING)
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")


def _generate_diagram(
    schema: Path,
    output: Path,
    show_edge_labels: bool,
    spacing_profile_name: str,
    color_by_trunk: bool,
    theme_name: str,
    config_file: Path | None = None,
) -> None:
    """Resolve configuration, validate it, and delegate to the pipeline.

    The CLI exposes several commands that ultimately do the same work.  Rather
    than duplicating validation in each Typer command, we normalize inputs
    (positional args, config files, env vars) here, then run the orchestrated
    pipeline.  Any exception raised here propagates back to the calling command
    so it can map the failure to an appropriate exit code.
    """
    loader = ConfigLoader()
    cli_args = {
        "output": output,
        "show_edge_labels": show_edge_labels,
        "spacing_profile": spacing_profile_name,
        "color_by_trunk": color_by_trunk,
        "theme": theme_name,
    }

    try:
        app_config = loader.load(
            cli_args=cli_args,
            config_file=config_file,
            input_path=schema,
        )
    except FileNotFoundError as exc:
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc
    except ValueError as exc:
        typer.secho(f"Failed to load configuration: {exc}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    # Positional schema argument always wins over config files/env vars
    app_config.input_path = schema

    validator = config.ConfigValidator()
    try:
        validator.validate_or_raise(app_config)
    except ValueError as exc:
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    try:
        pipeline.run(app_config)
    except ValueError as exc:  # pragma: no cover - CLI error handling
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc


def _register_generate_aliases(func):
    aliases = [
        ("generate", {"short_help": "Generate an ER diagram from a PostgreSQL schema dump"}),
        ("g", {"short_help": "Generate an ER diagram", "hidden": True}),
        ("render", {"short_help": "Generate an ER diagram (alias)", "hidden": False}),
        ("r", {"short_help": "Generate an ER diagram (alias)", "hidden": True}),
    ]

    for name, kwargs in aliases:
        func = app.command(name, **kwargs)(func)
    return func


@_register_generate_aliases
def generate(
    schema: Path = SCHEMA_ARGUMENT,
    output: Path = OUTPUT_OPTION,
    show_edge_labels: bool = SHOW_EDGE_LABELS_OPTION,
    spacing_profile: str = SPACING_PROFILE_OPTION,
    color_by_trunk: bool = COLOR_BY_TRUNK_OPTION,
    theme: str = THEME_OPTION,
    config: Path | None = CONFIG_OPTION,
) -> None:
    """Generate an ER diagram from a PostgreSQL schema dump (render aliases supported)."""
    _generate_diagram(
        schema,
        output,
        show_edge_labels,
        spacing_profile,
        color_by_trunk,
        theme,
        config,
    )


@app.command("themes", short_help="List all available themes")
@app.command("t", short_help="List themes", hidden=True)
def themes() -> None:
    """List all available themes.

    Shows all built-in themes with their descriptions and whether
    they are light or dark themes.

    Examples:
        wizerd themes
        wizerd t
    """
    theme_list = list_builtin_themes()
    typer.echo("Available themes:")
    typer.echo("")
    for name, theme in sorted(theme_list.items()):
        dark_indicator = " (dark)" if theme.is_dark else " (light)"
        typer.echo(f"  {name}{dark_indicator} - {theme.description}")


@app.command("parse", short_help="Parse schema and print JSON representation")
@app.command("p", short_help="Parse schema", hidden=True)
def parse(
    schema: Path = SCHEMA_ARGUMENT,
) -> None:
    """Parse a PostgreSQL schema and print JSON representation.

    This is useful for debugging or understanding how the parser
    interprets your schema.

    Examples:
        wizerd parse schema.sql
        wizerd p schema.sql > schema.json
    """
    parser = DDLParser()
    schema_model = parser.parse_file(schema)
    typer.echo(json.dumps(schema_model.to_dict(), indent=2))


@app.command("init", short_help="Create a config file with default values")
def init_config(
    path: Path = INIT_OUTPUT_OPTION,
    template: str = INIT_TEMPLATE_OPTION,
    force: bool = INIT_FORCE_OPTION,
) -> None:
    """Create a config file with default values.

    Templates:
      default  - Common options with recommended defaults
      minimal  - Just the essential options
      full     - All available options with explanations

    Examples:
        wizerd init
        wizerd init -o my-config.yaml
        wizerd init -t full -o full-config.yaml
    """
    if path.exists() and not force:
        typer.secho(
            f"Config file already exists: {path}",
            err=True,
            fg=typer.colors.RED,
        )
        typer.echo("Use --force to overwrite or choose a different path.")
        raise typer.Exit(code=1)

    try:
        template_body = load_template(template)
    except ValueError as exc:
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(template_body)
        typer.secho(f"Created config file: {path}", fg=typer.colors.GREEN)
    except OSError as exc:
        typer.secho(f"Failed to write config file: {exc}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc


@app.command("validate", short_help="Validate a config file")
def validate_config(
    config_file: Path = CONFIG_FILE_ARGUMENT,
    schema: Path | None = VALIDATE_SCHEMA_OPTION,
) -> None:
    """Validate a config file without generating a diagram.

    This is useful for catching configuration errors before running
    a full generation.

    Examples:
        wizerd validate .wizerd.yaml
        wizerd validate config.yaml --schema schema.sql
    """
    loader = ConfigLoader()
    try:
        app_config = loader.load(
            cli_args={},
            config_file=config_file,
            input_path=schema or Path("input.sql"),
        )
    except FileNotFoundError as exc:
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc
    except ValueError as exc:
        typer.secho(f"Failed to load configuration: {exc}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    if schema:
        app_config.input_path = schema

    validator = config.ConfigValidator()
    result = validator.validate(app_config, strict_paths=schema is not None)

    if result.is_valid and not result.warnings:
        typer.secho("Config file is valid!", fg=typer.colors.GREEN)
    else:
        if result.errors:
            typer.secho("Config validation failed:", err=True, fg=typer.colors.RED)
            for error in result.errors:
                typer.echo(f"  • {error}")
        if result.warnings:
            typer.secho("Config warnings:", fg=typer.colors.YELLOW)
            for warning in result.warnings:
                typer.echo(f"  • {warning}")

    if not result.is_valid:
        raise typer.Exit(code=1)


@app.command("defaults", short_help="Show default configuration values")
def show_defaults(
    format: str = typer.Option(
        "yaml",
        "--format",
        "-f",
        help="Output format: yaml, json, or env",
    ),
) -> None:
    """Show default configuration values.

    Useful for understanding what options are available and
    what the default values are.

    Examples:
        wizerd defaults
        wizerd defaults --format json
        wizerd defaults -f env
    """
    defaults = {
        "output": "diagram.svg",
        "show-edge-labels": False,
        "spacing-profile": "standard",
        "color-by-trunk": False,
        "theme": "default-dark",
        "edge-color-mode": "single",
    }

    if format == "yaml":
        import yaml  # type: ignore[import-untyped]

        typer.echo(yaml.dump(defaults, default_flow_style=False, sort_keys=False))
    elif format == "json":
        typer.echo(json.dumps(defaults, indent=2))
    elif format == "env":
        for key, value in defaults.items():
            env_key = f"WIZERD_{key.upper()}"
            typer.echo(f"# {env_key}={value}")
    else:
        typer.secho(
            f"Unknown format '{format}'. Use: yaml, json, or env",
            err=True,
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)
