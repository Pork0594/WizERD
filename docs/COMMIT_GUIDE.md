# Commit Message Guide

WizERD uses [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning and changelog generation.

## Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

## Types

| Type | Description | Release |
|------|-------------|---------|
| `feat` | New feature | minor |
| `fix` | Bug fix | patch |
| `docs` | Documentation only | none |
| `style` | Code style (formatting) | none |
| `refactor` | Code refactoring | none |
| `perf` | Performance improvement | patch |
| `test` | Adding/updating tests | none |
| `chore` | Maintenance tasks | none |
| `BREAKING CHANGE` | Breaking change | major |

## Examples

```bash
# New feature
git commit -m "feat(cli): add --output-format flag"

# Bug fix
git commit -m "fix(parser): handle quoted column names correctly"

# Documentation
git commit -m "docs(readme): add installation instructions"

# Breaking change
git commit -m "feat(cli)!: remove deprecated --old-flag option
BREAKING CHANGE: --old-flag has been removed, use --new-flag instead"

# Fix with body
git commit -m "fix(layout): correct edge routing for self-references

The edge routing algorithm was not handling self-referencing tables
correctly, causing connectors to overlap with the table itself.
Now uses a proper loop layout."
```

## How It Works

1. **Push to `main`** branch
2. **GitHub Actions** runs tests
3. **After tests pass**, semantic-release:
   - Analyzes commits since last release
   - Determines version bump (major/minor/patch)
   - Creates version tag (e.g., `v0.2.0`)
   - Generates `CHANGELOG.md`
   - Publishes to PyPI
   - Creates GitHub Release

## Common Scenarios

| What you want to do | Commit message |
|---------------------|----------------|
| New feature | `feat: add dark mode` |
| Fix bug | `fix: correct layout crash` |
| Breaking change | `feat(api)!: change response format` |
| Just documentation | `docs: update README` |
| Skip release | `chore: update dependencies` |

## Quick Reference

```bash
# Feature
git commit -m "feat: new amazing feature"

# Fix
git commit -m "fix: annoying bug"

# Major (breaking)
git commit -m "feat!: breaking change description"
```

## CI Skipping

Skip CI for a commit:
```bash
git commit -m "chore: update deps [skip ci]"
```
