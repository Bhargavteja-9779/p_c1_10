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
from src.fleet.data import Fleet, paired_differences, replicate_cov, item_means
from src.fleet.risk import fleet_risk, noise_term


def split_items(fl: Fleet, master: str, seed: int, grouped: str | None = None):
    """grouped=None: random item split; 'session': whole acquisition sessions (date) go to one part;
    'population': whole fruit populations (date|population) go to one part."""
    rng = np.random.default_rng(seed)
    cov = fl.coverage() > 0
    on_m = cov[master]
    n_units = cov.sum(axis=1)
    multi = np.array(cov.index[on_m & (n_units >= 2)])
    solo = np.array(cov.index[on_m & (n_units == 1)])
    off = np.array(cov.index[~on_m])
    if grouped is None or fl.group is None:
        multi = rng.permutation(multi)
        t = len(multi) // 3
        T, E, C = multi[:t], multi[t:2 * t], multi[2 * t:]
    else:
        g_of = pd.Series(fl.group, index=fl.item).groupby(level=0).first()
        key = g_of.loc[multi].astype(str)
        if grouped == 'session':
            key = key.str.split('|').str[0]
        groups = rng.permutation(np.unique(key))
        # greedy assignment of whole groups to the part with the fewest items so far (T, E, C)
        parts = {0: [], 1: [], 2: []}
        sizes = key.value_counts()
        for gname in groups:
            j = min(parts, key=lambda q: sum(sizes[x] for x in parts[q]))
            parts[j].append(gname)
        T, E, C = (np.array(key.index[key.isin(parts[j])]) for j in (0, 1, 2))
    return set(np.concatenate([C, solo]).tolist()), set(T.tolist()), set(np.concatenate([E, off]).tolist()), set(E.tolist())


def _err(model, X, y):
    e = model.predict(X) - y
    return float(np.sqrt(np.mean(e ** 2))), float(np.mean(e)), float(np.std(e, ddof=1)) if len(e) > 1 else np.nan


def _lfbc_offset_var(b, D, units, items):
    """Pooled (over fleet units) between-item variance of the per-item mean projection b'd: the sampling variance
    of a label-free offset estimated from m items is this value / m (used to correct the predicted LFBC risk)."""
    v = []
    for u in np.unique(units):
        s = units == u
        df = pd.DataFrame({"i": items[s], "p": D[s] @ b}).groupby("i").p.mean()
        if len(df) > 1:
            v.append(df.var(ddof=1))
    return float(np.mean(v)) if v else 0.0


