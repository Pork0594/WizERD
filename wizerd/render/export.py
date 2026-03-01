"""Output format helpers."""

from pathlib import Path
from types import ModuleType


class Exporter:
    """Handles conversions from SVG to other formats."""

    def svg_to_png(self, svg_path: Path, png_path: Path) -> None:
        """Convert an SVG diagram into a raster PNG using CairoSVG."""
        cairosvg = self._require_cairosvg()
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path))

    def svg_to_pdf(self, svg_path: Path, pdf_path: Path) -> None:
        """Convert an SVG diagram into a vector PDF using CairoSVG."""
        cairosvg = self._require_cairosvg()
        cairosvg.svg2pdf(url=str(svg_path), write_to=str(pdf_path))

    @staticmethod
    def _require_cairosvg() -> "ModuleType":
        try:
            import cairosvg  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "CairoSVG is required for export operations. Install wizerd[export] to enable this feature."
            ) from exc
        return cairosvg
