"""v2 analysis: every number quoted in the manuscript is written to results/summary_v2/facts.json.
Inference unit: physical instrument unit (mango: results averaged over seasons per unit serial; soil: per unit,
averaged over properties after normalising by the master; corn: instrument x property)."""
import sys, glob, os, json, warnings; sys.path.insert(0, '.'); warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from scipy import stats
from src.statistics.inference import holm
OUT = '../results/summary_v2'; os.makedirs(OUT, exist_ok=True)
F = {}
rms = lambda s: float(np.sqrt(np.nanmean(np.asarray(s, float) ** 2)))
df = pd.concat([pd.read_csv(f) for f in sorted(glob.glob('../results/e1e2_v2/*.csv'))], ignore_index=True)
df['family'] = np.select([df.dataset.str.startswith('mango'), df.dataset.str.startswith('neo')], ['mango', 'soil'], 'corn')
for c in [c for c in df.columns if c.startswith('rmse|')]:   # outside mango every test item is paired
    cp = 'rmseP|' + c[5:]
    if cp not in df: df[cp] = np.nan
    df.loc[df.family != 'mango', cp] = df.loc[df.family != 'mango', c]
METH = ['PLS-master', 'FR-LV', 'FR-PLS', 'EPO-default', 'GLSW-default', 'EPO-FR', 'GLSW-FR', 'PLS-pooled (labelled)',
        'EPO-oracle', 'GLSW-oracle', 'Tikhonov-oracle']
LF = [m + '+LFBC' for m in ['PLS-master', 'FR-LV', 'FR-PLS', 'EPO-FR', 'GLSW-FR', 'EPO-default', 'GLSW-default', 'PLS-pooled (labelled)']]
T = df.groupby(['grouped', 'family', 'dataset', 'target']).mean(numeric_only=True).reset_index()
T.to_csv(f'{OUT}/per_target.csv', index=False)
P = T[T.grouped == 'none']

# ---------- counts
mg = P[P.family == 'mango']
F['mango_seasons'] = sorted(mg.dataset.unique().tolist())
F['mango_units_in_seasons'] = int(pd.read_csv('../results/e1e2_v2/mango_2015_none.csv').shape[0] > 0) and None
F['mango_target_cases_all'] = int(len(mg)); F['mango_target_cases_paired'] = int(mg['rmseP|PLS-master'].notna().sum())
F['mango_physical_units_paired'] = int(mg.loc[mg['rmseP|PLS-master'].notna(), 'target'].nunique())
F['mango_physical_units_all'] = int(mg.target.nunique())
F['mango_masters'] = sorted(set(df[df.family == 'mango'].master.astype(str)))
for fam in ('soil', 'corn'):
    d = P[P.family == fam]; F[f'{fam}_target_cases'] = int(len(d)); F[f'{fam}_units'] = int(d.target.nunique())

# ---------- E1 unit risk (label-free) and fleet risk
def e1(d, mod, key='rmseP'):
    x, y = d[f'predK|{mod}'], d[f'{key}|{mod}']; ok = x.notna() & y.notna(); x, y = x[ok], y[ok]
    if len(x) < 3: return None
    return {'n': int(len(x)), 'r': float(stats.pearsonr(x, y)[0]), 'rho': float(stats.spearmanr(x, y)[0]),
            'median_ratio': float(np.median(x / y)), 'mdape_%': float(100 * np.median(np.abs(x - y) / y))}
for fam in ('mango', 'soil', 'corn'):
    d = P[P.family == fam]
    for mod in ('PLS-master', 'FR-LV', 'FR-PLS', 'PLS-master+LFBC', 'FR-PLS+LFBC'):
        F[f'E1unit|{fam}|{mod}'] = e1(d, mod)
# fleet level (LOUO), per dataset x seed: mean predF vs RMS realised over targets
R = df[df.grouped == 'none']
for fam in ('mango', 'soil', 'corn'):
    for mod in ('PLS-master', 'FR-LV', 'FR-PLS'):
        sub = R[(R.family == fam)].dropna(subset=[f'predF|{mod}', f'rmseP|{mod}'])
        if not len(sub): continue
        g = sub.groupby(['dataset', 'seed']).apply(lambda s: pd.Series({'pred': s[f'predF|{mod}'].mean(), 'real': rms(s[f'rmseP|{mod}'])}))
        cov = []
        for _, r in sub.iterrows():
            u = np.array([float(v) for v in str(r[f'predUnitsF|{mod}']).split(';')])
            if len(u) >= 3: cov.append(u.min() <= r[f'rmseP|{mod}'] <= u.max())
        F[f'E1fleet|{fam}|{mod}'] = {'pred_mean': float(g.pred.mean()), 'real_mean': float(g.real.mean()), 'ratio_median': float(np.median(g.pred / g.real)),
                                    'range_coverage_%': float(100 * np.mean(cov)) if cov else None, 'n_cases': int(len(sub))}
        F[f'cross_over_quad|{fam}|{mod}'] = float(np.median(sub[f'cross|{mod}'] / sub[f'quad|{mod}']))
        F[f'cross_over_risk|{fam}|{mod}'] = float(np.median(sub[f'cross|{mod}'] / (sub[f'predF|{mod}'] ** 2)))

