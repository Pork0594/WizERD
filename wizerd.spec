# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for building WizERD standalone binaries.

Usage:
    pyinstaller wizerd.spec

This creates a single executable that includes:
- Python interpreter
- All Python dependencies  
- WizERD application code

Note: The resulting binary still requires Node.js to be installed on the
user's system for the ELK layout engine to function.

To bundle Node.js would require additional complexity. For now, users
should install Node.js 18+ via their preferred package manager.
"""

import os
import sys
from pathlib import Path

block_cipher = None

# Paths
ROOT = Path(ROOT_DIR := os.path.dirname(os.path.abspath(SPEC)))
WIZERD_DIR = ROOT / "wizerd"
LAYOUT_DIR = WIZERD_DIR / "layout"

a = Analysis(
    [
        str(WIZERD_DIR / "__main__.py"),
    ],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # Include layout engine files
        (str(LAYOUT_DIR / "elk_runner.mjs"), "wizerd/layout"),
        (str(LAYOUT_DIR / "package.json"), "wizerd/layout"),
    ],
    hiddenimports=[
        "wizerd",
        "wizerd.cli",
        "wizerd.config",
        "wizerd.config_loader",
        "wizerd.pipeline",
        "wizerd.parser",
        "wizerd.parser.ddl_parser",
        "wizerd.render",
        "wizerd.render.svg_renderer",
        "wizerd.render.export",
        "wizerd.layout",
        "wizerd.layout.engine",
        "wizerd.layout.spacing",
        "wizerd.graph",
        "wizerd.graph.layout_graph",
        "wizerd.model",
        "wizerd.model.schema",
        "wizerd.theme",
        "wizerd.theme.loader",
        "wizerd.theme.presets",
        "wizerd.theme.renderer_theme",
        "wizerd.theme.palette",
        "typer",
        "typer.core",
        "click",
        "click.core",
        "sqlparse",
        "sqlparse.parser",
        "sqlparse.lexer",
        "sqlparse.tokens",
        "sqlparse.sql",
        "svgwrite",
        "yaml",
        "yaml.loader",
        "yaml.dumper",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "test",
        "tests",
        "pytest",
        "IPython",
        "jupyter",
        "matplotlib",
        "pandas",
        "numpy",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="wizerd",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
