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

## S3. Supplementary Table S1

**Table S1.** Evaluation of the target-label-free qualification rule on the mango fleet (seasons 2016–2018, 33 target units, 10 random draws of m paired fruit per unit). A unit deployment is fit for use if its realised RMSEP ≤ Spec × master cross-validated RMSE.

| Model | m | Spec | Unfit without rule (%) | Correct accept decisions (%) | False accept (%) | False reject (%) | Accepted (%) | Bias-corrected (%) | Rejected (%) | Deployed out of spec (%) |
|---|---|---|---|---|---|---|---|---|---|---|
| FR-PLS | 1 | 1.2 | 57.6 | 76.3 | 23.0 | 24.8 | 45.2 | 54.5 | 0.3 | 32.2 |
| FR-PLS | 1 | 1.5 | 39.4 | 79.2 | 29.2 | 15.3 | 62.8 | 37.2 | 0.0 | 16.5 |
| FR-PLS | 1 | 2.0 | 16.2 | 90.9 | 28.8 | 5.3 | 84.0 | 16.0 | 0.0 | 5.1 |
| FR-PLS | 3 | 1.2 | 57.6 | 78.8 | 15.8 | 28.6 | 39.4 | 56.2 | 4.4 | 24.4 |
| FR-PLS | 3 | 1.5 | 39.4 | 84.7 | 22.8 | 10.3 | 63.3 | 35.4 | 1.3 | 10.3 |
| FR-PLS | 3 | 2.0 | 16.2 | 93.9 | 20.6 | 3.3 | 84.4 | 15.3 | 0.3 | 3.4 |
| FR-PLS | 5 | 1.2 | 57.6 | 79.9 | 15.3 | 26.7 | 39.9 | 53.8 | 6.3 | 22.0 |
| FR-PLS | 5 | 1.5 | 39.4 | 87.3 | 19.7 | 8.2 | 63.4 | 35.8 | 0.8 | 9.1 |
| FR-PLS | 5 | 2.0 | 16.2 | 94.4 | 16.2 | 3.5 | 83.5 | 16.5 | 0.0 | 2.6 |
| FR-PLS | 10 | 1.2 | 57.6 | 80.4 | 15.3 | 25.5 | 40.4 | 54.5 | 5.1 | 20.1 |
| FR-PLS | 10 | 1.5 | 39.4 | 90.5 | 15.9 | 5.3 | 63.6 | 35.8 | 0.6 | 6.8 |
| FR-PLS | 10 | 2.0 | 16.2 | 95.8 | 12.5 | 2.7 | 83.6 | 16.4 | 0.0 | 2.0 |
| FR-PLS | 20 | 1.2 | 56.2 | 81.0 | 13.5 | 26.0 | 40.0 | 54.2 | 5.8 | 18.4 |
| FR-PLS | 20 | 1.5 | 38.5 | 92.0 | 14.1 | 4.2 | 64.3 | 34.4 | 1.4 | 5.5 |
| FR-PLS | 20 | 2.0 | 16.7 | 95.6 | 8.1 | 3.6 | 81.7 | 18.3 | 0.0 | 1.4 |
| PLS-master | 1 | 1.2 | 81.8 | 79.8 | 18.8 | 26.7 | 28.7 | 44.1 | 27.2 | 47.7 |
| PLS-master | 1 | 1.5 | 65.7 | 82.3 | 18.8 | 15.6 | 41.3 | 58.2 | 0.5 | 30.3 |
| PLS-master | 1 | 2.0 | 41.4 | 83.0 | 21.5 | 13.8 | 59.4 | 40.6 | 0.0 | 13.2 |
| PLS-master | 3 | 1.2 | 81.8 | 87.6 | 10.9 | 19.4 | 23.5 | 54.2 | 22.2 | 35.1 |
| PLS-master | 3 | 1.5 | 65.7 | 89.6 | 9.2 | 12.6 | 36.1 | 56.4 | 7.6 | 16.6 |
| PLS-master | 3 | 2.0 | 41.4 | 89.4 | 14.9 | 7.6 | 60.3 | 38.8 | 0.9 | 8.4 |
| PLS-master | 5 | 1.2 | 81.8 | 88.4 | 10.0 | 18.9 | 22.9 | 53.3 | 23.7 | 32.2 |
| PLS-master | 5 | 1.5 | 65.7 | 90.0 | 8.9 | 12.1 | 36.1 | 55.2 | 8.8 | 14.1 |
| PLS-master | 5 | 2.0 | 41.4 | 90.4 | 12.7 | 7.4 | 59.5 | 39.2 | 1.3 | 6.4 |
| PLS-master | 10 | 1.2 | 81.8 | 88.8 | 8.8 | 22.2 | 21.3 | 55.1 | 23.6 | 26.1 |
| PLS-master | 10 | 1.5 | 65.7 | 91.0 | 6.6 | 13.5 | 34.0 | 56.9 | 9.1 | 11.0 |
| PLS-master | 10 | 2.0 | 41.4 | 93.9 | 6.8 | 5.5 | 58.2 | 40.8 | 1.0 | 3.6 |
| PLS-master | 20 | 1.2 | 81.2 | 90.4 | 7.2 | 20.0 | 20.8 | 53.2 | 25.9 | 22.1 |
| PLS-master | 20 | 1.5 | 65.6 | 92.2 | 5.7 | 11.8 | 34.1 | 55.2 | 10.7 | 8.4 |
| PLS-master | 20 | 2.0 | 42.7 | 95.4 | 6.6 | 3.1 | 58.3 | 41.1 | 0.5 | 3.8 |