# ---------- E2 methods: RMS over target cases, both metrics; tests on physical units
tab = []
for fam in ('mango', 'soil', 'corn'):
    d = P[P.family == fam]
    for key in ('rmseP', 'rmse'):
        if fam != 'mango' and key == 'rmse': continue
        row = {'family': fam, 'metric': 'paired' if key == 'rmseP' else 'all-test'}
        base = d[f'{key}|PLS-master']
        for m in METH + LF:
            c = f'{key}|{m}'
            if c not in d: continue
            ok = d[c].notna() & base.notna()
            row[m] = rms(d.loc[ok, c]) if fam != 'soil' else float(np.median(d.loc[ok, c] / base[ok]))  # soil: mixed units -> median ratio
        row['n_cases'] = int(base.notna().sum())
        tab.append(row)
E2 = pd.DataFrame(tab); E2.to_csv(f'{OUT}/E2_methods.csv', index=False)
F['E2'] = E2.to_dict(orient='records')

def unitagg(d, a, b, key='rmseP'):
    x = d[[ 'target', f'{key}|{a}', f'{key}|{b}']].dropna()
    x['lr'] = np.log(x[f'{key}|{a}'] / x[f'{key}|{b}'])
    return x.groupby('target').lr.mean()
tests = []
for fam in ('mango', 'soil', 'corn'):
    d = P[P.family == fam]
    for key in (('rmseP', 'rmse') if fam == 'mango' else ('rmseP',)):
        for a, comps in (('FR-PLS', [m for m in METH if m != 'FR-PLS']), ('FR-PLS+LFBC', [m for m in LF if m != 'FR-PLS+LFBC'])):
            for b in comps:
                if f'{key}|{b}' not in d or f'{key}|{a}' not in d: continue
                lr = unitagg(d, a, b, key) if fam != 'corn' else np.log(d[f'{key}|{a}'] / d[f'{key}|{b}']).dropna()
                if len(lr) < 5: continue
                rng = np.random.default_rng(0)
                bs = np.array([np.median(rng.choice(lr.values, len(lr))) for _ in range(4000)])
                lo, hi = np.exp(np.quantile(bs, [0.05, 0.95]))
                tests.append({'family': fam, 'metric': key, 'A': a, 'B': b, 'n_units': int(len(lr)), 'median_ratio': float(np.exp(np.median(lr))),
                              'ci90_lo': float(lo), 'ci90_hi': float(hi), 'equivalent_10%': bool(lo > 0.9 and hi < 1 / 0.9),
                              'A_better_%': float(100 * np.mean(lr < 0)), 'p': float(stats.wilcoxon(lr).pvalue)})
TT = pd.DataFrame(tests)
TT['p_holm'] = np.nan
for _, idx in TT.groupby(['family', 'metric', 'A']).groups.items():
    TT.loc[idx, 'p_holm'] = holm(TT.loc[idx, 'p'].values)
TT.to_csv(f'{OUT}/E2_tests_physical_units.csv', index=False)
F['E2_tests'] = TT.to_dict(orient='records')
# selected parameters of tuned / oracle baselines (grid-edge check)
for fam in ('mango',):
    d = R[R.family == fam]
    F['EPO_FR_k_counts'] = d['param|EPO-FR'].value_counts().to_dict()
    F['GLSW_FR_alpha_counts'] = {str(k): int(v) for k, v in d['param|GLSW-FR'].value_counts().items()}
    F['EPO_oracle_counts'] = d['paramrmseP|EPO-oracle'].value_counts().to_dict()
    F['GLSW_oracle_counts'] = d['paramrmseP|GLSW-oracle'].value_counts().to_dict()
    F['Tik_oracle_counts'] = d['paramrmseP|Tikhonov-oracle'].value_counts().to_dict()
    F['LV_mean'] = {m: float(d[f'lv|{m}'].mean()) for m in ('PLS-master', 'FR-LV', 'FR-PLS')}
    F['LV_FRPLS_max'] = float(d['lv|FR-PLS'].max())
    F['master_cv_rmse_range'] = [float(d.rmse_master_cv.min()), float(d.rmse_master_cv.max())]
    F['master_paired_rmse_range'] = [float(P[P.family == 'mango']['rmseP|PLS-master'].min()), float(P[P.family == 'mango']['rmseP|PLS-master'].max())]

# ---------- robustness: population-grouped split (mango)
G = T[(T.grouped == 'population') & (T.family == 'mango')]
if len(G):
    F['grouped'] = {'n_cases_paired': int(G['rmseP|PLS-master'].notna().sum()),
                    'E1unit_master': e1(G, 'PLS-master'), 'E1unit_FRPLS': e1(G, 'FR-PLS'),
                    'rms': {m: rms(G[f'rmseP|{m}']) for m in ['PLS-master', 'FR-LV', 'FR-PLS', 'EPO-FR', 'GLSW-FR', 'PLS-pooled (labelled)', 'PLS-master+LFBC', 'FR-PLS+LFBC'] if f'rmseP|{m}' in G}}
    Pg = P[P.dataset.isin(G.dataset.unique()) & (P.family == 'mango')]
    F['grouped']['rms_random_same_seasons'] = {m: rms(Pg[f'rmseP|{m}']) for m in F['grouped']['rms']}
json.dump(F, open(f'{OUT}/facts.json', 'w'), indent=1, default=str)
print(json.dumps({k: v for k, v in F.items() if not k.startswith('E2')}, indent=1, default=str)[:6000])
print(E2.round(3).to_string())
print(TT[TT.metric == 'rmseP'].round(3).to_string())
