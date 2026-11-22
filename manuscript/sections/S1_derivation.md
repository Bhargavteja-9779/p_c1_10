# Supplementary material

**Fleet calibration of handheld near-infrared spectrometers: label-free prediction and minimisation of the error on instrument units never seen in calibration**

P N Bhargav Teja, [Second Author]

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

**Table S1.** Evaluation of the target-label-free qualification rule on the mango fleet (seasons 2016–2018, 33 target units, 10 random draws of m paired fruit per unit). A unit deployment is fit for use if its realised RMSEP ≤ Spec × the master PLS cross-validated RMSE.

| Model | m | Spec | Unfit without rule (%) | Correct accept decisions (%) | False accept (%) | False reject (%) | Accepted (%) | Bias-corrected (%) | Rejected (%) | Deployed out of spec (%) |
|---|---|---|---|---|---|---|---|---|---|---|
| FR-PLS | 1 | 1.25 | 54.5 | 75.2 | 23.7 | 26.2 | 46.5 | 46.6 | 7.0 | 30.8 |
| FR-PLS | 1 | 1.50 | 40.4 | 79.0 | 31.5 | 13.9 | 64.0 | 35.7 | 0.3 | 18.0 |
| FR-PLS | 1 | 2.00 | 15.2 | 90.6 | 32.7 | 5.2 | 85.4 | 14.6 | 0.0 | 5.4 |
| FR-PLS | 3 | 1.25 | 54.5 | 79.9 | 15.2 | 26.0 | 41.9 | 47.9 | 10.2 | 22.8 |
| FR-PLS | 3 | 1.50 | 40.4 | 86.5 | 24.5 | 6.1 | 65.9 | 31.9 | 2.2 | 11.2 |
| FR-PLS | 3 | 2.00 | 15.2 | 92.7 | 30.0 | 3.2 | 86.7 | 12.9 | 0.4 | 4.6 |
| FR-PLS | 5 | 1.25 | 54.5 | 78.9 | 15.0 | 28.4 | 40.7 | 49.2 | 10.1 | 19.7 |
| FR-PLS | 5 | 1.50 | 40.4 | 88.2 | 21.2 | 5.4 | 64.9 | 33.3 | 1.7 | 9.8 |
| FR-PLS | 5 | 2.00 | 15.2 | 94.0 | 25.3 | 2.5 | 86.6 | 13.3 | 0.1 | 3.8 |
| FR-PLS | 10 | 1.25 | 54.5 | 81.6 | 12.8 | 25.1 | 41.0 | 51.5 | 7.5 | 17.4 |
| FR-PLS | 10 | 1.50 | 40.4 | 90.9 | 17.5 | 3.4 | 64.6 | 34.3 | 1.0 | 7.8 |
| FR-PLS | 10 | 2.00 | 15.2 | 93.9 | 24.0 | 2.9 | 86.1 | 13.9 | 0.0 | 3.6 |
| FR-PLS | 20 | 1.25 | 53.1 | 83.2 | 10.4 | 24.0 | 41.1 | 51.1 | 7.7 | 15.9 |
| FR-PLS | 20 | 1.50 | 39.6 | 92.6 | 15.3 | 2.2 | 65.1 | 33.1 | 1.8 | 6.2 |
| FR-PLS | 20 | 2.00 | 15.6 | 94.3 | 16.0 | 3.8 | 83.6 | 16.4 | 0.0 | 2.5 |
| PLS-master | 1 | 1.25 | 81.8 | 79.8 | 18.8 | 26.7 | 28.7 | 13.6 | 57.7 | 44.4 |
| PLS-master | 1 | 1.50 | 65.7 | 82.3 | 18.8 | 15.6 | 41.3 | 35.7 | 23.0 | 27.3 |
| PLS-master | 1 | 2.00 | 41.4 | 83.0 | 21.5 | 13.8 | 59.4 | 40.6 | 0.0 | 13.2 |
| PLS-master | 3 | 1.25 | 81.8 | 87.6 | 10.9 | 19.4 | 23.5 | 46.1 | 30.4 | 32.7 |
| PLS-master | 3 | 1.50 | 65.7 | 89.6 | 9.2 | 12.6 | 36.1 | 52.0 | 11.9 | 15.8 |
| PLS-master | 3 | 2.00 | 41.4 | 89.4 | 14.9 | 7.6 | 60.3 | 36.9 | 2.8 | 8.2 |
| PLS-master | 5 | 1.25 | 81.8 | 88.4 | 10.0 | 18.9 | 22.9 | 47.6 | 29.5 | 29.7 |
| PLS-master | 5 | 1.50 | 65.7 | 90.0 | 8.9 | 12.1 | 36.1 | 51.8 | 12.1 | 12.8 |
| PLS-master | 5 | 2.00 | 41.4 | 90.4 | 12.7 | 7.4 | 59.5 | 38.5 | 2.0 | 6.4 |
| PLS-master | 10 | 1.25 | 81.8 | 88.8 | 8.8 | 22.2 | 21.3 | 50.9 | 27.8 | 25.2 |
| PLS-master | 10 | 1.50 | 65.7 | 91.0 | 6.6 | 13.5 | 34.0 | 55.6 | 10.4 | 10.3 |
| PLS-master | 10 | 2.00 | 41.4 | 93.9 | 6.8 | 5.5 | 58.2 | 40.6 | 1.2 | 3.7 |
| PLS-master | 20 | 1.25 | 81.2 | 90.4 | 7.2 | 20.0 | 20.8 | 50.6 | 28.5 | 21.1 |
| PLS-master | 20 | 1.50 | 65.6 | 92.2 | 5.7 | 11.8 | 34.1 | 53.9 | 12.1 | 7.8 |
| PLS-master | 20 | 2.00 | 42.7 | 95.4 | 6.6 | 3.1 | 58.3 | 40.8 | 0.8 | 3.7 |

