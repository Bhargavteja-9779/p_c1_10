"""Spectral preprocessing (fit on training data only; transform any data).

All transformers follow fit/transform so that no information from validation or
test spectra leaks into preprocessing parameters (e.g. the MSC reference).
"""
from __future__ import annotations

import numpy as np
from scipy.signal import savgol_filter


def snv(X: np.ndarray) -> np.ndarray:
    """Standard normal variate (row-wise; no fitted parameters)."""
    X = np.asarray(X, float)
    mu = X.mean(axis=1, keepdims=True)
    sd = X.std(axis=1, ddof=1, keepdims=True)
    sd[sd == 0] = 1.0
    return (X - mu) / sd


def savgol(X: np.ndarray, window: int = 17, poly: int = 2, deriv: int = 2) -> np.ndarray:
    """Savitzky-Golay smoothing/derivative along wavelengths (row-wise; no fitted parameters)."""
    return savgol_filter(np.asarray(X, float), window_length=window, polyorder=poly, deriv=deriv, axis=1)


class MSC:
    """Multiplicative scatter correction with reference = training mean spectrum."""

    def fit(self, X):
        self.ref_ = np.asarray(X, float).mean(axis=0)
        return self

    def transform(self, X):
        X = np.asarray(X, float)
        A = np.vstack([np.ones_like(self.ref_), self.ref_]).T
        coef, *_ = np.linalg.lstsq(A, X.T, rcond=None)  # (2, n)
        return (X - coef[0][:, None]) / coef[1][:, None]


class Pipeline:
    """Sequence of named steps: 'snv', ('savgol', dict), 'msc', ('range', (lo, hi))."""

    def __init__(self, steps, wl: np.ndarray | None = None):
        self.steps = steps
        self.wl = wl

    def fit(self, X):
        self._fitted = []
        Z = np.asarray(X, float)
        for st in self.steps:
            name, kw = (st, {}) if isinstance(st, str) else st
            if name == "msc":
                m = MSC().fit(Z)
                self._fitted.append(("msc", m))
                Z = m.transform(Z)
            else:
                self._fitted.append((name, kw))
                Z = self._apply(name, kw, Z)
        return self

    def _apply(self, name, kw, Z):
        if name == "snv":
            return snv(Z)
        if name == "savgol":
            return savgol(Z, **kw)
        if name == "range":
            lo, hi = kw
            idx = (self.wl >= lo) & (self.wl <= hi)
            return Z[:, idx]
        raise ValueError(name)

    def transform(self, X):
        Z = np.asarray(X, float)
        for name, obj in self._fitted:
            Z = obj.transform(Z) if name == "msc" else self._apply(name, obj, Z)
        return Z

    def fit_transform(self, X):
        return self.fit(X).transform(X)
