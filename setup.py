"""Custom setuptools entry point to bundle elkjs during builds."""

from __future__ import annotations

import filecmp
import os
import shutil
import subprocess
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as build_py_orig
from setuptools.command.egg_info import egg_info as egg_info_orig
from setuptools.command.sdist import sdist as sdist_orig

ROOT = Path(__file__).resolve().parent
LAYOUT_DIR = ROOT / "wizerd" / "layout"
PACKAGE_LOCK = LAYOUT_DIR / "package-lock.json"
NODE_MODULES = LAYOUT_DIR / "node_modules"
NODE_MODULES_LOCK = NODE_MODULES / ".package-lock.json"


class NpmInstallMixin:
    """Run `npm ci` once per build if node_modules is missing or stale."""

    _npm_env_var = "WIZERD_SKIP_NPM_CI"

    def _ensure_npm_dependencies(self) -> None:
        distribution = getattr(self, "distribution", None)
        if distribution is not None and getattr(distribution, "_wizerd_npm_ready", False):
            return

        if os.environ.get(self._npm_env_var):
            if not NODE_MODULES.exists():
                raise RuntimeError(
                    "Node modules are missing but npm install step was explicitly skipped."
                )
            if distribution is not None:
                distribution._wizerd_npm_ready = True  # type: ignore[attr-defined]
            return

        if self._node_modules_fresh():
            if distribution is not None:
                distribution._wizerd_npm_ready = True  # type: ignore[attr-defined]
            return

        npm_path = shutil.which("npm")
        if not npm_path:
            raise RuntimeError(
                "Node.js/npm is required to build the bundled ELK dependencies. "
                "Install Node 18+ or set WIZERD_SKIP_NPM_CI=1 if you have already vendored node_modules."
            )

        subprocess.check_call([npm_path, "ci"], cwd=str(LAYOUT_DIR))

        if distribution is not None:
            distribution._wizerd_npm_ready = True  # type: ignore[attr-defined]

    @staticmethod
    def _node_modules_fresh() -> bool:
        if not (NODE_MODULES.exists() and PACKAGE_LOCK.exists() and NODE_MODULES_LOCK.exists()):
            return False
        try:
            return filecmp.cmp(str(PACKAGE_LOCK), str(NODE_MODULES_LOCK), shallow=False)
        except OSError:
            return False


class build_py(NpmInstallMixin, build_py_orig):
    """Custom build command that ensures elkjs is installed."""

    def run(self) -> None:  # noqa: D401
        self._ensure_npm_dependencies()
        super().run()


class sdist(NpmInstallMixin, sdist_orig):
    """Ensure npm dependencies exist before creating the source tarball."""

    def run(self) -> None:  # noqa: D401
        self._ensure_npm_dependencies()
        super().run()


class egg_info(NpmInstallMixin, egg_info_orig):
    """Populate package metadata only after JS deps are installed."""

    def run(self) -> None:  # noqa: D401
        self._ensure_npm_dependencies()
        super().run()


cmdclass = {
    "build_py": build_py,
    "sdist": sdist,
    "egg_info": egg_info,
}

setup(cmdclass=cmdclass)
