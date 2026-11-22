"""E7: physical decomposition of unit effects. For each fleet unit, the mean paired difference of raw absorbance
spectra (same items, unit minus master) is regressed on [1, mean spectrum (gain), d mean/d lambda (wavelength
shift), d2 mean/d lambda2 (bandwidth)]. Reports R2 and the implied wavelength shift (nm)."""
import sys, os, warnings; sys.path.insert(0, '.'); warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from src.data.loaders import load_mango
from src.fleet.data import Fleet, paired_differences, item_means
from src.fleet.protocol import choose_master
OUT = '../results/e7'; os.makedirs(OUT, exist_ok=True)
rows = []


def analyse(fl, tag):
    master = choose_master(fl)
    units = [u for u in np.unique(fl.unit) if u != master]
    allitems = np.unique(fl.item)
    mi, mX, _ = item_means(fl.X[fl.unit == master], fl.item[fl.unit == master])
    xbar = mX.mean(0)
    wl = fl.wl
    d1 = np.gradient(xbar, wl); d2 = np.gradient(d1, wl)
    Z = np.c_[np.ones_like(xbar), xbar - xbar.mean(), d1, d2]  # shift coef: d ~ -dlambda * dxbar/dlambda (nm)
    for u in units:
        D, du, di, _ = paired_differences(fl, master, [u], allitems)
        if len(np.unique(di)) < 10:
            continue
        d = D.mean(0)
        coef, *_ = np.linalg.lstsq(Z, d, rcond=None)
        fit = Z @ coef
        sst = np.sum(d ** 2)  # uncentred: the offset is part of the unit effect to be explained
        r2 = 1 - np.sum((d - fit) ** 2) / sst
        part = {}  # unique (drop-one) contributions, uncentred
        for j, nm in enumerate(['offset', 'gain', 'shift', 'bandwidth']):
            Zr = np.delete(Z, j, axis=1)
            cr, *_ = np.linalg.lstsq(Zr, d, rcond=None)
            part[nm] = (np.sum((d - Zr @ cr) ** 2) - np.sum((d - fit) ** 2)) / sst
        # shape part: offset removed (what a derivative pre-treatment leaves); centred R2 of gain+shift+bandwidth
        dc = d - d.mean(); Zs = np.c_[xbar - xbar.mean(), d1, d2]; Zs = Zs - Zs.mean(0)
        cs, *_ = np.linalg.lstsq(Zs, dc, rcond=None); sss = np.sum(dc ** 2)
        r2s = 1 - np.sum((dc - Zs @ cs) ** 2) / sss
        shp = {}
        for j, nm in enumerate(['gain', 'shift', 'bandwidth']):
            Zr = np.delete(Zs, j, axis=1); cr, *_ = np.linalg.lstsq(Zr, dc, rcond=None)
            shp[f'shapeR2_unique_{nm}'] = (np.sum((dc - Zr @ cr) ** 2) - np.sum((dc - Zs @ cs) ** 2)) / sss
        shp['offset_share'] = 1 - sss / sst
        shp['R2_shape'] = r2s
        rows.append({**shp, 'dataset': tag, 'master': master, 'unit': u, 'n_items': len(np.unique(di)), 'R2': r2,
                     'shift_nm': float(-coef[2]), 'gain_rel': float(coef[1]), 'offset': float(coef[0]),
                     'rms_diff': float(np.sqrt(np.mean(d ** 2))),
                     'rel_diff': float(np.sqrt(np.mean(d ** 2)) / np.std(xbar)), **{f'partR2_{k}': v for k, v in part.items()}})


d = load_mango('v4')
r = (d.wl >= 684) & (d.wl <= 990)
for s in (2016, 2017, 2018):
    m = ((d.meta.season == s) & (d.meta.outlier_flag == 0)).to_numpy()
    fl = Fleet(f'mango{s}', d.X[m][:, r], d.Y.dm.to_numpy()[m], d.meta.sample_id.to_numpy()[m].astype(str),
               d.meta.instrument.to_numpy()[m].astype(str), d.wl[r], 'dm')
    analyse(fl, f'mango{s}')
neo = pd.read_csv('../data/raw/neospectra/Neospectra_WoodwellKSSL_soil+site+NIR.csv', low_memory=False)
neo = neo[neo.SCANNER.isin([f'NEO{i}' for i in range(1, 8)])]
spec = [c for c in neo.columns if str(c).replace('.', '', 1).isdigit()]
wl = np.array([float(c) for c in spec]); o = np.argsort(wl)
A = np.log10(100 / np.clip(neo[spec].to_numpy(float)[:, o], 1e-3, None))
analyse(Fleet('neospectra', A, np.zeros(len(A)), neo.kssl_id.astype(str).to_numpy(), neo.SCANNER.astype(str).to_numpy(), wl[o], 'none'), 'neospectra')
df = pd.DataFrame(rows); df.to_csv(f'{OUT}/unit_effect_decomposition.csv', index=False)
print(df.round(3).to_string())
print(df.groupby('dataset')[['R2', 'offset_share', 'R2_shape', 'shapeR2_unique_gain', 'shapeR2_unique_shift', 'shapeR2_unique_bandwidth', 'rel_diff']].median().round(3))
