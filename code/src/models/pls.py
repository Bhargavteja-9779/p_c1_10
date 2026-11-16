"""Fast PLS1 (single response) returning regression vectors for ALL component counts.

NIPALS PLS1 with deflation of X; R = W (P'W)^-1, and the coefficient vector for
a components is  b_a = sum_{j<=a} R[:, j] q_j.  One fit therefore yields every
latent-variable count, which makes cross-validated LV selection cheap.
Verified against sklearn.cross_decomposition.PLSRegression(scale=False) in tests.
"""
from __future__ import annotations

import numpy as np


class PLS1:
    def __init__(self, n_components: int = 20):
        self.n_components = n_components

    def fit(self, X, y, sample_weight=None):
        X = np.asarray(X, float)
        y = np.asarray(y, float).ravel()
        n, p = X.shape
        if sample_weight is None:
            w_s = np.ones(n)
        else:
            w_s = np.asarray(sample_weight, float)
        w_s = w_s / w_s.sum()
        self.x_mean_ = w_s @ X
        self.y_mean_ = float(w_s @ y)
        sw = np.sqrt(w_s * n)
        Xa = (X - self.x_mean_) * sw[:, None]
        ya = (y - self.y_mean_) * sw
        A = int(min(self.n_components, n - 1, p))
        W = np.zeros((p, A))
        P = np.zeros((p, A))
        q = np.zeros(A)
        for a in range(A):
            w = Xa.T @ ya
            nw = np.linalg.norm(w)
            if nw < 1e-14:
                A = a
                break
            w /= nw
            t = Xa @ w
            tt = t @ t
            if tt < 1e-14:
                A = a
                break
            pl = Xa.T @ t / tt
            qa = (ya @ t) / tt
            Xa = Xa - np.outer(t, pl)
            ya = ya - qa * t
            W[:, a], P[:, a], q[a] = w, pl, qa
        W, P, q = W[:, :A], P[:, :A], q[:A]
        R = W @ np.linalg.inv(P.T @ W)
        self.coefs_ = np.cumsum(R * q[None, :], axis=1)  # (p, A): column a-1 = a components
        self.W_, self.P_, self.q_, self.R_ = W, P, q, R
        self.n_fitted_ = A
        return self

    def predict(self, X, n_components: int | None = None):
        X = np.asarray(X, float)
        a = self.n_fitted_ if n_components is None else int(min(n_components, self.n_fitted_))
        return (X - self.x_mean_) @ self.coefs_[:, a - 1] + self.y_mean_

    def predict_all(self, X):
        """(n, A) predictions for every component count 1..A."""
        X = np.asarray(X, float)
        return (X - self.x_mean_) @ self.coefs_ + self.y_mean_

    def scores(self, X, n_components: int):
        return (np.asarray(X, float) - self.x_mean_) @ self.R_[:, :n_components]


def select_n_components(X, y, groups, max_components: int = 20, n_splits: int = 5, rule: str = "1se", seed: int = 0):
    """Group-aware K-fold CV over all LV counts at once; returns (best_a, rmsecv_curve).

    rule='min' -> argmin RMSECV; '1se' -> smallest a within one standard error of the minimum
    (fold-level SE), which is the conventional guard against over-fitting.
    """
    from sklearn.model_selection import GroupKFold

    X = np.asarray(X, float)
    y = np.asarray(y, float).ravel()
    groups = np.asarray(groups)
    k = int(min(n_splits, len(np.unique(groups))))
    gkf = GroupKFold(n_splits=k, shuffle=True, random_state=seed) if "shuffle" in GroupKFold.__init__.__code__.co_varnames else GroupKFold(n_splits=k)
    A = int(min(max_components, X.shape[1], int(len(y) * (k - 1) / k) - 1))
    fold_mse = []
    for tr, te in gkf.split(X, y, groups):
        m = PLS1(A).fit(X[tr], y[tr])
        P = m.predict_all(X[te])
        if P.shape[1] < A:  # pad if early termination
            P = np.hstack([P, np.repeat(P[:, -1:], A - P.shape[1], axis=1)])
        fold_mse.append(((P - y[te][:, None]) ** 2).mean(axis=0))
    fold_mse = np.array(fold_mse)  # (k, A)
    rmse = np.sqrt(fold_mse.mean(axis=0))
    if rule == "min":
        return int(np.argmin(rmse) + 1), rmse
    se = np.sqrt(fold_mse).std(axis=0, ddof=1) / np.sqrt(len(fold_mse))
    best = int(np.argmin(rmse))
    thresh = rmse[best] + se[best]
    a = int(np.argmax(rmse <= thresh) + 1)
    return a, rmse
