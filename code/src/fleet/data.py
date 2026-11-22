"""Paired-fleet data containers.

A *fleet dataset* holds single scans x (preprocessed), the instrument unit that produced each scan, the physical
item (fruit, soil sample, tablet) that was scanned, and the item's reference value y. The same item scanned on
several units provides the paired information used by the fleet-risk estimator; no reference value of a
transfer item is ever used by the label-free methods.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Fleet:
    name: str
    X: np.ndarray          # (n_scans, p) preprocessed spectra
    y: np.ndarray          # (n_scans,) reference value of the scanned item (NaN allowed)
    item: np.ndarray       # (n_scans,) item id (str)
    unit: np.ndarray       # (n_scans,) instrument unit id (str)
    wl: np.ndarray
    property: str
    group: np.ndarray | None = None  # (n_scans,) acquisition session/population of the item (for grouped splits)

    def mask(self, m) -> "Fleet":
        m = np.asarray(m)
        return Fleet(self.name, self.X[m], self.y[m], self.item[m], self.unit[m], self.wl, self.property,
                     None if self.group is None else self.group[m])

    def items_on(self, unit) -> np.ndarray:
        return np.unique(self.item[self.unit == unit])

    def coverage(self) -> pd.DataFrame:
        """Items x units table of scan counts."""
        return pd.crosstab(pd.Series(self.item, name="item"), pd.Series(self.unit, name="unit"))


def item_means(X: np.ndarray, item: np.ndarray):
    """Average the scans of each item -> (unique items, mean spectra, n scans per item)."""
    codes, uniq = pd.factorize(pd.Series(item), sort=True)
    n = np.bincount(codes)
    S = np.zeros((len(uniq), X.shape[1]))
    np.add.at(S, codes, X)
    return np.asarray(uniq), S / n[:, None], n


def replicate_cov(X: np.ndarray, item: np.ndarray) -> tuple[np.ndarray, int]:
    """Pooled within-item (replicate-scan) covariance and its degrees of freedom."""
    codes, uniq = pd.factorize(pd.Series(item), sort=True)
    n = np.bincount(codes)
    S = np.zeros((len(uniq), X.shape[1]))
    np.add.at(S, codes, X)
    R = X - (S / n[:, None])[codes]
    dof = int(len(X) - len(uniq))
    return (R.T @ R) / max(dof, 1), dof


def paired_differences(fl: Fleet, master: str, units, items) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Single-scan differences D = x_{scan on unit k} - mean(master scans of the same item).

    Returns D (M, p), unit label per row, item label per row and the mean number of master scans per item (r0),
    which is needed for the replicate-noise correction of the risk estimator.
    """
    items = set(np.asarray(items).tolist())
    mm = (fl.unit == master) & np.isin(fl.item, list(items))
    mi, mX, mn = item_means(fl.X[mm], fl.item[mm])
    pos = {it: j for j, it in enumerate(mi)}
    rows, ru, ri, r0 = [], [], [], []
    for u in units:
        if u == master:
            continue
        sel = np.where((fl.unit == u) & np.isin(fl.item, list(pos)))[0]
        if len(sel) == 0:
            continue
        j = np.array([pos[it] for it in fl.item[sel]])
        rows.append(fl.X[sel] - mX[j])
        ru.append(fl.unit[sel])
        ri.append(fl.item[sel])
        r0.append(mn[j])
    if not rows:
        return np.zeros((0, fl.X.shape[1])), np.array([]), np.array([]), 1.0
    r0 = np.concatenate(r0)
    return np.vstack(rows), np.concatenate(ru), np.concatenate(ri), float(np.mean(1.0 / r0)) ** -1
