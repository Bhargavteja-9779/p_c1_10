"""Table 1 (Markdown) generated from results/summary_v2 so that table numbers cannot drift from the analysis."""
import json, pandas as pd, numpy as np
F = json.load(open('../results/summary_v2/facts.json'))
E2 = pd.DataFrame(F['E2']); TT = pd.DataFrame(F['E2_tests'])
rows = [('Target-label-free', 'PLS-master', 'Master PLS'), ('', 'FR-LV', 'FR-LV (proposed)'), ('', 'FR-PLS', 'FR-PLS (proposed)'),
        ('', 'EPO-default', 'EPO, k = 2'), ('', 'GLSW-default', 'GLSW, α = 0.01'), ('', 'EPO-FR', 'EPO, k by fleet risk'),
        ('', 'GLSW-FR', 'GLSW, α by fleet risk'),
        ('Uses fleet reference values', 'PLS-pooled (labelled)', 'Pooled PLS'),
        ('Oracle (target reference values)', 'EPO-oracle', 'EPO, oracle k'), ('', 'GLSW-oracle', 'GLSW, oracle α'), ('', 'Tikhonov-oracle', 'Tikhonov, oracle τ²'),
        ('With LFBC (target paired items)', 'PLS-master+LFBC', 'Master PLS + LFBC'), ('', 'FR-PLS+LFBC', 'FR-PLS + LFBC'),
        ('', 'GLSW-FR+LFBC', 'GLSW (fleet risk) + LFBC'), ('', 'PLS-pooled (labelled)+LFBC', 'Pooled PLS + LFBC')]
mp = E2[(E2.family == 'mango') & (E2.metric == 'paired')].iloc[0]; ma = E2[(E2.family == 'mango') & (E2.metric == 'all-test')].iloc[0]
so = E2[E2.family == 'soil'].iloc[0]; co = E2[E2.family == 'corn'].iloc[0]
def ratio(m):
    ref = 'FR-PLS+LFBC' if m.endswith('LFBC') else 'FR-PLS'
    if m == ref: return '—'
    t = TT[(TT.family == 'mango') & (TT.metric == 'rmseP') & (TT.A == ref) & (TT.B == m)]
    if not len(t): return ''
    t = t.iloc[0]; star = '*' if t.p_holm < 0.05 else ''
    return f"{t.median_ratio:.2f} ({t.ci90_lo:.2f}–{t.ci90_hi:.2f}){star}"
f = lambda v: '' if v is None or (isinstance(v, float) and np.isnan(v)) else f'{v:.2f}'
out = ['**Table 1.** Error of the calibration strategies on unseen units (leave-one-unit-out). Mango: RMS of RMSEP (%DM) over target-unit/season cases on paired test fruit (62 cases, 25 physical units) and on all test fruit (89 cases, 30 units). Soil: median over 36 unit × property cases of RMSEP relative to the master PLS. Corn: RMS of RMSEP over 8 instrument × property cases (property units). Last column: median per-physical-unit RMSEP ratio of FR-PLS (or FR-PLS + LFBC for LFBC rows) to the method in the row, with 90 % bootstrap CI; * Holm-adjusted Wilcoxon p < 0.05.', '',
       '| Group | Method | Mango, paired | Mango, all test | Soil (rel.) | Corn | FR-PLS / method |', '|---|---|---|---|---|---|---|']
for g, k, name in rows:
    out.append(f"| {g} | {name} | {f(mp.get(k))} | {f(ma.get(k))} | {f(so.get(k))} | {f(co.get(k))} | {ratio(k)} |")
open('../manuscript/sections/04b_table1.md', 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
