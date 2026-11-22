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
T = pd.read_csv('../results/e1e2/summary/per_target.csv')
FAM = {'mango': ('Mango DM, 31 units (%)', 0), 'neospectra': ('Soil, 7 units (property units)', 1), 'corn': ('Corn, 3 instruments', 2)}


def panel_letter(ax, s):
    ax.text(-0.18, 1.04, s, transform=ax.transAxes, fontweight='bold', fontsize=9, va='bottom')


# ---------------- Fig 2: label-free unit-risk prediction vs realised RMSEP (paired test)
apply_style()
fig, axs = plt.subplots(1, 2, figsize=(WIDTH['double'], 80 * MM))
tab = []
for ax, mod, lab in zip(axs, ['PLS-master', 'FR-PLS'], ['a', 'b']):
    lo, hi = np.inf, 0
    for fam, (name, i) in FAM.items():
        d = T[T.family == fam]
        x, y = d[f'predK|{mod}'], d[f'rmseP|{mod}']
        ok = x.notna() & y.notna()
        if not ok.any():
            continue
        st = series_style(i)
        ax.scatter(x[ok], y[ok], s=16, color=st['color'], marker=st['marker'], edgecolor=SURFACE, linewidth=0.5,
                   label=name.split(',')[0] + f' (n={ok.sum()})', zorder=3)
        lo, hi = min(lo, x[ok].min(), y[ok].min()), max(hi, x[ok].max(), y[ok].max())
        tab.append(pd.DataFrame({'model': mod, 'family': fam, 'dataset': d.dataset[ok], 'target': d.target[ok],
                                 'predicted_rmsep': x[ok], 'realised_rmsep': y[ok]}))
    ax.set_xscale('log'); ax.set_yscale('log')
    lim = [lo / 1.2, hi * 1.2]
    ax.plot(lim, lim, color=INK['muted'], lw=0.8, ls='--', zorder=1)
    ax.set_xlim(lim); ax.set_ylim(lim); plain_log(ax)
    ax.set_xlabel('Predicted RMSEP on unit (label-free)'); ax.set_ylabel('Realised RMSEP on unit')
    ax.set_title({'PLS-master': 'Master PLS', 'FR-PLS': 'FR-PLS'}[mod], loc='left')
    panel_letter(ax, lab)
    ax.legend(loc='upper left')
fig.tight_layout()
save(fig, f'{FIG}/fig2_unit_risk', pd.concat(tab))

# ---------------- Fig 3: methods, RMSEP relative to master PLS per target (paired test)
meths = [('FR-LV', 'FR-LV'), ('FR-PLS', 'FR-PLS'), ('FR-PLS+LFBC', 'FR-PLS + LFBC'), ('EPO-default', 'EPO (k=2)'),
         ('GLSW-default', 'GLSW (α=0.01)'), ('EPO-oracle', 'EPO, oracle k*'), ('GLSW-oracle', 'GLSW, oracle α*'),
         ('Tikhonov-oracle', 'Tikhonov, oracle τ*'), ('PLS-pooled (labelled)', 'Pooled PLS (labelled)*')]
fams = [f for f in FAM if (T.family == f).any()]
apply_style()
fig, axs = plt.subplots(1, len(fams), figsize=(WIDTH['double'], 75 * MM), sharey=True)
axs = np.atleast_1d(axs)
tab = []
for ax, fam, lab in zip(axs, fams, 'abc'):
    d = T[T.family == fam]
    for j, (m, name) in enumerate(meths):
        r = d[f'rmseP|{m}'] / d['rmseP|PLS-master']
        r = r[np.isfinite(r)]
        if not len(r):
            continue
        y = len(meths) - 1 - j
        q = np.quantile(r, [0.25, 0.5, 0.75])
        col = series_style(1 if m.startswith('FR') else 0)['color'] if not m.endswith(('oracle', '(labelled)')) else INK['muted']
        ax.scatter(r, np.full(len(r), y) + np.random.default_rng(j).uniform(-0.18, 0.18, len(r)), s=5, color=col, alpha=0.45, lw=0, zorder=2)
        ax.plot([q[0], q[2]], [y, y], color=INK['primary'], lw=1.6, zorder=3, solid_capstyle='round')
        ax.scatter([q[1]], [y], s=26, color=INK['primary'], zorder=4, marker='|', linewidths=1.6)
        tab.append({'family': fam, 'method': name, 'n_targets': len(r), 'q25': q[0], 'median': q[1], 'q75': q[2]})
    ax.axvline(1, color=INK['muted'], lw=0.8, ls='--')
    ax.set_xscale('log'); plain_log(ax, 'x')
    ax.set_title(FAM[fam][0].split(',')[0], loc='left')
    ax.set_xlabel('RMSEP / RMSEP of master PLS')
    panel_letter(ax, lab)
axs[0].set_yticks(range(len(meths))); axs[0].set_yticklabels([n for _, n in meths][::-1])
axs[0].grid(axis='y', visible=False)
fig.text(0.01, 0.005, '* uses information not available in label-free deployment (target labels or transfer-item reference values)', fontsize=6, color=INK['secondary'])
fig.tight_layout(rect=(0, 0.03, 1, 1))
save(fig, f'{FIG}/fig3_methods', pd.DataFrame(tab))

# ---------------- Fig 4: design curves (mango)
cur = pd.concat([pd.read_csv(f) for f in glob.glob('../results/e4/mango*_curves.csv')])
tm = pd.concat([pd.read_csv(f) for f in glob.glob('../results/e4/mango*_targetm.csv')])
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
