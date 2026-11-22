**Table 1.** Error of the calibration strategies on unseen units (leave-one-unit-out). Mango: RMS of RMSEP (%DM) over target-unit/season cases on paired test fruit (62 cases, 25 physical units) and on all test fruit (89 cases, 30 units). Soil: median over 36 unit × property cases of RMSEP relative to the master PLS. Corn: RMS of RMSEP over 8 instrument × property cases (property units). Last column: median per-physical-unit RMSEP ratio of FR-PLS (or FR-PLS + LFBC for LFBC rows) to the method in the row, with 90 % bootstrap CI; * Holm-adjusted Wilcoxon p < 0.05.

| Group | Method | Mango, paired | Mango, all test | Soil (rel.) | Corn | FR-PLS / method |
|---|---|---|---|---|---|---|
| Target-label-free | Master PLS | 2.39 | 2.34 | 1.00 | 1.35 | 0.64 (0.59–0.70)* |
|  | FR-LV (proposed) | 1.82 | 2.21 | 1.00 | 0.48 | 0.79 (0.67–0.85)* |
|  | FR-PLS (proposed) | 1.41 | 1.91 | 0.95 | 0.38 | — |
|  | EPO, k = 2 | 2.25 | 2.30 | 1.03 | 0.44 | 0.65 (0.59–0.71)* |
|  | GLSW, α = 0.01 | 2.28 | 2.22 | 0.98 | 0.42 | 0.68 (0.60–0.69)* |
|  | EPO, k by fleet risk | 1.56 | 1.89 | 1.00 |  | 0.86 (0.82–0.94)* |
|  | GLSW, α by fleet risk | 1.51 | 2.19 | 0.98 |  | 0.94 (0.89–0.99)* |
| Uses fleet reference values | Pooled PLS | 1.34 | 1.75 | 0.92 | 0.36 | 1.08 (0.98–1.17) |
| Oracle (target reference values) | EPO, oracle k | 1.01 | 1.26 | 0.99 | 0.28 | 1.23 (1.17–1.30)* |
|  | GLSW, oracle α | 1.09 | 1.33 | 0.94 | 0.30 | 1.19 (1.15–1.21)* |
|  | Tikhonov, oracle τ² | 1.10 | 1.26 | 0.94 | 0.27 | 1.18 (1.13–1.24)* |
| With LFBC (target paired items) | Master PLS + LFBC | 1.15 | 1.37 | 0.98 | 0.26 | 0.90 (0.87–0.91)* |
|  | FR-PLS + LFBC | 0.98 | 1.07 | 0.92 | 0.24 | — |
|  | GLSW (fleet risk) + LFBC | 1.04 | 1.12 | 0.94 |  | 0.96 (0.94–0.97)* |
|  | Master PLS + PDS | 1.05 | 1.44 | 0.97 | 0.25 | 0.98 (0.91–0.99)* |
|  | FR-PLS + PDS | 1.05 | 1.21 | 0.93 | 0.25 | 0.96 (0.94–1.01)* |
| Target reference values | Master PLS + slope/bias (labelled) | 1.01 | 1.21 | 0.96 | 0.25 | 0.97 (0.91–0.99) |
|  | FR-PLS + slope/bias (labelled) | 0.87 | 1.00 | 0.92 | 0.25 | 1.11 (1.06–1.13)* |
| Fleet reference values | Pooled PLS + LFBC | 0.94 | 1.02 | 0.92 | 0.23 | 1.01 (1.00–1.03) |
