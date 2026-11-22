"""Manuscript figures 2-5 (Fig. 1 = schematic/graphical abstract, made separately). Each figure is saved as
PDF/PNG/TIFF plus a CSV of the plotted values (table view)."""
import sys, glob, os, warnings; sys.path.insert(0, '.'); warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter
PLAIN = FuncFormatter(lambda v, _: f'{v:g}')


def plain_log(ax, axis='both'):
    for a in ([ax.xaxis, ax.yaxis] if axis == 'both' else [getattr(ax, axis + 'axis')]):
        a.set_major_locator(LogLocator(base=10, subs=(1, 2, 5)))
        a.set_major_formatter(PLAIN); a.set_minor_formatter(NullFormatter())
from src.visualization.style import figure, save, series_style, INK, apply_style, WIDTH, MM, SURFACE
FIG = '../manuscript/figures'; os.makedirs(FIG, exist_ok=True)
rms = lambda s: float(np.sqrt(np.nanmean(np.asarray(s, float) ** 2)))
T = pd.read_csv('../results/summary_v2/per_target.csv')
FAMC = {'mango': 0, 'soil': 2, 'corn': 3}


def panel_letter(ax, s):
    ax.text(-0.2, 1.04, s, transform=ax.transAxes, fontweight='bold', fontsize=9, va='bottom')


# ---------------- Fig 2: label-free unit-risk prediction vs realised RMSEP (master PLS)
apply_style()
fig, axs = plt.subplots(1, 3, figsize=(WIDTH['double'], 66 * MM))
tab = []
specs = [('a', 'Mango, random split', T[(T.grouped == 'none') & (T.family == 'mango')], False, ['mango']),
         ('b', 'Mango, population-grouped split', T[(T.grouped == 'population') & (T.family == 'mango')], False, ['mango']),
         ('c', 'Soil and corn (relative to master CV)', T[(T.grouped == 'none') & T.family.isin(['soil', 'corn'])], True, ['soil', 'corn'])]
for lab, title, d, rel, fams in specs:
    ax = axs['abc'.index(lab)]
    lo, hi = np.inf, 0
    for fam in fams:
        dd = d[d.family == fam]
        x, y = dd['predK|PLS-master'], dd['rmseP|PLS-master']
        if rel:
            x, y = x / dd.rmse_master_cv, y / dd.rmse_master_cv
        ok = x.notna() & y.notna()
        if not ok.any():
            continue
        st = series_style(FAMC[fam])
        ax.scatter(x[ok], y[ok], s=14, color=st['color'], marker=st['marker'], edgecolor=SURFACE, linewidth=0.5,
                   label={'mango': 'Mango', 'soil': 'Soil (6 properties)', 'corn': 'Corn'}[fam] + f' (n={ok.sum()})', zorder=3)
        lo, hi = min(lo, x[ok].min(), y[ok].min()), max(hi, x[ok].max(), y[ok].max())
        tab.append(pd.DataFrame({'panel': lab, 'family': fam, 'dataset': dd.dataset[ok], 'target': dd.target[ok], 'predicted': x[ok], 'realised': y[ok]}))
    ax.set_xscale('log'); ax.set_yscale('log')
    lim = [lo / 1.15, hi * 1.15]
    ax.plot(lim, lim, color=INK['muted'], lw=0.8, ls='--', zorder=1)
    ax.set_xlim(lim); ax.set_ylim(lim); plain_log(ax)
    u = ' / master CV RMSE' if rel else ' (%DM)'
    ax.set_xlabel('Predicted RMSEP' + u); ax.set_ylabel('Realised RMSEP' + u)
    ax.set_title(title, loc='left', fontsize=7)
    panel_letter(ax, lab)
    ax.legend(loc='upper left', fontsize=6)
fig.tight_layout()
save(fig, f'{FIG}/fig2_unit_risk', pd.concat(tab))

