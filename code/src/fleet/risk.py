"""Fleet risk: label-free estimation of the prediction error of a linear calibration on unseen instrument units.

Notation (single scans, linear predictor yhat = b0 + b'x):
  e_0  = error of the scan on the master unit,  e_k = error of a scan of the same item on unit k,
  D    = x_k - mean(master scans of the item).
Exact identity (algebra, no assumption):  e_k = e_0bar + b'D, with e_0bar the error of the averaged master scans.
Writing x_0 = s + eps_0 and x_k = s + a_k + eps_k (a_k: unit effect, eps: scan noise, Sigma_0 = cov(eps_0)),

  E[e_k^2] = MSE_0 + E[(b'D)^2] - (1 + 1/r0) b'Sigma_0 b + 2 E[(b's - y) b'a_k]                     (Prop. 1)

where MSE_0 is the single-scan master MSE and r0 the number of master scans averaged per item. The last term is
zero when the unit effect is uncorrelated with the master residual (testable with labelled pairs); the
label-free estimator drops it. Averaging over units gives the risk for a randomly drawn unit of the fleet
("fleet risk"); restricting to one unit gives that unit's risk ("unit risk").
"""
from __future__ import annotations

import numpy as np


def quad_terms(B: np.ndarray, D: np.ndarray, units: np.ndarray) -> tuple[np.ndarray, list]:
    """Per-unit mean of (b'D)^2 for each column of B. Returns (n_units, n_models) and the unit order."""
    B = B[:, None] if B.ndim == 1 else B
    P = D @ B  # (M, n_models)
    uu = list(dict.fromkeys(units.tolist()))
    out = np.vstack([np.mean(P[units == u] ** 2, axis=0) for u in uu])
    return out, uu


def noise_term(B: np.ndarray, Sigma0: np.ndarray, r0: float) -> np.ndarray:
    B = B[:, None] if B.ndim == 1 else B
    return (1.0 + 1.0 / r0) * np.einsum("pa,pq,qa->a", B, Sigma0, B)


def fleet_risk(B, mse0, D, units, Sigma0, r0, per_unit: bool = False, cross=None):
    """Label-free fleet risk (MSE scale) for coefficient vectors B (p,) or (p, A).

    mse0  : master single-scan MSE for each model (cross-validated), shape (A,) or scalar.
    cross : optional (n_units, A) labelled cross-term estimates 2E[(b's-y)b'a]; omitted in label-free mode.
    Units are weighted equally (each unit is one draw from the instrument population).
    """
    B = np.asarray(B, float)
    B2 = B[:, None] if B.ndim == 1 else B
    q, uu = quad_terms(B2, D, units)
    nt = noise_term(B2, Sigma0, r0)
    R_u = np.atleast_1d(np.asarray(mse0, float))[None, :] + q - nt[None, :]
    if cross is not None:
        R_u = R_u + cross
    R_u = np.maximum(R_u, 1e-12)
    if per_unit:
        return (R_u[:, 0] if B.ndim == 1 else R_u), uu
    R = R_u.mean(axis=0)
    return R[0] if B.ndim == 1 else R


def unit_bootstrap_ci(R_u: np.ndarray, n_boot: int = 5000, conf: float = 0.95, seed: int = 0):
    """Percentile CI of the fleet-mean risk by resampling units (the population sampling unit)."""
    R_u = np.asarray(R_u, float)
    rng = np.random.default_rng(seed)
    k = len(R_u)
    bs = R_u[rng.integers(0, k, size=(n_boot, k))].mean(axis=1)
    a = (1 - conf) / 2
    return float(np.quantile(bs, a)), float(np.quantile(bs, 1 - a))


def predictive_interval_new_unit(R_u: np.ndarray, conf: float = 0.9):
    """Distribution-free interval for the risk of ONE new unit from the fleet's unit risks (order statistics).

    With N exchangeable units the probability that a new unit's risk falls inside [R_(i), R_(N+1-i)] is
    (N+1-2i)/(N+1); we return the widest symmetric pair with level >= conf if available, else (min, max).
    """
    r = np.sort(np.asarray(R_u, float))
    N = len(r)
    best = (r[0], r[-1], (N - 1) / (N + 1))
    for i in range(1, N // 2 + 1):
        lev = (N + 1 - 2 * i) / (N + 1)
        if lev >= conf:
            best = (r[i - 1], r[N - i], lev)
    return best
