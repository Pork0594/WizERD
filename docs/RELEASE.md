# WizERD Release Guide

This document covers the release process for WizERD using semantic-release.

## How Releases Work

WizERD uses **semantic-release** to automate versioning and publishing:

1. **Push to `main`** branch
2. **GitHub Actions** runs tests and builds binaries
3. **semantic-release** analyzes commits:
   - `feat:` → minor version bump
   - `fix:` → patch version bump
   - `BREAKING CHANGE:` → major version bump
4. Creates git tag, publishes to PyPI, creates GitHub Release

See [COMMIT_GUIDE.md](./COMMIT_GUIDE.md) for commit message conventions.

---

## Distribution Channels

### PyPI (Python Package Index)

```bash
pip install wizerd

# With export features (PNG/PDF)
pip install wizerd[export]
```

### GitHub Releases (Pre-built Binaries)

Download from: https://github.com/Pork0594/wizerd/releases

```bash
# Linux/macOS
curl -sL https://github.com/Pork0594/wizerd/releases/latest/download/wizerd-linux-x64.tar.gz | tar xz
./wizerd generate schema.sql -o diagram.svg
```

Available binaries:
- `wizerd-linux-x64.tar.gz`
- `wizerd-linux-arm64.tar.gz`
- `wizerd-macos-x64.tar.gz`
- `wizerd-macos-arm64.tar.gz`
- `wizerd-windows-x64.zip`

---

## Manual Release (Not Recommended)

Only for special cases. Push a tag manually:

```bash
git tag v0.2.0
git push origin v0.2.0
```

This bypasses semantic-release and requires manual version management.

---

## GitHub Secrets

Required for automated releases:
- `PYPI_TOKEN`: PyPI API token (add to GitHub repo secrets)
- `GH_TOKEN`: GitHub token (automatically available via `secrets.GITHUB_TOKEN`)

---

## Troubleshooting

### Release not triggered
- Ensure commits follow conventional format
- Check that you're pushing to `main` branch
- Verify GitHub Actions workflow is enabled

### PyPI upload fails
- Verify `PYPI_TOKEN` is set in GitHub secrets
- Check token has upload permissions

### Binary build fails
- Ensure Node.js 20 is available in the workflow
- Check PyInstaller version is correct