# ---------------- Fig 3: methods, RMSEP relative to master PLS per PHYSICAL unit (paired test)
meths = [('FR-LV', 'FR-LV'), ('FR-PLS', 'FR-PLS'), ('EPO-default', 'EPO (k = 2)'), ('GLSW-default', 'GLSW (α = 0.01)'),
         ('EPO-FR', 'EPO (fleet-risk tuned)'), ('GLSW-FR', 'GLSW (fleet-risk tuned)'),
         ('PLS-pooled (labelled)', 'Pooled PLS †'), ('EPO-oracle', 'EPO, oracle k ‡'), ('GLSW-oracle', 'GLSW, oracle α ‡'),
         ('Tikhonov-oracle', 'Tikhonov, oracle τ² ‡'), ('PLS-master+LFBC', 'Master PLS + LFBC §'), ('FR-PLS+LFBC', 'FR-PLS + LFBC §')]
P = T[T.grouped == 'none']
fams = ['mango', 'soil', 'corn']
apply_style()
fig, axs = plt.subplots(1, 3, figsize=(WIDTH['double'], 82 * MM), sharey=True)
tab = []
for ax, fam, lab in zip(axs, fams, 'abc'):
    d = P[P.family == fam]
    for j, (m, name) in enumerate(meths):
        c = f'rmseP|{m}'
        if c not in d:
            continue
        x = d[['target', c, 'rmseP|PLS-master']].dropna()
        if not len(x):
            continue
        lr = np.log(x[c] / x['rmseP|PLS-master'])
        r = np.exp(lr.groupby(x.target).mean()) if fam != 'corn' else np.exp(lr)
        y = len(meths) - 1 - j
        q = np.quantile(r, [0.25, 0.5, 0.75])
        ref = m.endswith(('oracle', '(labelled)'))
        col = INK['muted'] if ref else series_style(1 if m.startswith('FR') else 0)['color']
        ax.scatter(r, np.full(len(r), y) + np.random.default_rng(j).uniform(-0.18, 0.18, len(r)), s=6, color=col, alpha=0.55, lw=0, zorder=2)
        ax.plot([q[0], q[2]], [y, y], color=INK['primary'], lw=1.6, zorder=3, solid_capstyle='round')
        ax.scatter([q[1]], [y], s=26, color=INK['primary'], zorder=4, marker='|', linewidths=1.6)
        tab.append({'family': fam, 'method': name, 'n_units': len(r), 'q25': q[0], 'median': q[1], 'q75': q[2]})
    ax.axvline(1, color=INK['muted'], lw=0.8, ls='--')
    ax.set_xscale('log'); plain_log(ax, 'x')
    if fam == 'soil':
        ax.set_xticks([0.7, 0.8, 0.9, 1, 1.2, 1.5]); ax.xaxis.set_major_formatter(PLAIN)
    ax.set_title({'mango': 'Mango (25 units)', 'soil': 'Soil (6 units)', 'corn': 'Corn (8 instrument × property)'}[fam], loc='left', fontsize=7)
    ax.set_xlabel('RMSEP / RMSEP of master PLS')
    panel_letter(ax, lab)
axs[0].set_yticks(range(len(meths))); axs[0].set_yticklabels([n for _, n in meths][::-1])
for ax in axs: ax.grid(axis='y', visible=False)
fig.text(0.01, 0.005, '† uses reference values of all transfer items on fleet units;  ‡ parameter chosen on the target unit\'s own reference values;  § uses the target unit\'s paired items (no reference values)', fontsize=5.8, color=INK['secondary'])
fig.tight_layout(rect=(0, 0.035, 1, 1))
save(fig, f'{FIG}/fig3_methods', pd.DataFrame(tab))

