"""Calibration methods for fleet deployment. Every method returns a LinearModel (b0, b) so that its error on
any unit and its fleet risk can be computed with the same algebra.

Label-free (fleet information = paired spectral differences D, no reference values of transfer items):
  master_pls        PLS on the master unit, LV by grouped CV + 1-SE rule (conventional practice)
  fr_lv             same PLS, LV chosen by minimum estimated fleet risk (proposed, FR-LV)
  fr_pls            fleet-risk-minimising PLS: calibration rows + sqrt(w)*D rows with target 0, weight w fixed by
                    theory (w = n / (N_units * M_u) per row, so the D-block equals n * mean_u mean (b'D)^2) (proposed)
  tikhonov          same augmentation with a free weight tau^2 (Kalivas-type Tikhonov transfer, tuned)
  epo               external parameter orthogonalisation with the first k right-singular vectors of D
  glsw              generalised least-squares weighting from the covariance of D with parameter alpha
Labelled reference:
  pooled_pls        master calibration + fleet scans of the transfer items WITH their reference values
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from sklearn.model_selection import GroupKFold

from src.models.pls import PLS1


@dataclass
class LinearModel:
    b0: float
    b: np.ndarray
    name: str = ""
    info: dict = field(default_factory=dict)

    def predict(self, X):
        return self.b0 + np.asarray(X, float) @ self.b


def _folds(groups, k, seed=0):
    groups = np.asarray(groups)
    k = int(min(k, len(np.unique(groups))))
    try:
        g = GroupKFold(n_splits=k, shuffle=True, random_state=seed)
    except TypeError:
        g = GroupKFold(n_splits=k)
    return list(g.split(np.zeros(len(groups)), groups=groups))


def pls_cv_curve(X, y, groups, A=20, k=5, seed=0):
    """Grouped-CV single-scan MSE for every LV count 1..A plus fold-level SE (for the 1-SE rule)."""
    folds = _folds(groups, k, seed)
    A = int(min(A, X.shape[1], min(len(tr) for tr, _ in folds) - 1))
    sse = np.zeros(A)
    fm = []
    for tr, te in folds:
        m = PLS1(A).fit(X[tr], y[tr])
        P = m.predict_all(X[te])
        if P.shape[1] < A:
            P = np.hstack([P, np.repeat(P[:, -1:], A - P.shape[1], axis=1)])
        r = (P - y[te][:, None]) ** 2
        sse += r.sum(0)
        fm.append(r.mean(0))
    fm = np.array(fm)
    return sse / len(y), np.sqrt(fm).std(0, ddof=1) / np.sqrt(len(fm)), A


def one_se(mse, se_rmse):
    rm = np.sqrt(mse)
    i = int(np.argmin(rm))
    return int(np.argmax(rm <= rm[i] + se_rmse[i]) + 1)


def _fit_all(X, y, A):
    m = PLS1(A).fit(X, y)
    B = m.coefs_
    if B.shape[1] < A:
        B = np.hstack([B, np.repeat(B[:, -1:], A - B.shape[1], axis=1)])
    b0 = m.y_mean_ - m.x_mean_ @ B
    return b0, B


def master_pls(X, y, groups, A=20, k=5, seed=0):
    mse, se, A = pls_cv_curve(X, y, groups, A, k, seed)
    a = one_se(mse, se)
    b0, B = _fit_all(X, y, A)
    return LinearModel(float(b0[a - 1]), B[:, a - 1], "PLS-master", {"lv": a, "mse_cv": mse, "B": B, "b0": b0, "A": A})


def fr_lv(base: LinearModel, D, units, Sigma0, r0):
    """Choose the LV count of an already fitted master PLS by minimum estimated fleet risk."""
    from src.fleet.risk import fleet_risk

    B, b0, mse = base.info["B"], base.info["b0"], base.info["mse_cv"]
    R = fleet_risk(B, mse, D, units, Sigma0, r0)
    a = int(np.argmin(R) + 1)
    return LinearModel(float(b0[a - 1]), B[:, a - 1], "FR-LV", {"lv": a, "risk_curve": R})


def _aug_weights(units, n, tau2=1.0):
    uu, inv, cnt = np.unique(units, return_inverse=True, return_counts=True)
    return tau2 * n / (len(uu) * cnt[inv])


def _fit_aug(X, y, D, units, A, tau2=1.0):
    """PLS on [X - mean; sqrt(w) D] with targets [y - mean; 0]; D rows are NOT re-centred (offsets penalised)."""
    xm, ym = X.mean(0), y.mean()
    if len(D):
        w = np.sqrt(_aug_weights(units, len(y), tau2))
        Xa = np.vstack([X - xm, D * w[:, None]])
        ya = np.concatenate([y - ym, np.zeros(len(D))])
    else:
        Xa, ya = X - xm, y - ym
    m = PLS1(A, center=False).fit(Xa, ya)
    B = m.coefs_
    if B.shape[1] < A:
        B = np.hstack([B, np.repeat(B[:, -1:], A - B.shape[1], axis=1)])
    return ym - xm @ B, B


def _unit_groups(units, k, seed):
    uu = np.unique(units)
    rng = np.random.default_rng(seed)
    uu = rng.permutation(uu)
    k = int(min(k, len(uu)))
    return [set(uu[i::k].tolist()) for i in range(k)], k


def fr_pls(X, y, groups, D, units, Sigma0, r0, A=20, k=5, seed=0, tau2=1.0, name="FR-PLS"):
    """Fleet-risk-minimising PLS with LV selected by unit-held-out cross-validated fleet risk.

    In fold f the model is fitted without master fold f and without the D rows of unit group g_f; the master
    MSE is measured on fold f and the quadratic term on the held-out units' D rows (honest, no reuse).
    """
    from src.fleet.risk import noise_term

    folds = _folds(groups, k, seed)
    ugr, ku = _unit_groups(units, len(folds), seed)
    A = int(min(A, X.shape[1], min(len(tr) for tr, _ in folds) - 1))
    sse = np.zeros(A)
    qsum, qn = {}, {}
    for f, (tr, te) in enumerate(folds):
        held = ugr[f % ku] if ku > 1 else set()
        keep = ~np.isin(units, list(held))
        b0, B = _fit_aug(X[tr], y[tr], D[keep], units[keep], A, tau2)
        P = b0[None, :] + X[te] @ B
        sse += ((P - y[te][:, None]) ** 2).sum(0)
        evalu = held if held else set(np.unique(units).tolist())
        for u in evalu:
            Pu = D[units == u] @ B
            qsum[u] = qsum.get(u, 0) + (Pu ** 2).mean(0)
            qn[u] = qn.get(u, 0) + 1
    mse = sse / len(y)
    q = np.mean([qsum[u] / qn[u] for u in qsum], axis=0)
    b0, B = _fit_aug(X, y, D, units, A, tau2)
    R = np.maximum(mse + q - noise_term(B, Sigma0, r0), 1e-12)
    a = int(np.argmin(R) + 1)
    return LinearModel(float(b0[a - 1]), B[:, a - 1], name, {"lv": a, "risk_cv": R, "mse_cv": mse, "B": B, "b0": b0, "tau2": tau2})


def tikhonov_path(X, y, D, units, lv, taus):
    """Tikhonov-transfer models for a grid of tau^2 at fixed LV (for oracle tuning)."""
    out = []
    for t in taus:
        b0, B = _fit_aug(X, y, D, units, lv, t)
        out.append(LinearModel(float(b0[lv - 1]), B[:, lv - 1], f"Tikhonov(tau2={t:g})", {"tau2": t, "lv": lv}))
    return out


def pooled_pls(X, y, groups, Xf, yf, gf, A=20, k=5, seed=0):
    Xp = np.vstack([X, Xf])
    yp = np.concatenate([y, yf])
    gp = np.concatenate([np.asarray(groups).astype(str), np.asarray(gf).astype(str)])
    m = master_pls(Xp, yp, gp, A, k, seed)
    m.name = "PLS-pooled (labelled)"
    return m


def _epo_P(D, kcomp):
    _, _, Vt = np.linalg.svd(D, full_matrices=False)
    V = Vt[:kcomp].T
    return np.eye(D.shape[1]) - V @ V.T


def epo_models(X, y, groups, D, ks=(1, 2, 3, 4, 5, 6, 8, 10), A=20, k=5, seed=0):
    out = []
    _, _, Vt = np.linalg.svd(D, full_matrices=False)
    for kc in ks:
        V = Vt[:kc].T
        P = np.eye(D.shape[1]) - V @ V.T
        m = master_pls(X @ P, y, groups, A, k, seed)
        out.append(LinearModel(m.b0, P @ m.b, f"EPO(k={kc})", {"k": kc, "lv": m.info["lv"]}))
    return out


def glsw_models(X, y, groups, D, alphas=(1e-4, 1e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1.0), A=20, k=5, seed=0):
    C = D.T @ D / max(len(D) - 1, 1)
    s2, V = np.linalg.eigh(C)
    s2 = np.clip(s2, 0, None)
    out = []
    for al in alphas:
        a_abs = al * s2.max()
        G = V @ np.diag(1.0 / np.sqrt(s2 / a_abs + 1.0)) @ V.T
        m = master_pls(X @ G, y, groups, A, k, seed)
        out.append(LinearModel(m.b0, G @ m.b, f"GLSW(a={al:g})", {"alpha": al, "lv": m.info["lv"]}))
    return out
