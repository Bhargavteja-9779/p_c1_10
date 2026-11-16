"""Standardised loaders for the public NIR datasets.

Every loader returns a ``SpectralData`` with
  X      : (n, p) float64 spectra
  wl     : (p,) wavelengths (nm) or channel index
  Y      : DataFrame of reference values (one column per property)
  meta   : DataFrame of grouping metadata used for leakage-safe splitting
           (e.g. sample_id, instrument, season, partition)
Nothing is filtered silently: any exclusion is explicit and logged by callers.
"""
from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io as sio

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
EXTRACT = ROOT / "data" / "processed" / "extract"


@dataclass
class SpectralData:
    name: str
    X: np.ndarray
    wl: np.ndarray
    Y: pd.DataFrame
    meta: pd.DataFrame

    def subset(self, mask) -> "SpectralData":
        mask = np.asarray(mask)
        return SpectralData(self.name, self.X[mask], self.wl, self.Y.loc[mask].reset_index(drop=True),
                            self.meta.loc[mask].reset_index(drop=True))

    def __len__(self) -> int:
        return self.X.shape[0]

    def __post_init__(self):
        # pandas>=3 copy-on-write returns read-only arrays; keep our own writable copies.
        self.X = np.array(self.X, dtype=float, copy=True)
        self.wl = np.array(self.wl, dtype=float, copy=True)


def _extract(zip_rel: str) -> None:
    EXTRACT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(RAW / zip_rel) as z:
        for m in z.namelist():
            if not m.startswith("__MACOSX") and not (EXTRACT / m).exists():
                z.extract(m, EXTRACT)


def _ds(obj):
    """Return .data array of an Eigenvector DataSet saved as a MATLAB struct."""
    return np.asarray(obj["data"][0, 0], dtype=float)


def _axis(obj, dim=1):
    ax = obj["axisscale"][0, 0]
    try:
        v = np.asarray(ax[dim, 0], dtype=float).ravel()
        return v if v.size else None
    except Exception:
        return None


def load_corn() -> dict[str, SpectralData]:
    """Corn: 80 samples on instruments m5, mp5, mp6; properties moisture, oil, protein, starch."""
    _extract("corn/corn.mat_.zip")
    d = sio.loadmat(EXTRACT / "corn.mat")
    Y = pd.DataFrame(_ds(d["propvals"]), columns=["moisture", "oil", "protein", "starch"])
    wl = np.arange(1100, 2500, 2, dtype=float)
    out = {}
    for inst in ("m5", "mp5", "mp6"):
        X = _ds(d[f"{inst}spec"])
        meta = pd.DataFrame({"sample_id": np.arange(len(X)), "instrument": inst})
        out[inst] = SpectralData(f"corn_{inst}", X, wl, Y.copy(), meta)
    return out


def load_tablets() -> dict[str, SpectralData]:
    """IDRC 2002 shootout tablets on two instruments; partitions as distributed."""
    _extract("tablets/nir_shootout_2002.mat_.zip")
    d = sio.loadmat(EXTRACT / "nir_shootout_2002.mat")
    out = {}
    for inst in (1, 2):
        Xs, Ys, metas = [], [], []
        offset = 0
        for part in ("calibrate", "validate", "test"):
            X = _ds(d[f"{part}_{inst}"])
            Y = _ds(d[f"{part}_Y"])
            Xs.append(X)
            Ys.append(Y)
            metas.append(pd.DataFrame({"sample_id": np.arange(offset, offset + len(X)), "partition": part, "instrument": f"inst{inst}"}))
            offset += len(X)
        wl = _axis(d[f"calibrate_{inst}"], 1)
        X = np.vstack(Xs)
        Yv = np.vstack(Ys)
        cols = ["weight", "hardness", "assay"][: Yv.shape[1]]
        out[f"inst{inst}"] = SpectralData(f"tablets_inst{inst}", X, wl if wl is not None else np.arange(X.shape[1], dtype=float),
                                          pd.DataFrame(Yv, columns=cols), pd.concat(metas, ignore_index=True))
    return out


