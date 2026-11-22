"""Fig. 1 / graphical abstract: fleet-calibration workflow schematic."""
import sys; sys.path.insert(0, '.')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from src.visualization.style import apply_style, WIDTH, MM, INK, SERIES, save
apply_style(7)
fig, ax = plt.subplots(figsize=(WIDTH['double'], 78 * MM))
ax.set_xlim(0, 190); ax.set_ylim(0, 78); ax.axis('off')
BG = {'data': '#eef4fc', 'calc': '#fdf0ea', 'out': '#e9f7f1'}


def box(x, y, w, h, title, body, kind):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.4,rounding_size=2', fc=BG[kind], ec=INK['muted'], lw=0.6))
    ax.text(x + w / 2, y + h - 3.2, title, ha='center', va='top', fontsize=7.2, fontweight='bold', color=INK['primary'])
    ax.text(x + w / 2, y + h - 8.6, body, ha='center', va='top', fontsize=6.1, color=INK['secondary'], linespacing=1.35)


def arrow(x0, y0, x1, y1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle='-|>', mutation_scale=8, lw=0.9, color=INK['secondary']))


box(2, 44, 52, 30, 'Master unit (labelled)', 'calibration spectra X₀ + lab\nreference values y\n→ PLS, cross-validated MSE₀\n→ replicate covariance Σ₀', 'data')
box(2, 6, 52, 32, 'Fleet units (no lab analysis)', 'a few items scanned on the\nmaster and on N other units\n→ paired differences\n  d = x(unit k) − x̄(master)', 'data')
box(70, 44, 54, 30, 'Fleet risk  (Eq. 5)', 'R̂(b) = MSE₀ + mean (bᵀd)²\n          − (1+1/r₀) bᵀΣ₀b\nfrom the identity e(k) = ē₀ + bᵀd\nunits = random population', 'calc')
box(70, 6, 54, 32, 'FR-PLS  (Eq. 6)', 'PLS on [X₀ ; √w D] → [y ; 0]\nweight w = n/(N·M(k)) follows\nfrom the risk (not tuned)\nLVs by unit-held-out risk', 'calc')
box(140, 52, 48, 22, 'Before release', 'expected RMSEP on units\nnever seen (label-free)', 'out')
box(140, 27, 48, 21, 'Fleet-robust calibration', 'error on unseen units −36 %\n(median, 25 mango units)', 'out')
box(140, 2, 48, 21, 'New unit arrives', 'scan 5 items: predict its RMSEP\n→ accept / bias-correct / reject', 'out')
arrow(55, 59, 69, 59); arrow(55, 22, 69, 22); arrow(55, 30, 69, 52); arrow(55, 52, 69, 30)
arrow(125, 63, 139, 63); arrow(125, 22, 139, 37); arrow(125, 52, 139, 14)
save(fig, '../manuscript/figures/fig1_workflow')
print('ok')
