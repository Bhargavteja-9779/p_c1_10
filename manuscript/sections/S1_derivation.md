# Supplementary material

## S1. Derivation of Eq. (4)

Let item $i$ be scanned $r_0$ times on the master, $\mathbf{x}_{i0}^{(r)} = \mathbf{s}_i + \boldsymbol{\varepsilon}_{i0}^{(r)}$, and once on unit $k$, $\mathbf{x}_{ik} = \mathbf{s}_i + \mathbf{a}_{ik} + \boldsymbol{\varepsilon}_{ik}$, with zero-mean scan noise independent across scans, items and units, $\mathrm{cov}(\boldsymbol{\varepsilon}_{i0}) = \boldsymbol{\Sigma}_0$, $\mathrm{cov}(\boldsymbol{\varepsilon}_{ik}) = \boldsymbol{\Sigma}_k$. Define $c_i = b_0 + \mathbf{b}^\top\mathbf{s}_i - y_i$ (the master's noise-free error). Then

- master single-scan error $e_{i0} = c_i + \mathbf{b}^\top\boldsymbol{\varepsilon}_{i0}$, so $\mathrm{MSE}_0 = \mathbb{E}[c_i^2] + \mathbf{b}^\top\boldsymbol{\Sigma}_0\mathbf{b}$;
- unit-$k$ error $e_{ik} = c_i + \mathbf{b}^\top\mathbf{a}_{ik} + \mathbf{b}^\top\boldsymbol{\varepsilon}_{ik}$, so $\mathbb{E}[e_{ik}^2] = \mathbb{E}[c_i^2] + \mathbb{E}[(\mathbf{b}^\top\mathbf{a}_{ik})^2] + \mathbf{b}^\top\boldsymbol{\Sigma}_k\mathbf{b} + 2\mathbb{E}[c_i\,\mathbf{b}^\top\mathbf{a}_{ik}]$;
- paired difference $\mathbf{d}_{ik} = \mathbf{a}_{ik} + \boldsymbol{\varepsilon}_{ik} - \bar{\boldsymbol{\varepsilon}}_{i0}$, so $\mathbb{E}[(\mathbf{b}^\top\mathbf{d}_{ik})^2] = \mathbb{E}[(\mathbf{b}^\top\mathbf{a}_{ik})^2] + \mathbf{b}^\top\boldsymbol{\Sigma}_k\mathbf{b} + \mathbf{b}^\top\boldsymbol{\Sigma}_0\mathbf{b}/r_0$.

Eliminating $\mathbb{E}[c_i^2]$ and $\mathbb{E}[(\mathbf{b}^\top\mathbf{a}_{ik})^2] + \mathbf{b}^\top\boldsymbol{\Sigma}_k\mathbf{b}$ gives

$$\mathbb{E}[e_{ik}^2] = \mathrm{MSE}_0 + \mathbb{E}[(\mathbf{b}^\top\mathbf{d}_{ik})^2] - \Big(1 + \tfrac{1}{r_0}\Big)\mathbf{b}^\top\boldsymbol{\Sigma}_0\mathbf{b} + 2\,\mathbb{E}[c_i\,\mathbf{b}^\top\mathbf{a}_{ik}],$$

which is Eq. (4). Note that the unit's own noise covariance $\boldsymbol{\Sigma}_k$ is *not* needed: it enters the deployment error and the paired difference identically. With unequal numbers of master scans per item, $1/r_0$ is replaced by the mean of $1/r_{0i}$ over the paired items. When the fleet risk is averaged over units, each unit receives equal weight because the population of interest is the population of units. The estimator is unbiased for the unit risk when the cross-term vanishes; its sampling variance is that of a mean of $M_k$ squared projections and is reduced by averaging over items and units, which is why five items suffice for most units (Fig. 4b).

## S2. Unit-held-out cross-validation for FR-PLS

The master calibration items are split into 5 grouped folds. When the fleet has three or more units, the units are randomly assigned to min(5, N) groups and fold $f$ holds out unit group $f$; with fewer than three units, the paired items (not units) are assigned to folds. In fold $f$, Eq. (6) is solved without master fold $f$ and without the held-out difference rows; $\mathrm{MSE}_0(a)$ is accumulated on master fold $f$ and the quadratic term on the held-out difference rows, for every number of latent variables $a$. The selected $a$ minimises the resulting estimate of Eq. (5), and the final model is refitted on all data. This guarantees that no paired difference is used both to fit a model and to estimate that model's fleet risk.
