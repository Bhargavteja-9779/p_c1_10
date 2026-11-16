"""Point-prediction and interval metrics."""
from __future__ import annotations

import numpy as np


def rmse(y, yhat):
    y, yhat = np.asarray(y, float), np.asarray(yhat, float)
    return float(np.sqrt(np.mean((y - yhat) ** 2)))


def bias(y, yhat):
    return float(np.mean(np.asarray(yhat, float) - np.asarray(y, float)))


def sep(y, yhat):
    """Bias-corrected standard error of prediction."""
    e = np.asarray(yhat, float) - np.asarray(y, float)
    return float(np.std(e, ddof=1))


def r2(y, yhat):
    y, yhat = np.asarray(y, float), np.asarray(yhat, float)
    return float(1 - np.sum((y - yhat) ** 2) / np.sum((y - y.mean()) ** 2))


def rpd(y, yhat):
    return float(np.std(np.asarray(y, float), ddof=1) / sep(y, yhat))


def coverage(y, lo, hi):
    y = np.asarray(y, float)
    return float(np.mean((y >= lo) & (y <= hi)))


def mean_width(lo, hi):
    return float(np.mean(np.asarray(hi, float) - np.asarray(lo, float)))


def interval_score(y, lo, hi, alpha):
    """Gneiting & Raftery (2007) interval score (lower is better)."""
    y, lo, hi = (np.asarray(v, float) for v in (y, lo, hi))
    return float(np.mean((hi - lo) + (2 / alpha) * (lo - y) * (y < lo) + (2 / alpha) * (y - hi) * (y > hi)))
