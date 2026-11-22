"""E4: fleet-size and transfer-set-size learning curves for FR-PLS; E3b: number of target paired items for
label-free bias correction (LFBC) and unit qualification. Mango seasons 2016-2018 (largest fleets) + NeoSpectra OC."""
import sys, os, time, warnings; sys.path.insert(0, '.')
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from src.fleet import builders as B, methods as M
from src.fleet.data import paired_differences, replicate_cov
from src.fleet.protocol import split_items, choose_master, _lfbc_offset_var
from src.fleet.risk import fleet_risk, noise_term
OUT = '../results/e4_v2'; os.makedirs(OUT, exist_ok=True)


def rm(m, X, y):
    return float(np.sqrt(np.mean((m.predict(X) - y) ** 2)))


def run(fl, tag, seeds=(0, 1, 2), Ns=(1, 2, 4, 8, 99), ms=(3, 5, 10, 20, 999), mk=(1, 2, 3, 5, 10, 20)):
    master = choose_master(fl)
    rows, rowsB = [], []
    for seed in seeds:
        rng = np.random.default_rng(100 + seed)
        C, T, E, Ep = split_items(fl, master, seed)
        cm = (fl.unit == master) & np.isin(fl.item, list(C))
        Xc, yc, gc = fl.X[cm], fl.y[cm], fl.item[cm]
        S0, _ = replicate_cov(Xc, gc)
        base = M.master_pls(Xc, yc, gc, A=30, seed=seed)
        units = [u for u in np.unique(fl.unit) if u != master]
        tc = {u: sorted(set(fl.item[fl.unit == u]) & T) for u in units}
        for k in units:
            tp = (fl.unit == k) & np.isin(fl.item, list(Ep))
            if len(np.unique(fl.item[tp])) < 10:
                continue
            Xp, yp = fl.X[tp], fl.y[tp]
            F = [u for u in units if u != k and len(tc[u]) >= 5]
            # --- N curve (all transfer items of chosen units) and m curve (all units, m items per unit)
            for kind, grid in (('N', Ns), ('m', ms)):
                for g, rep in [(g, rep) for g in grid for rep in range(3 if kind == 'N' else 1)]:
                    if kind == 'N' and (g >= len(F) or g == 99) and rep > 0:
                        continue
                    if kind == 'N':
                        if g > len(F) and g != 99:
                            continue
                        Fs = list(rng.choice(F, size=min(g, len(F)), replace=False))
                        items = T
                    else:
                        Fs = F
                        items = set()
                        for u in F:
                            its = tc[u]
                            items |= set(rng.choice(its, size=min(g, len(its)), replace=False).tolist())
                    D, Du, Di, r0 = paired_differences(fl, master, Fs, items)
                    m = M.fr_pls(Xc, yc, gc, D, Du, S0, r0, A=30, seed=seed, ditems=Di)
                    rows.append({'tag': tag, 'seed': seed, 'target': k, 'curve': kind, 'value': g, 'rep': rep, 'n_units': len(Fs),
                                 'n_D': len(D), 'rmseP_FRPLS': rm(m, Xp, yp), 'rmseP_master': rm(base, Xp, yp),
                                 'predF_FRPLS': float(np.sqrt(m.info['risk_cv'][m.info['lv'] - 1]))})
            # --- E3b: target paired items for LFBC + unit-specific risk (master PLS and FR-PLS with full fleet)
            D, Du, Di, r0 = paired_differences(fl, master, F, T)
            frp = M.fr_pls(Xc, yc, gc, D, Du, S0, r0, A=30, seed=seed, ditems=Di)
            for mod, mse0 in ((base, base.info['mse_cv'][base.info['lv'] - 1]), (frp, frp.info['mse_cv'][frp.info['lv'] - 1])):
                its_k = tc[k]
                vo = _lfbc_offset_var(mod.b, D, Du, Di)
                for g in mk:
                    if g > len(its_k):
                        continue
                    for rep in range(10):
                        sub = set(rng.choice(its_k, size=g, replace=False).tolist())
                        Dk, Duk, _, r0k = paired_differences(fl, master, [k], sub)
                        pk = Dk @ mod.b
                        off = float(np.mean(pk))
                        q = np.mean(pk ** 2)
                        predK = np.sqrt(max(mse0 + q - noise_term(mod.b, S0, r0k)[0], 1e-12))
                        predKc = np.sqrt(max(mse0 + q - off ** 2 - noise_term(mod.b, S0, r0k)[0] + vo / g, 1e-12))
                        mc = M.LinearModel(mod.b0 - off, mod.b)
                        rowsB.append({'tag': tag, 'seed': seed, 'target': k, 'model': mod.name, 'm_target': g, 'rep': rep,
                                      'rmseP': rm(mod, Xp, yp), 'rmseP_LFBC': rm(mc, Xp, yp), 'predK': predK, 'predK_LFBC': predKc,
                                      'rmse_cv_master': float(np.sqrt(mse0))})
        print(tag, seed, time.strftime('%X'), flush=True)
    pd.DataFrame(rows).to_csv(f'{OUT}/{tag}_curves.csv', index=False)
    pd.DataFrame(rowsB).to_csv(f'{OUT}/{tag}_targetm.csv', index=False)


if __name__ == '__main__':
    for s in sys.argv[1:]:
        if s.isdigit():
            run(B.mango(int(s)), f'mango{s}')
        else:
            run(B.neospectra(s), f'neo_{s}')
