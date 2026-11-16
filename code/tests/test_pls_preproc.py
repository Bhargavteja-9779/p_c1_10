import numpy as np
import pytest
from sklearn.cross_decomposition import PLSRegression

from src.models.pls import PLS1, select_n_components
from src.preprocessing.spectral import MSC, Pipeline, snv


def _data(n=80, p=60, seed=0):
    rng = np.random.default_rng(seed)
    T = rng.normal(size=(n, 4))
    X = T @ rng.normal(size=(4, p)) + 0.05 * rng.normal(size=(n, p))
    y = T @ np.array([1.0, -0.5, 0.3, 0.0]) + 0.05 * rng.normal(size=n)
    return X, y


@pytest.mark.parametrize("a", [1, 3, 6])
def test_pls1_matches_sklearn(a):
    X, y = _data()
    ours = PLS1(10).fit(X, y).predict(X, a)
    sk = PLSRegression(n_components=a, scale=False).fit(X, y).predict(X).ravel()
    assert np.allclose(ours, sk, atol=1e-8)


def test_weighted_equals_duplication():
    X, y = _data(n=40)
    w = np.ones(40); w[:10] = 2.0
    Xd = np.vstack([X, X[:10]]); yd = np.concatenate([y, y[:10]])
    a = PLS1(5).fit(X, y, sample_weight=w).predict(X, 4)
    b = PLS1(5).fit(Xd, yd).predict(X, 4)
    assert np.allclose(a, b, atol=1e-8)


def test_select_components_reasonable():
    X, y = _data(n=120)
    groups = np.repeat(np.arange(60), 2)
    a, curve = select_n_components(X, y, groups, max_components=12)
    assert 2 <= a <= 6 and curve.shape == (12,)


def test_snv_rows():
    X, _ = _data()
    Z = snv(X)
    assert np.allclose(Z.mean(1), 0) and np.allclose(Z.std(1, ddof=1), 1)


def test_msc_fit_on_train_only():
    X, _ = _data()
    m = MSC().fit(X[:40])
    assert np.allclose(m.ref_, X[:40].mean(0))
    pipe = Pipeline(["msc", "snv"]).fit(X[:40])
    assert pipe.transform(X[40:]).shape == X[40:].shape
