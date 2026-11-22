"""E4 summaries (fleet-size / item curves) + evaluation of the label-free accept / bias-correct / reject rule.
Specification: a unit is fit for use if its realised RMSEP <= SPEC x master CV RMSE (SPEC=1.5)."""
import sys, glob, os, json, warnings; sys.path.insert(0, '.'); warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from scipy import stats
OUT = '../results/summary_v3'; os.makedirs(OUT, exist_ok=True)
rms = lambda s: float(np.sqrt(np.nanmean(np.asarray(s, float) ** 2)))
F = {}
cur = pd.concat([pd.read_csv(f) for f in glob.glob('../results/e4_v3/mango*_curves.csv')])
c = cur.groupby(['tag', 'target', 'curve', 'value']).mean(numeric_only=True).reset_index()
def boot_rms(x, B=2000, seed=0):
    x = np.asarray(x, float); rng = np.random.default_rng(seed)
    bs = [rms(x[rng.integers(0, len(x), len(x))]) for _ in range(B)]
    return float(np.quantile(bs, 0.05)), float(np.quantile(bs, 0.95))
cv = []
for (cu, v), d in c.groupby(['curve', 'value']):
    lo, hi = boot_rms(d.rmseP_FRPLS); plo, phi = boot_rms(d.predF_FRPLS)
    cv.append({'curve': cu, 'value': v, 'n': len(d), 'FRPLS': rms(d.rmseP_FRPLS), 'FRPLS_lo': lo, 'FRPLS_hi': hi,
               'pred': rms(d.predF_FRPLS), 'pred_lo': plo, 'pred_hi': phi, 'master': rms(d.rmseP_master),
               'n_units_used_max': int(cur[(cur.curve == cu) & (cur.value == v)].n_units.max()), 'n_units_used_min': int(cur[(cur.curve == cu) & (cur.value == v)].n_units.min())})
F['curves'] = cv
tm = pd.concat([pd.read_csv(f) for f in glob.glob('../results/e4_v3/mango*_targetm.csv')])
F['n_target_units_e4'] = int(tm.groupby(['tag', 'target']).ngroups)
rows, dec = [], []
for (mod, m), d in tm.groupby(['model', 'm_target']):
    per = d.groupby(['tag', 'target']).mean(numeric_only=True)
    rp = [np.corrcoef(x.predK, x.rmseP)[0, 1] for _, x in d.groupby(['seed', 'rep'])]
    rows.append({'model': mod, 'm': int(m), 'raw': rms(per.rmseP), 'lfbc': rms(per.rmseP_LFBC), 'pred_lfbc': rms(per.predK_LFBC),
                 'r_single_draw_median': float(np.median(rp)),
                 'mdape_single_%': float(100 * np.median(np.abs(d.predK - d.rmseP) / d.rmseP)),
                 'mdape_lfbc_single_%': float(100 * np.median(np.abs(d.predK_LFBC - d.rmseP_LFBC) / d.rmseP_LFBC))})
    for SPEC in (1.25, 1.5, 2.0):
        thr = SPEC * d.rmse_cv_master
        ok_true, ok_pred = d.rmseP <= thr, d.predK <= thr
        okc_true, okc_pred = d.rmseP_LFBC <= thr, d.predK_LFBC <= thr
        # three-way rule: accept if predK<=thr; else bias-correct if predK_LFBC<=thr; else reject
        action = np.where(ok_pred, 'accept', np.where(okc_pred, 'correct', 'reject'))
        realised_after = np.where(action == 'accept', d.rmseP, np.where(action == 'correct', d.rmseP_LFBC, np.nan))
        bad_deployed = np.nanmean(np.where(action == 'reject', np.nan, realised_after > thr))
        dec.append({'model': mod, 'm': int(m), 'spec': SPEC, 'n': int(len(d)), 'prevalence_unfit_raw_%': 100 * float((~ok_true).mean()),
                    'false_accept_%': 100 * float((ok_pred & ~ok_true).sum() / max((~ok_true).sum(), 1)),
                    'false_reject_%': 100 * float((~ok_pred & ok_true).sum() / max(ok_true.sum(), 1)),
                    'accuracy_accept_decision_%': 100 * float((ok_pred == ok_true).mean()),
                    'share_accept_%': 100 * float((action == 'accept').mean()), 'share_correct_%': 100 * float((action == 'correct').mean()),
                    'share_reject_%': 100 * float((action == 'reject').mean()),
                    'deployed_out_of_spec_%': 100 * float(bad_deployed),
                    'unfit_after_LFBC_true_%': 100 * float((~okc_true).mean())})
F['targetm'] = rows; F['decision'] = dec
pd.DataFrame(rows).to_csv(f'{OUT}/E4_targetm.csv', index=False); pd.DataFrame(dec).to_csv(f'{OUT}/E4_decision.csv', index=False)
json.dump(F, open(f'{OUT}/facts_e4.json', 'w'), indent=1)
print(pd.DataFrame(F['curves']).round(3).to_string())
F['fleet_sizes_all'] = [int(cur[cur.value == 99].n_units.min()), int(cur[cur.value == 99].n_units.max())]; print(pd.DataFrame(rows).round(3).to_string())
print(pd.DataFrame(dec).query('spec==1.5').round(1).to_string())
json.dump(F, open(f'{OUT}/facts_e4.json', 'w'), indent=1)
