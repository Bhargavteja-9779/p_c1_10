import numpy as np
from src.fleet.data import Fleet, paired_differences, replicate_cov, item_means
from src.fleet.risk import fleet_risk


def simulate(n_items=400, n_units=30, p=40, r=3, seed=0, noise=0.05, eff=0.3, gain=0.0):
    rng = np.random.default_rng(seed)
    L = rng.normal(size=(p, 5))
    c = rng.normal(size=(n_items, 5))
    S = c @ L.T
    beta = np.zeros(5); beta[0] = 1.0
    y = c @ beta + 0.1 * rng.normal(size=n_items)
    U = rng.normal(size=(p, 2))
    mu = 0.1 * eff * rng.normal(size=p)
    X, Y, I, Uu = [], [], [], []
    for k in range(n_units):
        a = mu + eff * U @ rng.normal(size=2)
        g = 1 + gain * rng.normal()
        for i in range(n_items):
            for _ in range(r):
                X.append(g * S[i] + (0 if k == 0 else a) + noise * rng.normal(size=p))
                Y.append(y[i]); I.append(f"i{i}"); Uu.append(f"u{k}")
    return Fleet("sim", np.array(X), np.array(Y), np.array(I), np.array(Uu), np.arange(p), "y")


def test_exact_identity():
    fl = simulate(n_items=30, n_units=3, seed=1)
    b = np.random.default_rng(2).normal(size=fl.X.shape[1]); b0 = 0.3
    D, du, di, r0 = paired_differences(fl, "u0", ["u1"], np.unique(fl.item))
    mi, mX, _ = item_means(fl.X[fl.unit == "u0"], fl.item[fl.unit == "u0"])
    pos = {it: j for j, it in enumerate(mi)}
    sel = fl.unit == "u1"
    ek = b0 + fl.X[sel] @ b - fl.y[sel]
    e0bar = b0 + mX[[pos[i] for i in fl.item[sel]]] @ b - fl.y[sel]
    assert np.allclose(ek, e0bar + D @ b)


def _setup(n_units, n_items, seed):
    fl = simulate(n_items=n_items, n_units=n_units, seed=seed, r=2)
    rng = np.random.default_rng(seed + 1)
    items = np.unique(fl.item); rng.shuffle(items)
    k = len(items)
    cal, tr, te = items[: k // 2], items[k // 2: 3 * k // 4], items[3 * k // 4:]
    m = (fl.unit == "u0") & np.isin(fl.item, cal)
    Xc, yc = fl.X[m], fl.y[m]
    b = np.linalg.lstsq(np.c_[np.ones(len(Xc)), Xc - Xc.mean(0)], yc, rcond=None)[0]
    b0, bv = b[0] - Xc.mean(0) @ b[1:], b[1:]
    mt = (fl.unit == "u0") & np.isin(fl.item, te)
    mse0 = np.mean((b0 + fl.X[mt] @ bv - fl.y[mt]) ** 2)
    S0, _ = replicate_cov(Xc, fl.item[m])
    return fl, b0, bv, mse0, S0, tr, te


def _real(fl, b0, bv, u, te):
    s = (fl.unit == u) & np.isin(fl.item, te)
    return np.mean((b0 + fl.X[s] @ bv - fl.y[s]) ** 2)


def test_unit_risk_tracks_realised():
    fl, b0, bv, mse0, S0, tr, te = _setup(12, 400, 3)
    units = [f"u{k}" for k in range(1, 12)]
    D, du, _, r0 = paired_differences(fl, "u0", units, tr)
    Ru, uu = fleet_risk(bv, mse0, D, du, S0, r0, per_unit=True)
    real = np.array([_real(fl, b0, bv, u, te) for u in uu])
    assert np.corrcoef(Ru, real)[0, 1] > 0.9
    assert 0.8 < np.mean(Ru) / np.mean(real) < 1.25


def test_fleet_risk_unbiased_for_unseen_units():
    fl, b0, bv, mse0, S0, tr, te = _setup(161, 80, 5)
    fleet = [f"u{k}" for k in range(1, 81)]
    unseen = [f"u{k}" for k in range(81, 161)]
    D, du, _, r0 = paired_differences(fl, "u0", fleet, tr)
    pred = fleet_risk(bv, mse0, D, du, S0, r0)
    real = np.mean([_real(fl, b0, bv, u, te) for u in unseen])
    assert abs(pred - real) / real < 0.2, (pred, real)
    assert pred > 1.5 * mse0
