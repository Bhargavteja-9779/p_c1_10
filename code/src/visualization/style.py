"""Publication figure style for Elsevier (Analytica Chimica Acta).

Colour decisions follow a validated categorical palette (checked with the
dataviz skill's validator on a white print surface: adjacent CVD dE >= 9.1,
normal-vision dE >= 19.6). Because three slots are < 3:1 contrast on white,
every multi-series figure carries a legend AND a secondary encoding (marker
shape), and the plotted values are always exported as a CSV "table view".
Sizes follow Elsevier artwork guidance: single column 90 mm, 1.5 column
140 mm, full width 190 mm; raster output >= 600 dpi.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

MM = 1 / 25.4
WIDTH = {"single": 90 * MM, "onehalf": 140 * MM, "double": 190 * MM}

# Fixed categorical order (never cycled past 8; colour follows the entity, not rank).
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "h"]
# Sequential (single hue blue, light->dark) and diverging (blue <-> red, grey midpoint).
SEQ_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
DIVERGING = ["#184f95", "#3987e5", "#9ec5f4", "#f0efec", "#f3a9a8", "#e34948", "#a32a2a"]
INK = {"primary": "#0b0b0b", "secondary": "#52514e", "muted": "#898781"}
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SURFACE = "#ffffff"


def apply_style(font_size: float = 7.5) -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"],
        "font.size": font_size,
        "axes.titlesize": font_size + 0.5,
        "axes.labelsize": font_size,
        "xtick.labelsize": font_size - 0.5,
        "ytick.labelsize": font_size - 0.5,
        "legend.fontsize": font_size - 0.5,
        "legend.frameon": False,
        "axes.edgecolor": AXIS,
        "axes.linewidth": 0.6,
        "axes.labelcolor": INK["primary"],
        "axes.titlecolor": INK["primary"],
        "text.color": INK["primary"],
        "xtick.color": INK["secondary"],
        "ytick.color": INK["secondary"],
        "xtick.major.width": 0.5,
        "ytick.major.width": 0.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.4,
        "grid.linestyle": "-",
        "axes.axisbelow": True,
        "axes.prop_cycle": matplotlib.cycler(color=SERIES),
        "lines.linewidth": 1.2,
        "lines.markersize": 4.5,
        "lines.markeredgewidth": 0.7,
        "lines.markeredgecolor": SURFACE,
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        "errorbar.capsize": 0,
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    })


def series_style(i: int) -> dict:
    """Colour + marker for the i-th entity (fixed order; callers must map entity->i stably)."""
    if i >= len(SERIES):
        raise ValueError("More than 8 categorical series: fold into 'Other' or use small multiples.")
    return {"color": SERIES[i], "marker": MARKERS[i]}


def figure(width: str = "single", height_mm: float = 60.0, **kw):
    apply_style()
    return plt.subplots(figsize=(WIDTH[width], height_mm * MM), **kw)


def save(fig, stem: str | Path, table: pd.DataFrame | None = None, formats=("pdf", "png", "tiff"), dpi: int = 600) -> list[Path]:
    """Save a figure in journal formats and its CSV table view (the plotted numbers)."""
    stem = Path(stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    out = []
    for fmt in formats:
        p = stem.with_suffix("." + fmt)
        kwargs = {"dpi": dpi} if fmt in ("png", "tiff") else {}
        if fmt == "tiff":
            kwargs["pil_kwargs"] = {"compression": "tiff_lzw"}
        fig.savefig(p, **kwargs)
        out.append(p)
    if table is not None:
        p = stem.with_suffix(".csv")
        table.to_csv(p, index=False)
        out.append(p)
    plt.close(fig)
    return out
