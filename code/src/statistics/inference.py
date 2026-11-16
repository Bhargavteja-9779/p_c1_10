"""Statistical inference utilities used for all quantitative claims.

Design principles
-----------------
* The unit of analysis must be chosen by the caller (e.g. one value per
  dataset x seed x scenario, never individual spectra when spectra are nested).
* Paired designs use paired tests; multiple comparisons are corrected (Holm by
  default, Benjamini-Hochberg optionally).
* Every test returns the statistic, p-value, effect size and a confidence
  interval so the manuscript can report all four.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from scipy import stats


# ---------------------------------------------------------------- intervals
def clopper_pearson(k: int, n: int, conf: float = 0.95) -> tuple[float, float]:
    """Exact binomial CI for a proportion (e.g. empirical coverage)."""
    a = 1 - conf
    lo = 0.0 if k == 0 else stats.beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - a / 2, k + 1, n - k)
    return float(lo), float(hi)


def bootstrap_ci(x, stat=np.mean, n_boot: int = 10000, conf: float = 0.95, seed: int = 0,
                 method: str = "percentile") -> tuple[float, float, float]:
    """Nonparametric bootstrap CI of ``stat`` over the 1-D sample ``x``.

    Returns (estimate, lo, hi). ``method`` in {"percentile", "bca"}.
    """
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    rng = np.random.default_rng(seed)
    est = float(stat(x))
    if len(x) < 2:
        return est, float("nan"), float("nan")
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))
    boots = np.apply_along_axis(stat, 1, x[idx])
    a = 1 - conf
    if method == "percentile":
        lo, hi = np.quantile(boots, [a / 2, 1 - a / 2])
        return est, float(lo), float(hi)
    # BCa
    z0 = stats.norm.ppf((boots < est).mean() + 0.5 * (boots == est).mean())
    jack = np.array([stat(np.delete(x, i)) for i in range(len(x))])
    jm = jack.mean()
    num = ((jm - jack) ** 3).sum()
    den = 6.0 * (((jm - jack) ** 2).sum() ** 1.5)
    acc = num / den if den > 0 else 0.0
    zs = stats.norm.ppf([a / 2, 1 - a / 2])
    adj = stats.norm.cdf(z0 + (z0 + zs) / (1 - acc * (z0 + zs)))
    lo, hi = np.quantile(boots, np.clip(adj, 0, 1))
    return est, float(lo), float(hi)


def paired_bootstrap_diff(a, b, stat=np.mean, n_boot: int = 10000, conf: float = 0.95, seed: int = 0):
    """CI for stat(a - b) over paired units."""
    d = np.asarray(a, float) - np.asarray(b, float)
    return bootstrap_ci(d, stat=stat, n_boot=n_boot, conf=conf, seed=seed)


# ---------------------------------------------------------------- paired tests
@dataclass
class PairedTestResult:
    test: str
    n: int
    statistic: float
    p_value: float
    effect_size: float
    effect_size_name: str
    estimate: float
    estimate_name: str
    ci_low: float
    ci_high: float
    alternative: str

    def as_dict(self) -> dict:
        return asdict(self)


def hodges_lehmann_paired(d: np.ndarray) -> float:
    """Hodges-Lehmann estimator for paired differences (median of Walsh averages)."""
    d = np.asarray(d, float)
    i, j = np.triu_indices(len(d))
    return float(np.median((d[i] + d[j]) / 2.0))


def wilcoxon_signed_rank(a, b, alternative: str = "two-sided", conf: float = 0.95, seed: int = 0,
                         zero_method: str = "wilcox") -> PairedTestResult:
    """Wilcoxon signed-rank test on paired samples with matched-pairs rank-biserial r.

    Effect size r = (W+ - W-) / (W+ + W-) computed on non-zero differences
    (Kerby 2014). CI: bootstrap CI of the Hodges-Lehmann estimate.
    """
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    d = a - b
    nz = d[d != 0]
    if len(nz) == 0:
        return PairedTestResult("wilcoxon", len(d), 0.0, 1.0, 0.0, "rank_biserial", 0.0, "hodges_lehmann", 0.0, 0.0, alternative)
    res = stats.wilcoxon(a, b, alternative=alternative, zero_method=zero_method)
    ranks = stats.rankdata(np.abs(nz))
    wp, wm = ranks[nz > 0].sum(), ranks[nz < 0].sum()
    r = float((wp - wm) / (wp + wm))
    hl, lo, hi = bootstrap_ci(d, stat=hodges_lehmann_paired if len(d) <= 400 else np.median, conf=conf, seed=seed, n_boot=4000)
    return PairedTestResult("wilcoxon_signed_rank", len(d), float(res.statistic), float(res.pvalue), r, "rank_biserial",
                            hl, "hodges_lehmann", lo, hi, alternative)


def sign_flip_permutation(a, b, stat=np.mean, n_perm: int = 20000, alternative: str = "two-sided", seed: int = 0,
                          conf: float = 0.95) -> PairedTestResult:
    """Exact-in-distribution paired permutation (sign-flip) test of stat(a-b)=0."""
    d = np.asarray(a, float) - np.asarray(b, float)
    rng = np.random.default_rng(seed)
    obs = stat(d)
    n = len(d)
    if n <= 16:  # enumerate all sign patterns
        signs = np.array(np.meshgrid(*[[-1, 1]] * n)).reshape(n, -1).T
    else:
        signs = rng.choice([-1.0, 1.0], size=(n_perm, n))
    null = np.array([stat(s * d) for s in signs])
    if alternative == "two-sided":
        p = (np.sum(np.abs(null) >= abs(obs) - 1e-12) + (0 if n <= 16 else 1)) / (len(null) + (0 if n <= 16 else 1))
    elif alternative == "greater":
        p = (np.sum(null >= obs - 1e-12) + (0 if n <= 16 else 1)) / (len(null) + (0 if n <= 16 else 1))
    else:
        p = (np.sum(null <= obs + 1e-12) + (0 if n <= 16 else 1)) / (len(null) + (0 if n <= 16 else 1))
    sd = np.std(d, ddof=1) if n > 1 else float("nan")
    dz = float(obs / sd) if sd and sd > 0 else 0.0
    est, lo, hi = bootstrap_ci(d, stat=stat, conf=conf, seed=seed, n_boot=4000)
    return PairedTestResult("sign_flip_permutation", n, float(obs), float(min(1.0, p)), dz, "cohens_dz", est,
                            "mean_difference", lo, hi, alternative)


def mcnemar_exact(b01: int, b10: int) -> float:
    """Exact McNemar p-value from discordant counts (two-sided binomial)."""
    n = b01 + b10
    if n == 0:
        return 1.0
    return float(min(1.0, 2 * stats.binom.cdf(min(b01, b10), n, 0.5)))


# ---------------------------------------------------------------- multiplicity
def holm(pvals) -> np.ndarray:
    p = np.asarray(pvals, float)
    m = len(p)
    order = np.argsort(p)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        val = (m - rank) * p[i]
        running = max(running, val)
        adj[i] = min(1.0, running)
    return adj


def benjamini_hochberg(pvals) -> np.ndarray:
    p = np.asarray(pvals, float)
    m = len(p)
    order = np.argsort(p)
    adj = np.empty(m)
    prev = 1.0
    for rank in range(m - 1, -1, -1):
        i = order[rank]
        prev = min(prev, p[i] * m / (rank + 1))
        adj[i] = prev
    return np.minimum(adj, 1.0)


# ---------------------------------------------------------------- omnibus
def friedman(*groups) -> tuple[float, float]:
    res = stats.friedmanchisquare(*groups)
    return float(res.statistic), float(res.pvalue)


def cliffs_delta(a, b) -> float:
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    gt = (a[:, None] > b[None, :]).sum()
    lt = (a[:, None] < b[None, :]).sum()
    return float((gt - lt) / (len(a) * len(b)))
