# Installation

WizERD supports multiple installation methods. Choose the one that fits your workflow.

## Requirements

- Python 3.9 or higher
- Node.js 18+ (for the layout engine)

## Homebrew (macOS)

```bash
brew tap Pork0594/WizERD
brew install wizerd
```

## Install from PyPI

```bash
pip install wizerd
```

## Install from Source

```bash
git clone https://github.com/Pork0594/wizerd.git
cd wizerd
pip install -e .
```

Editable installs run a build hook that executes `npm ci` inside `wizerd/layout/` and bundles the resulting `node_modules` into the package.

## Verify Installation

```bash
wizerd --help
```

## Pre-built Binaries

Download pre-built binaries from the [releases page](https://github.com/Pork0594/wizerd/releases):

```bash
# Linux x64
curl -sL https://github.com/Pork0594/wizerd/releases/latest/download/wizerd-linux-x64.tar.gz | tar xz
./wizerd generate schema.sql -o diagram.svg

# macOS ARM (Apple Silicon)
curl -sL https://github.com/Pork0594/wizerd/releases/latest/download/wizerd-macos-arm64.tar.gz | tar xz

# macOS x64
curl -sL https://github.com/Pork0594/wizerd/releases/latest/download/wizerd-macos-x64.tar.gz | tar xz

# Windows
curl -sL https://github.com/Pork0594/wizerd/releases/latest/download/wizerd-windows-x64.zip -o wizerd.zip
unzip wizerd.zip
```

## Node.js Dependency

WizERD uses ELK (Eclipse Layout Kernel) via Node.js for the layout engine. If `node` is not installed, the CLI will report a clear error.

To verify Node.js is available:

```bash
node --version  # Should be 18.0.0 or higher
```

## System Requirements Summary

| Component | Minimum Version |
|-----------|-----------------|
| Python | 3.9+ |
| Node.js | 18+ |
| pip | Latest recommended |

## Next Steps

- [Getting Started](getting-started.md) — Generate your first diagram
- [Configuration](configuration.md) — Customize your setup
