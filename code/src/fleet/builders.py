"""Build preprocessed paired-fleet datasets. Preprocessing is row-wise (no fitted parameters), so it cannot leak
information between units or between calibration and test items."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.loaders import RAW, load_corn, load_mango, load_tablets
from src.fleet.data import Fleet
from src.preprocessing.spectral import savgol, snv

_MANGO = None


def mango(season: int, window=13, lo=684, hi=990) -> Fleet:
    """Mango DM, one season. SG 2nd derivative (w=13, poly 2) on 684-990 nm, as in Anderson et al. (2020)."""
    global _MANGO
    if _MANGO is None:
        _MANGO = load_mango("v4")
    d = _MANGO
    m = ((d.meta.season == season) & (d.meta.outlier_flag == 0)).to_numpy()
    r = (d.wl >= lo - 24) & (d.wl <= hi + 24)
    Z = savgol(d.X[m][:, r], window, 2, 2)
    keep = (d.wl[r] >= lo) & (d.wl[r] <= hi)
    return Fleet(f"mango{season}", Z[:, keep], d.Y.dm.to_numpy()[m], d.meta.sample_id.to_numpy()[m].astype(str),
                 d.meta.instrument.to_numpy()[m].astype(str), d.wl[r][keep], "DM (%)",
                 (d.meta.date.astype(str) + "|" + d.meta.population.astype(str)).to_numpy()[m])


_NEO = None
NEO_PROPS = {"oc": ("eoc_tot_c", "log"), "clay": ("clay_tot_psa", None), "ph": ("ph_h2o", None),
             "n": ("n_tot_ncs", "log"), "cec": ("cecd_nh4", "log"), "sand": ("sand_tot_psa", None)}


def neospectra(prop: str = "oc", units=("NEO1", "NEO2", "NEO3", "NEO4", "NEO5", "NEO6", "NEO7")) -> Fleet:
    """NeoSpectra handheld soil fleet (no accessory units NEO1-NEO7). Absorbance log10(100/R), SNV, SG 1st
    derivative (w=11). log10(x+0.1) transform for skewed properties (OC, N, CEC)."""
    global _NEO
    if _NEO is None:
        _NEO = pd.read_csv(RAW / "neospectra" / "Neospectra_WoodwellKSSL_soil+site+NIR.csv", low_memory=False)
    df = _NEO[_NEO.SCANNER.isin(units)]
    spec = [c for c in df.columns if str(c).replace(".", "", 1).isdigit()]
    wl = np.array([float(c) for c in spec])
    o = np.argsort(wl)
    R = df[spec].to_numpy(float)[:, o]
    A = np.log10(100.0 / np.clip(R, 1e-3, None))
    Z = savgol(snv(A), 11, 2, 1)
    col, tr = NEO_PROPS[prop]
    y = df[col].to_numpy(float)
    if tr == "log":
        y = np.log10(np.clip(y, 0, None) + 0.1)
    ok = np.isfinite(y)
    return Fleet(f"neospectra_{prop}", Z[ok], y[ok], df.kssl_id.astype(str).to_numpy()[ok],
                 df.SCANNER.astype(str).to_numpy()[ok], wl[o], prop + (" (log10)" if tr else ""))


def corn(prop: str = "protein") -> Fleet:
    d = load_corn()
    Xs, ys, it, un = [], [], [], []
    for u, sd in d.items():
        Z = savgol(sd.X, 15, 2, 1)
        Xs.append(Z); ys.append(sd.Y[prop].to_numpy()); it.append(sd.meta.sample_id.astype(str).to_numpy()); un.append(np.repeat(u, len(Z)))
    return Fleet(f"corn_{prop}", np.vstack(Xs), np.concatenate(ys), np.concatenate(it), np.concatenate(un), d["m5"].wl, prop)


def tablets(prop: str = "assay") -> Fleet:
    d = load_tablets()
    Xs, ys, it, un = [], [], [], []
    for u, sd in d.items():
        Z = savgol(snv(sd.X), 11, 2, 1)
        Xs.append(Z); ys.append(sd.Y[prop].to_numpy()); it.append(sd.meta.sample_id.astype(str).to_numpy()); un.append(np.repeat(u, len(Z)))
    return Fleet(f"tablets_{prop}", np.vstack(Xs), np.concatenate(ys), np.concatenate(it), np.concatenate(un), d["inst1"].wl, prop)
