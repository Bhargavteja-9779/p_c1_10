import numpy as np
import pytest
from scipy import stats

from src.statistics.inference import (benjamini_hochberg, bootstrap_ci, clopper_pearson, holm,
                                      mcnemar_exact, sign_flip_permutation, wilcoxon_signed_rank)


def test_clopper_pearson_known():
    lo, hi = clopper_pearson(9, 10)
    assert lo == pytest.approx(0.5549839, abs=1e-6)  # R binom.test(9,10)
    assert hi == pytest.approx(0.9974714, abs=1e-6)


def test_holm_known():
    adj = holm([0.01, 0.04, 0.03, 0.005])
    assert np.allclose(adj, [0.03, 0.06, 0.06, 0.02])


def test_bh_monotone_and_bounds():
    p = np.array([0.001, 0.01, 0.02, 0.5, 0.9])
    adj = benjamini_hochberg(p)
    assert np.all(adj >= p) and np.all(adj <= 1)
    assert np.all(np.diff(adj[np.argsort(p)]) >= -1e-12)


def test_wilcoxon_matches_scipy():
    rng = np.random.default_rng(1)
    a = rng.normal(0.3, 1, 30)
    b = rng.normal(0.0, 1, 30)
    r = wilcoxon_signed_rank(a, b)
    assert r.p_value == pytest.approx(stats.wilcoxon(a, b).pvalue)
    assert -1 <= r.effect_size <= 1


def test_sign_flip_exact_small():
    a = np.array([1.0, 2.0, 3.0, 4.0])
    b = np.zeros(4)
    r = sign_flip_permutation(a, b, alternative="greater")
    assert r.p_value == pytest.approx(1 / 16)


def test_bootstrap_ci_contains_mean():
    x = np.random.default_rng(0).normal(5, 1, 200)
    est, lo, hi = bootstrap_ci(x, n_boot=2000)
    assert lo < est < hi and lo < 5 < hi


def test_mcnemar():
    assert mcnemar_exact(0, 0) == 1.0
    assert mcnemar_exact(0, 10) == pytest.approx(2 * 0.5 ** 10)