def _read_eigen_csv(path: Path) -> tuple[list[str], list[str], np.ndarray]:
    """Parse an Eigenvector DataSet CSV export -> (column labels, row labels, values)."""
    import csv

    rows = list(csv.reader(open(path, newline="")))
    # Spectra files carry an "Axisscale" row (wavelengths); property files a "Label" header row.
    ax = [i for i, r in enumerate(rows) if len(r) > 2 and r[0].strip() == "Axisscale"]
    hdr_idx = ax[0] if ax else next(i for i, r in enumerate(rows) if len(r) > 2 and r[0].strip() == "Label")
    cols = [c.strip() for c in rows[hdr_idx][2:] if c.strip() != ""]
    labels, vals = [], []
    for r in rows[hdr_idx + 1:]:
        if len(r) < 3 or r[1].strip() == "":
            continue
        labels.append(r[1].strip())
        v = []
        for c in r[2:2 + len(cols)]:
            c = c.strip()
            v.append(float("nan") if c in ("", "NaN", "nan") else float(c))
        vals.append(v)
    return cols, labels, np.asarray(vals, dtype=float)


def load_diesel() -> SpectralData:
    """SWRI diesel: NIR spectra + 7 properties (NaN where a property was not measured)."""
    _extract("diesel/SWRI_Diesel_NIR_CSV.zip")
    wcols, slabels, X = _read_eigen_csv(EXTRACT / "diesel_spec.csv")
    pcols, plabels, P = _read_eigen_csv(EXTRACT / "diesel_prop.csv")
    pidx = {lab: i for i, lab in enumerate(plabels)}
    keep = [i for i, lab in enumerate(slabels) if lab in pidx]
    Y = pd.DataFrame(P[[pidx[slabels[i]] for i in keep]], columns=[c.lower() for c in pcols])
    try:
        wl = np.array([float(c) for c in wcols])
    except ValueError:
        wl = np.arange(X.shape[1], dtype=float)
    meta = pd.DataFrame({"sample_id": [slabels[i] for i in keep]})
    return SpectralData("diesel", X[keep], wl, Y, meta)


def load_mango(version: str = "v4") -> SpectralData:
    f = RAW / f"mango_{version}" / f"MangoDMC_NIR_Data_{version}.csv"
    df = pd.read_csv(f, low_memory=False)
    spec_cols = [c for c in df.columns if str(c).replace(".", "", 1).isdigit()]
    X = df[spec_cols].to_numpy(float)
    wl = np.array([float(c) for c in spec_cols])
    if version == "v4":
        Y = pd.DataFrame({"dm": df["dry_matter"].astype(float)})
        meta = pd.DataFrame({
            "sample_id": df["reference_no"].astype(str) + "_" + df["origin"].astype(str) + "_" + df["season"].astype(str),
            "instrument": df["instrument"].astype(str), "season": df["season"].astype(int), "region": df["region"].astype(str),
            "cultivar": df["cultivar"].astype(str), "temp": df["temp"].astype(str), "physio_stage": df["physio_stage"].astype(str),
            "origin": df["origin"].astype(str), "partition": df["partition_1"].astype(str), "outlier_flag": df["outlier_flag_1"].astype(int),
            "population": df["population"].astype(str), "date": df["date"].astype(str), "spectra_no": df["spectra_no"].astype(int)})
    else:
        Y = pd.DataFrame({"dm": df["DM"].astype(float)})
        meta = pd.DataFrame({"set": df["Set"].astype(str), "season": df["Season"].astype(int), "region": df["Region"].astype(str),
                             "cultivar": df["Cultivar"].astype(str), "temp": df["Temp"].astype(str), "pop": df["Pop"].astype(str),
                             "date": df["Date"].astype(str), "type": df["Type"].astype(str)})
    return SpectralData(f"mango_{version}", X, wl, Y, meta)
