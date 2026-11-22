"""Leave-one-unit-out (LOUO) fleet protocol.

For one fleet dataset, a master unit and an item-split seed:
  * items scanned on the master AND on >=1 other unit ("multi" items) are split 1/3 transfer (T), 1/3 test, 1/3
    calibration; master-only items go to calibration (C); items never scanned on the master go to test.
  * for each target unit k (!= master): the fleet F = remaining units with >= min_pairs transfer items. All
    label-free fleet information (D) comes from T scans on F; the target unit contributes NOTHING to model fitting
    or to the fleet-risk prediction. Its test scans are used only to measure the realised error.
  * scenario B (unit qualification): the target's own T scans (unlabelled) give the unit-specific risk estimate.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.fleet import methods as M
from src.fleet.data import Fleet, paired_differences, replicate_cov
from src.fleet.risk import fleet_risk


def split_items(fl: Fleet, master: str, seed: int):
    rng = np.random.default_rng(seed)
    cov = fl.coverage() > 0
    on_m = cov[master]
    n_units = cov.sum(1)
    multi = np.array(cov.index[on_m & (n_units >= 2)])
    solo = np.array(cov.index[on_m & (n_units == 1)])
    off = np.array(cov.index[~on_m])
    multi = rng.permutation(multi)
    t = len(multi) // 3
    T, E, C = multi[:t], multi[t:2 * t], multi[2 * t:]
    return set(np.concatenate([C, solo]).tolist()), set(T.tolist()), set(np.concatenate([E, off]).tolist()), set(E.tolist())


def _err(model, X, y):
    e = model.predict(X) - y
    return float(np.sqrt(np.mean(e ** 2))), float(np.mean(e)), float(np.std(e, ddof=1)) if len(e) > 1 else np.nan


def run_scenario(fl: Fleet, master: str, seed: int = 0, min_test=20, min_pairs=5, A=20, oracle=True, targets=None):
    C, T, E, Ep = split_items(fl, master, seed)
    cm = (fl.unit == master) & np.isin(fl.item, list(C))
    Xc, yc, gc = fl.X[cm], fl.y[cm], fl.item[cm]
    Sigma0, _ = replicate_cov(Xc, gc)
    base = M.master_pls(Xc, yc, gc, A=A, seed=seed)
    lvA = base.info["A"]
    units = [u for u in np.unique(fl.unit) if u != master]
    # transfer-item counts per unit
    tcount = {u: len(set(fl.item[fl.unit == u]) & T) for u in units}
    rows = []
    # master test error (reference, same items type as targets)
    mt = (fl.unit == master) & np.isin(fl.item, list(E))
    for k in (targets or units):
        te = (fl.unit == k) & np.isin(fl.item, list(E))
        if te.sum() < min_test or len(np.unique(fl.item[te])) < min_test // 2:
            continue
        F = [u for u in units if u != k and tcount[u] >= min_pairs]
        if len(F) < 1:
            continue
        D, Du, Di, r0 = paired_differences(fl, master, F, T)
        Xk, yk = fl.X[te], fl.y[te]
        tp = te & np.isin(fl.item, list(Ep))  # paired test items (also scanned on the master): pure unit effect
        Xp, yp = fl.X[tp], fl.y[tp]
        npair = len(np.unique(fl.item[tp]))
        res = {"dataset": fl.name, "master": master, "seed": seed, "target": k, "n_fleet": len(F), "n_D": len(D),
               "n_test_scans": int(te.sum()), "n_test_paired_items": int(npair), "n_test_items": int(len(np.unique(fl.item[te]))), "n_cal": int(cm.sum())}
        models = [base, M.fr_lv(base, D, Du, Sigma0, r0)]
        models.append(M.fr_pls(Xc, yc, gc, D, Du, Sigma0, r0, A=A, seed=seed, ditems=Di))
        # labelled pooled reference: fleet scans of transfer items WITH labels
        fm = np.isin(fl.unit, F) & np.isin(fl.item, list(T))
        models.append(M.pooled_pls(Xc, yc, gc, fl.X[fm], fl.y[fm], fl.item[fm], A=A, seed=seed))
        # default-parameter baselines (as commonly used)
        epo = M.epo_models(Xc, yc, gc, D, A=A, seed=seed)
        gls = M.glsw_models(Xc, yc, gc, D, A=A, seed=seed)
        tik = M.tikhonov_path(Xc, yc, D, Du, models[2].info["lv"], [0.01, 0.1, 0.3, 1, 3, 10, 100])
        for m in models:
            r, b, s = _err(m, Xk, yk)
            res[f"rmse|{m.name}"], res[f"bias|{m.name}"], res[f"sep|{m.name}"] = r, b, s
            res[f"lv|{m.name}"] = m.info.get("lv")
            if npair >= 10:
                res[f"rmseP|{m.name}"] = _err(m, Xp, yp)[0]
        for fam, lst, default in (("EPO", epo, "EPO(k=2)"), ("GLSW", gls, "GLSW(a=0.01)"), ("Tikhonov", tik, None)):
            errs = [(_err(m, Xk, yk)[0], m) for m in lst]
            best = min(errs, key=lambda t: t[0])
            res[f"rmse|{fam}-oracle"] = best[0]
            res[f"param|{fam}-oracle"] = best[1].name
            if default:
                dm = [m for m in lst if m.name == default][0]
                res[f"rmse|{fam}-default"] = _err(dm, Xk, yk)[0]
            res[f"rmseall|{fam}"] = ";".join(f"{m.name}={e:.4f}" for e, m in errs)
            if npair >= 10:
                ep = [(_err(m, Xp, yp)[0], m) for m in lst]
                res[f"rmseP|{fam}-oracle"] = min(e for e, _ in ep)
                if default:
                    res[f"rmseP|{fam}-default"] = [e for e, m in ep if m.name == default][0]
        # master error on master test items
        res["rmse_master_on_master"] = _err(base, fl.X[mt], fl.y[mt])[0] if mt.sum() > 2 else np.nan
        res["rmse_master_cv"] = float(np.sqrt(base.info["mse_cv"][base.info["lv"] - 1]))
        # ---- risk predictions (label-free) for the master PLS and FR-LV and FR-PLS
        for m in models[:3]:
            if m.name == "FR-PLS":
                pred = float(m.info["risk_cv"][m.info["lv"] - 1])
            else:
                a = m.info["lv"]
                pred = float(fleet_risk(base.info["B"][:, a - 1], base.info["mse_cv"][a - 1], D, Du, Sigma0, r0))
            res[f"predF|{m.name}"] = np.sqrt(pred)
            # per-unit risks in the fleet (for predictive interval)
            Ru, _ = fleet_risk(m.b, (base.info["mse_cv"][m.info["lv"] - 1] if m.name != "FR-PLS" else m.info["mse_cv"][m.info["lv"] - 1]),
                               D, Du, Sigma0, r0, per_unit=True)
            res[f"predUnitsF|{m.name}"] = ";".join(f"{np.sqrt(v):.4f}" for v in np.atleast_1d(Ru))
        # ---- scenario B: unit-specific (target's own unlabelled transfer scans)
        Dk, Duk, Dik, r0k = paired_differences(fl, master, [k], T)
        res["n_pairs_target"] = int(len(np.unique(Dik))) if len(Dik) else 0
        if len(Dk) >= 3:
            for m in models[:3]:
                mse0 = (base.info["mse_cv"][m.info["lv"] - 1] if m.name != "FR-PLS" else m.info["mse_cv"][m.info["lv"] - 1])
                res[f"predK|{m.name}"] = float(np.sqrt(fleet_risk(m.b, mse0, Dk, Duk, Sigma0, r0k)))
                # label-free bias correction from the target's paired items
                off = float(np.mean(Dk @ m.b))
                mc = M.LinearModel(m.b0 - off, m.b, m.name + "+LFBC")
                r, b, s = _err(mc, Xk, yk)
                res[f"rmse|{m.name}+LFBC"], res[f"bias|{m.name}+LFBC"] = r, b
                if npair >= 10:
                    res[f"rmseP|{m.name}+LFBC"] = _err(mc, Xp, yp)[0]
                # predicted risk after correction: remove the squared mean term
                q = np.mean((Dk @ m.b) ** 2) - off ** 2
                from src.fleet.risk import noise_term
                pr = mse0 + q - noise_term(m.b, Sigma0, r0k)[0]
                res[f"predK|{m.name}+LFBC"] = float(np.sqrt(max(pr, 1e-12)))
        rows.append(res)
    return pd.DataFrame(rows)


def choose_master(fl: Fleet) -> str:
    """Master = unit sharing the most items with other units (pre-registered rule, label-free)."""
    cov = fl.coverage() > 0
    multi = cov[cov.sum(axis=1) >= 2]
    return str(multi.sum(axis=0).idxmax())