def run_scenario(fl: Fleet, master: str, seed: int = 0, min_test=20, min_pairs=5, A=30, oracle=True, targets=None, grouped=None):
    C, T, E, Ep = split_items(fl, master, seed, grouped)
    cm = (fl.unit == master) & np.isin(fl.item, list(C))
    Xc, yc, gc = fl.X[cm], fl.y[cm], fl.item[cm]
    Sigma0, _ = replicate_cov(Xc, gc)
    base = M.master_pls(Xc, yc, gc, A=A, seed=seed)
    units = [u for u in np.unique(fl.unit) if u != master]
    tcount = {u: len(set(fl.item[fl.unit == u]) & T) for u in units}
    # master means of transfer items (for the labelled cross-term check only)
    tm = (fl.unit == master) & np.isin(fl.item, list(T))
    from src.fleet.data import item_means
    ti, tX, _ = item_means(fl.X[tm], fl.item[tm])
    ty = pd.Series(fl.y[tm], index=fl.item[tm]).groupby(level=0).first().reindex(ti).to_numpy()
    tpos = {it: j for j, it in enumerate(ti)}
    rows = []
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
        tp = te & np.isin(fl.item, list(Ep))
        Xp, yp = fl.X[tp], fl.y[tp]
        npair = len(np.unique(fl.item[tp]))
        res = {"dataset": fl.name, "master": master, "seed": seed, "grouped": grouped or "none", "target": k,
               "n_fleet": len(F), "n_D": len(D), "n_test_scans": int(te.sum()), "n_test_paired_items": int(npair),
               "n_test_items": int(len(np.unique(fl.item[te]))), "n_cal": int(cm.sum())}
        frlv = M.fr_lv(base, D, Du, Sigma0, r0)
        frpls = M.fr_pls(Xc, yc, gc, D, Du, Sigma0, r0, A=A, seed=seed, ditems=Di)
        fm = np.isin(fl.unit, F) & np.isin(fl.item, list(T))
        pooled = M.pooled_pls(Xc, yc, gc, fl.X[fm], fl.y[fm], fl.item[fm], A=A, seed=seed)
        epo = M.epo_models(Xc, yc, gc, D, A=A, seed=seed)
        gls = M.glsw_models(Xc, yc, gc, D, A=A, seed=seed)
        epo_fr = M.fr_select(epo, "EPO", Xc, yc, D, Du, Sigma0, r0, seed)
        gls_fr = M.fr_select(gls, "GLSW", Xc, yc, D, Du, Sigma0, r0, seed)
        epo_def = [m for m in epo if m.name == "EPO(k=2)"][0]; epo_def = M.LinearModel(epo_def.b0, epo_def.b, "EPO-default", epo_def.info)
        gls_def = [m for m in gls if m.name == "GLSW(a=0.01)"][0]; gls_def = M.LinearModel(gls_def.b0, gls_def.b, "GLSW-default", gls_def.info)
        taus = [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100]
        tik_all = M.tikhonov_path(Xc, yc, D, Du, frpls.info["lv"], taus)
        tik = [m for m in tik_all if m.info["tau2"] != 1]  # oracle grid excludes tau2=1 (= FR-PLS itself)
        models = [base, frlv, frpls, pooled, epo_def, gls_def] + [m for m in (epo_fr, gls_fr) if m is not None]
        if epo_fr is not None:
            res["param|EPO-FR"], res["param|GLSW-FR"] = epo_fr.info["k"], gls_fr.info["alpha"]
            res["lvsel|EPO-FR"], res["lvsel|GLSW-FR"] = epo_fr.info["lv"], gls_fr.info["lv"]
        for m in models:
            r, bb, sd = _err(m, Xk, yk)
            res[f"rmse|{m.name}"], res[f"bias|{m.name}"], res[f"sep|{m.name}"] = r, bb, sd
            res[f"lv|{m.name}"] = m.info.get("lv")
            if npair >= 10:
                res[f"rmseP|{m.name}"] = _err(m, Xp, yp)[0]
        for fam, lst in (("EPO", epo), ("GLSW", gls), ("Tikhonov", tik)):
            for key, Xe, ye, ok in (("rmse", Xk, yk, True), ("rmseP", Xp, yp, npair >= 10)):
                if not ok:
                    continue
                errs = [(_err(m, Xe, ye)[0], m) for m in lst]
                e, mbest = min(errs, key=lambda t: t[0])
                res[f"{key}|{fam}-oracle"] = e
                res[f"param{key}|{fam}-oracle"] = mbest.name
        for m in tik_all:  # fleet-level tau2 curve (tau2=1 is FR-PLS at the same LV count)
            if npair >= 10:
                res[f"tauP|{m.info['tau2']:g}"] = _err(m, Xp, yp)[0]
            res[f"tauA|{m.info['tau2']:g}"] = _err(m, Xk, yk)[0]
        res["rmse_master_on_master"] = _err(base, fl.X[mt], fl.y[mt])[0] if mt.sum() > 2 else np.nan
        res["rmse_master_cv"] = float(np.sqrt(base.info["mse_cv"][base.info["lv"] - 1]))
        # ---- label-free fleet-risk predictions (+ labelled cross-term check)
        jpos = np.array([tpos[it] for it in Di])
        for m in (base, frlv, frpls):
            mse0 = m.info["mse_cv"][m.info["lv"] - 1] if m.name == "FR-PLS" else base.info["mse_cv"][m.info["lv"] - 1]
            if m.name == "FR-PLS":
                pred = float(m.info["risk_cv"][m.info["lv"] - 1])
            else:
                pred = float(fleet_risk(m.b, mse0, D, Du, Sigma0, r0))
            res[f"predF|{m.name}"] = np.sqrt(pred)
            Ru, _ = fleet_risk(m.b, mse0, D, Du, Sigma0, r0, per_unit=True)
            res[f"predUnitsF|{m.name}"] = ";".join(f"{np.sqrt(v):.4f}" for v in np.atleast_1d(Ru))
            e0 = m.b0 + tX[jpos] @ m.b - ty[jpos]
            pdx = D @ m.b
            res[f"cross|{m.name}"] = float(np.mean([2 * np.mean(e0[Du == u] * pdx[Du == u]) for u in np.unique(Du)]))
            res[f"quad|{m.name}"] = float(np.mean([np.mean(pdx[Du == u] ** 2) for u in np.unique(Du)]))
        # ---- scenario B: the target's own unlabelled transfer scans (qualification + LFBC)
        Dk, Duk, Dik, r0k = paired_differences(fl, master, [k], T)
        mk = int(len(np.unique(Dik))) if len(Dik) else 0
        res["n_pairs_target"] = mk
        if len(Dk) >= 3:
            for m in models:
                mse0 = (m.info["mse_cv"][m.info["lv"] - 1] if m.name == "FR-PLS" else
                        base.info["mse_cv"][m.info["lv"] - 1] if m.name in ("PLS-master", "FR-LV") else m.info.get("mse0", np.nan))
                pk = Dk @ m.b
                off = float(np.mean(pk))
                mc = M.LinearModel(m.b0 - off, m.b, m.name + "+LFBC")
                r, bb, _ = _err(mc, Xk, yk)
                res[f"rmse|{m.name}+LFBC"], res[f"bias|{m.name}+LFBC"] = r, bb
                if npair >= 10:
                    res[f"rmseP|{m.name}+LFBC"] = _err(mc, Xp, yp)[0]
                if m.name in ("PLS-master", "FR-LV", "FR-PLS"):
                    nt = noise_term(m.b, Sigma0, r0k)[0]
                    res[f"predK|{m.name}"] = float(np.sqrt(max(mse0 + np.mean(pk ** 2) - nt, 1e-12)))
                    # after correction: within-item scan variance + unbiased between-item variance (fleet-pooled
                    # value when m<2) + sampling variance of the offset estimated from m items
                    dfp = pd.DataFrame({"i": Dik, "p": pk})
                    im = dfp.groupby("i").p.mean()
                    v_within = float(np.mean((dfp.p - dfp.i.map(im)) ** 2))
                    vo = _lfbc_offset_var(m.b, D, Du, Di)
                    v_between = float(im.var(ddof=1)) if len(im) >= 2 else vo
                    res[f"predK|{m.name}+LFBC"] = float(np.sqrt(max(mse0 - nt + v_within + v_between + vo / max(mk, 1), 1e-12)))
            # classical standardisation with the same paired items: PDS (master PLS on standardised target spectra)
            mi_, mX_, _ = item_means(fl.X[(fl.unit == master) & np.isin(fl.item, list(T))], fl.item[(fl.unit == master) & np.isin(fl.item, list(T))])
            ki_, kX_, _ = item_means(fl.X[(fl.unit == k) & np.isin(fl.item, list(T))], fl.item[(fl.unit == k) & np.isin(fl.item, list(T))])
            common = sorted(set(mi_) & set(ki_))
            if len(common) >= 5:
                pm_ = {it: j for j, it in enumerate(mi_)}; pk_ = {it: j for j, it in enumerate(ki_)}
                Fm, f0 = M.pds(mX_[[pm_[i] for i in common]], kX_[[pk_[i] for i in common]])
                for m in (base, frpls):
                    mp_ = M.LinearModel(m.b0 + f0 @ m.b, Fm @ m.b, m.name + "+PDS")
                    res[f"rmse|{m.name}+PDS"] = _err(mp_, Xk, yk)[0]
                    if npair >= 10:
                        res[f"rmseP|{m.name}+PDS"] = _err(mp_, Xp, yp)[0]
                # slope/bias correction with the REFERENCE VALUES of the target's transfer items (labelled reference)
                ky = pd.Series(fl.y[(fl.unit == k) & np.isin(fl.item, list(T))], index=fl.item[(fl.unit == k) & np.isin(fl.item, list(T))]).groupby(level=0).first()
                for m in (base, frpls):
                    yh = m.predict(kX_[[pk_[i] for i in common]]); yt = ky.reindex(common).to_numpy()
                    sl, ic = np.polyfit(yh, yt, 1)
                    ms_ = M.LinearModel(sl * m.b0 + ic, sl * m.b, m.name + "+SBC(labelled)")
                    res[f"rmse|{m.name}+SBC(labelled)"] = _err(ms_, Xk, yk)[0]
                    if npair >= 10:
                        res[f"rmseP|{m.name}+SBC(labelled)"] = _err(ms_, Xp, yp)[0]
        rows.append(res)
    return pd.DataFrame(rows)


def choose_master(fl: Fleet, rank: int = 1) -> str:
    """Master = unit sharing the most items with other units (pre-registered rule, label-free); rank=2 gives the
    runner-up (master-choice sensitivity analysis)."""
    cov = fl.coverage() > 0
    multi = cov[cov.sum(axis=1) >= 2]
    return str(multi.sum(axis=0).sort_values(ascending=False).index[rank - 1])
