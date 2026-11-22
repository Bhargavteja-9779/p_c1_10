"""E6: simulation study of the fleet-risk estimator with known ground truth. Fleets of units with random
low-rank additive + gain effects; master calibration by PLS; risk predicted from N fleet units with m paired items
each; realised risk measured on 200 unseen units. Reports the ratio predicted/realised fleet RMSEP."""
import sys, os, warnings; sys.path.insert(0, '.'); sys.path.insert(0, 'tests'); warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from src.fleet.data import Fleet, paired_differences, replicate_cov
from src.fleet.risk import fleet_risk
from src.fleet import methods as M
OUT = '../results/e6'; os.makedirs(OUT, exist_ok=True)


def make(rng, n_items, n_units, p=60, r=2, eff=0.25, gain=0.03, noise=0.03):
    L = rng.normal(size=(p, 6)); c = rng.normal(size=(n_items, 6)); S = c @ L.T
    y = c[:, 0] + 0.5 * c[:, 1] + 0.15 * rng.normal(size=n_items)
    U = rng.normal(size=(p, 3)) / np.sqrt(p) * np.sqrt(p / 3)
    mu = 0.2 * eff * rng.normal(size=p)
    X, Y, I, Uu = [], [], [], []
    for k in range(n_units):
        a = (0 if k == 0 else 1) * (mu + eff * U @ rng.normal(size=3))
        g = 1 + (0 if k == 0 else gain * rng.normal())
        Xk = g * S[None] + a + noise * rng.normal(size=(r, n_items, p))
        for j in range(r):
            X.append(Xk[j]); Y.append(y); I.append([f'i{i}' for i in range(n_items)]); Uu.append([f'u{k}'] * n_items)
    return Fleet('sim', np.vstack(X), np.concatenate(Y), np.concatenate(I), np.concatenate(Uu), np.arange(p), 'y')


rows = []
for rep in range(30):
    rng = np.random.default_rng(rep)
    fl = make(rng, 260, 1 + 32 + 60)
    items = np.unique(fl.item); rng.shuffle(items)
    cal, tr, te = items[:120], items[120:180], items[180:]
    cm = (fl.unit == 'u0') & np.isin(fl.item, cal)
    Xc, yc, gc = fl.X[cm], fl.y[cm], fl.item[cm]
    S0, _ = replicate_cov(Xc, gc)
    base = M.master_pls(Xc, yc, gc, A=15, seed=rep)
    unseen = [f'u{k}' for k in range(33, 93)]
    def realised(m):
        return np.sqrt(np.mean([np.mean((m.predict(fl.X[(fl.unit == u) & np.isin(fl.item, te)]) - fl.y[(fl.unit == u) & np.isin(fl.item, te)]) ** 2) for u in unseen]))
    for N in (1, 2, 4, 8, 16, 32):
        for mitems in (5, 20, 60):
            fleet = [f'u{k}' for k in range(1, N + 1)]
            sub = set(tr[:mitems].tolist())
            D, Du, Di, r0 = paired_differences(fl, 'u0', fleet, sub)
            pred_m = np.sqrt(fleet_risk(base.b, base.info['mse_cv'][base.info['lv'] - 1], D, Du, S0, r0))
            fr = M.fr_pls(Xc, yc, gc, D, Du, S0, r0, A=15, seed=rep, ditems=Di)
            rows.append({'rep': rep, 'N': N, 'm': mitems, 'pred_master': pred_m, 'real_master': realised(base),
                         'pred_frpls': np.sqrt(fr.info['risk_cv'][fr.info['lv'] - 1]), 'real_frpls': realised(fr)})
    print(rep, flush=True)
df = pd.DataFrame(rows); df.to_csv(f'{OUT}/simulation.csv', index=False)
g = df.assign(r_m=df.pred_master / df.real_master, r_f=df.pred_frpls / df.real_frpls).groupby(['N', 'm'])
print(g[['r_m', 'r_f']].median().round(3).unstack())
print(g[['real_master', 'real_frpls']].mean().round(3).unstack())