## S4. Simulation study

Fleets were simulated with 260 items whose master spectra are linear mixtures of six latent profiles (60 channels; reference value a linear function of two latent scores plus noise, SD 0.15). Each of 93 units added a random additive effect (fleet mean offset plus a random combination of three unit-effect profiles), a random gain (SD 3 %) and scan noise (two scans per item and unit). Unit 0 was the master (120 calibration items), units 1–N formed the fleet (paired transfer items: m of 60), and 60 further units were unseen; realised errors were measured on 80 test items on the unseen units. Thirty independent fleets were simulated. Table S2 gives the median ratio of predicted to realised fleet RMSEP.

**Table S2.** Median ratio predicted/realised fleet RMSEP on 60 unseen simulated units (30 simulated fleets).

| Fleet units N | Paired items m | Master PLS | FR-PLS |
|---|---|---|---|
| 1 | 5 | 1.036 | 0.968 |
| 1 | 20 | 1.036 | 0.963 |
| 1 | 60 | 1.029 | 0.958 |
| 2 | 5 | 1.025 | 0.989 |
| 2 | 20 | 1.023 | 0.998 |
| 2 | 60 | 1.022 | 1.005 |
| 4 | 5 | 1.013 | 1.002 |
| 4 | 20 | 1.011 | 1.006 |
| 4 | 60 | 1.006 | 1.017 |
| 8 | 5 | 1.037 | 1.018 |
| 8 | 20 | 1.040 | 1.021 |
| 8 | 60 | 1.036 | 1.023 |
| 16 | 5 | 1.035 | 1.020 |
| 16 | 20 | 1.038 | 1.020 |
| 16 | 60 | 1.038 | 1.021 |
| 32 | 5 | 1.037 | 1.020 |
| 32 | 20 | 1.042 | 1.020 |
| 32 | 60 | 1.041 | 1.021 |