# ---------------- Fig 4: design curves (mango)
cur = pd.concat([pd.read_csv(f) for f in glob.glob('../results/e4_v2/mango*_curves.csv')])
tm = pd.concat([pd.read_csv(f) for f in glob.glob('../results/e4_v2/mango*_targetm.csv')])
apply_style()
fig, axs = plt.subplots(1, 2, figsize=(WIDTH['double'], 70 * MM))
ax = axs[0]
c = cur[cur.curve == 'N'].groupby(['tag', 'target', 'n_units']).mean(numeric_only=True).reset_index()
c['nb'] = np.where(c.value == 99, 'all', c.value.astype(int).astype(str))
order = ['1', '2', '4', '8', 'all']
agg = c.groupby('nb').agg(real=('rmseP_FRPLS', rms), pred=('predF_FRPLS', rms), master=('rmseP_master', rms)).reindex(order)
xs = np.arange(len(order))
for i, (col, lab) in enumerate([('real', 'FR-PLS, realised'), ('pred', 'FR-PLS, predicted (label-free)'), ('master', 'Master PLS, realised')]):
    st = series_style([1, 0, 4][i])
    ax.plot(xs, agg[col], color=st['color'], marker=st['marker'], label=lab, ls='-' if i != 1 else '--')
ax.set_xticks(xs); ax.set_xticklabels(['1', '2', '4', '8', 'all\n(≤ 22)'])
ax.set_xlabel('Fleet units contributing paired spectra, N'); ax.set_ylabel('RMSEP on unseen units (%DM)')
ax.set_ylim(0, None); ax.legend(loc='upper right'); panel_letter(ax, 'a')
tabA = agg.reset_index()
ax = axs[1]
t = tm.groupby(['tag', 'target', 'model', 'm_target']).mean(numeric_only=True).reset_index()
tabB = []
for i, (mod, nm) in enumerate([('PLS-master', 'Master PLS'), ('FR-PLS', 'FR-PLS')]):
    a = t[t.model == mod].groupby('m_target').agg(raw=('rmseP', rms), lfbc=('rmseP_LFBC', rms), pred=('predK_LFBC', rms))
    st = series_style([4, 1][i])
    ax.plot(a.index, a.lfbc, color=st['color'], marker=st['marker'], label=f'{nm} + LFBC, realised')
    ax.plot(a.index, a.pred, color=st['color'], ls='--', lw=1.0, label=f'{nm} + LFBC, predicted')
    ax.axhline(a.raw.iloc[0], color=st['color'], lw=0.8, ls=':', zorder=1)
    ax.text(a.index.max(), a.raw.iloc[0], f'{nm}, no correction', ha='right', va='bottom', fontsize=6, color=INK['secondary'])
    tabB.append(a.assign(model=mod).reset_index())
ax.set_xscale('log'); ax.set_xticks([1, 2, 3, 5, 10, 20]); ax.set_xticklabels(['1', '2', '3', '5', '10', '20'])
ax.set_xlabel('Items scanned on new unit and master, m'); ax.set_ylabel('RMSEP on new unit (%DM)')
ax.set_ylim(0, None); ax.legend(loc='lower center', ncol=2, fontsize=6); panel_letter(ax, 'b')
fig.tight_layout()
save(fig, f'{FIG}/fig4_design_curves', pd.concat([tabA.assign(panel='a'), pd.concat(tabB).assign(panel='b')]))

# ---------------- Fig 5: physical decomposition of unit effects (offset-free shape)
e7 = pd.read_csv('../results/e7/unit_effect_decomposition.csv')
e7['family'] = np.where(e7.dataset.str.startswith('mango'), 'Mango, Si-PDA units', 'Soil, MEMS FT-NIR units')
apply_style()
fig, ax = plt.subplots(figsize=(WIDTH['single'], 62 * MM))
for i, (f, d) in enumerate(e7.groupby('family')):
    st = series_style([0, 2][i])
    ax.scatter(d.rel_diff, d.R2_shape, s=16, color=st['color'], marker=st['marker'], edgecolor=SURFACE, lw=0.5, label=f'{f} (n={len(d)})')
ax.set_xscale('log'); plain_log(ax, 'x'); ax.set_ylim(0, 1.02)
ax.set_xlabel('Size of mean unit difference\n(RMS / SD of master mean spectrum)'); ax.set_ylabel('Offset-free difference explained\nby gain + shift + bandwidth (R²)')
ax.legend(loc='lower left', fontsize=6)
save(fig, f'{FIG}/fig5_unit_effects', e7)
print('figures written')
