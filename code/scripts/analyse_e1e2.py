"""Summaries for E1 (risk prediction), E2 (methods), E3 (LFBC/qualification). Statistical unit = target unit
(results averaged over item-split seeds first, to avoid pseudo-replication)."""
import sys, glob, os, warnings; sys.path.insert(0, '.'); warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from scipy import stats
from src.statistics.inference import holm
OUT = '../results/e1e2/summary'; os.makedirs(OUT, exist_ok=True)
fs = sorted(glob.glob('../results/e1e2/*.csv'))
df = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
df['family'] = df.dataset.str.replace(r'_.*', '', regex=True).str.replace(r'\d{4}', '', regex=True)
# prefer paired-test metric; for datasets where all test items are paired, rmseP==rmse
for c in [c for c in df.columns if c.startswith('rmse|')]:
    cp = 'rmseP|' + c[5:]
    if cp not in df:
        df[cp] = np.nan
    df[cp] = df[cp].fillna(df[c]) if not df.family.eq('mango').all() else df[cp]
    df.loc[df.family != 'mango', cp] = df.loc[df.family != 'mango', c]
g = df.groupby(['dataset', 'target'])
T = g.mean(numeric_only=True).reset_index()
T['family'] = T.dataset.str.replace(r'_.*', '', regex=True).str.replace(r'\d{4}', '', regex=True)
T.to_csv(f'{OUT}/per_target.csv', index=False)

# ---------------- E1: unit-risk prediction (label-free) vs realised, master PLS
rows = []
for fam, d in T.groupby('family'):
    for mod in ['PLS-master', 'FR-LV', 'FR-PLS']:
        x, y = d[f'predK|{mod}'], d[f'rmseP|{mod}']
        ok = x.notna() & y.notna()
        x, y = x[ok], y[ok]
        if len(x) < 3:
            continue
        rows.append({'family': fam, 'model': mod, 'n_targets': len(x), 'pearson_r': stats.pearsonr(x, y)[0],
                     'spearman': stats.spearmanr(x, y)[0], 'median_ratio_pred/real': np.median(x / y),
                     'MAPE_%': 100 * np.median(np.abs(x - y) / y), 'mean_real': y.mean(), 'mean_pred': x.mean()})
e1 = pd.DataFrame(rows); e1.to_csv(f'{OUT}/E1_unit_risk.csv', index=False); print('E1 unit risk\n', e1.round(3).to_string())

# ---------------- E1b: fleet-level prediction for an unseen unit (LOUO) : predF vs realised per target, plus
# coverage of the order-statistic prediction interval built from the other units' unit risks.
rows = []
for fam, d in df.groupby('family'):
    for mod in ['PLS-master', 'FR-LV', 'FR-PLS']:
        sub = d[[f'predF|{mod}', f'rmseP|{mod}', f'predUnitsF|{mod}', 'dataset', 'seed']].dropna()
        if len(sub) < 3:
            continue
        cov, wid = [], []
        for _, r in sub.iterrows():
            u = np.sort(np.array([float(v) for v in str(r[f'predUnitsF|{mod}']).split(';')]))
            lo, hi = u[0], u[-1]
            cov.append(lo <= r[f'rmseP|{mod}'] <= hi)
        # fleet mean: RMS of realised across targets within dataset/seed vs mean predF
        agg = sub.groupby(['dataset', 'seed']).apply(lambda s: pd.Series({'pred': s[f'predF|{mod}'].mean(), 'real': np.sqrt(np.mean(s[f'rmseP|{mod}'] ** 2))}))
        rows.append({'family': fam, 'model': mod, 'n': len(sub), 'range_cover_%': 100 * np.mean(cov),
                     'fleet_pred_mean': agg.pred.mean(), 'fleet_real_mean': agg.real.mean(),
                     'fleet_ratio_median': np.median(agg.pred / agg.real)})
e1b = pd.DataFrame(rows); e1b.to_csv(f'{OUT}/E1_fleet_risk.csv', index=False); print('\nE1 fleet risk\n', e1b.round(3).to_string())

# ---------------- E2: methods (paired test)
meths = ['PLS-master', 'FR-LV', 'FR-PLS', 'PLS-pooled (labelled)', 'EPO-default', 'EPO-oracle', 'GLSW-default',
         'GLSW-oracle', 'Tikhonov-oracle', 'PLS-master+LFBC', 'FR-PLS+LFBC']
rows = []
for fam, d in T.groupby('family'):
    for ds_name, dd in list(d.groupby('dataset')) + [('ALL ' + fam, d)]:
        r = {'family': fam, 'dataset': ds_name, 'n_targets': len(dd)}
        for m in meths:
            c = f'rmseP|{m}'
            if c in dd:
                r[m] = np.sqrt(np.nanmean(dd[c] ** 2))
        rows.append(r)
e2 = pd.DataFrame(rows); e2.to_csv(f'{OUT}/E2_methods_rms.csv', index=False); print('\nE2 RMS over targets\n', e2.round(3).to_string())
# paired tests FR-PLS vs each competitor, per family (targets pooled across seasons/properties)
rows = []
for fam, d in T.groupby('family'):
    pv = []
    for m in meths:
        if m == 'FR-PLS' or f'rmseP|{m}' not in d:
            continue
        a, b = d['rmseP|FR-PLS'], d[f'rmseP|{m}']
        ok = a.notna() & b.notna()
        if ok.sum() < 5:
            continue
        lr = np.log(a[ok] / b[ok])
        p = stats.wilcoxon(lr).pvalue
        rows.append({'family': fam, 'vs': m, 'n': int(ok.sum()), 'median_ratio_FRPLS/other': float(np.exp(np.median(lr))),
                     'wins_%': 100 * float(np.mean(lr < 0)), 'p': p})
e2t = pd.DataFrame(rows)
e2t['p_holm'] = np.concatenate([holm(x.p.values) for _, x in e2t.groupby('family')])
e2t.to_csv(f'{OUT}/E2_tests.csv', index=False); print('\nE2 tests\n', e2t.round(4).to_string())
