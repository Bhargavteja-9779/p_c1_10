# Review round 2: "Fleet calibration of handheld near-infrared spectrometers" (revised draft for Analytica Chimica Acta)

Material checked: `manuscript/sections/*.md` (00–07, 04b_table1, S1), the five figure PNGs and their CSVs, `results/summary_v2/*` (facts.json, facts_e4.json, per_target.csv, E2_methods.csv, E2_tests_physical_units.csv, E4_targetm.csv, E4_decision.csv), `results/e7/unit_effect_decomposition.csv`, the raw runs in `results/e1e2_v2/` and `results/e4_v2/`, and the code in `code/src/fleet/` (methods.py, risk.py, protocol.py, data.py, builders.py) and `code/scripts/` (run_job.py, analyse_v2.py, analyse_e4.py, run_e4.py). I recomputed every number with Python from the CSVs, and I re-ran `split_items` on the mango data to check the population-grouped split.

**Overall recommendation: minor-to-major revision.** The revision is substantial and mostly in good faith. The numbers in Table 1 and in most of §4 now match the result files exactly. The all-test metric is reported. Inference is done per physical unit with bootstrap CIs and an equivalence criterion. Baselines are tuned label-free, a grouped split was added, the qualification rule is evaluated as a decision, the soil results are in, and the E7 bug is fixed. What remains:
- a small set of number mismatches, mostly in places the authors did not regenerate (Fig. 1, Fig. 4a, §3.3, the corn sentence);
- a residual unfairness in the label-free baselines: LVs are still not tuned for EPO/GLSW;
- a robustness check that does not separate sessions as claimed;
- an incomplete LFBC variance term;
- several claims stronger than the evidence (abstract and conclusion).

---

## 1. Number audit

Legend: ✓ = matches result files (after rounding); ✗ = mismatch.

### 1.1 Mismatches (to be fixed)

| # | Location | Claimed | Correct (source) |
|---|---|---|---|
| 1 | Fig. 1 (graphical abstract and workflow figure) | "error on unseen units −41 % (31 mango units)"; "exact identity"; "fixed by theory (no tuning)" | The text now uses −36 % (median per unit; RMS reduction 2.39→1.41 is −41 % but over 62 unit-seasons / **25** units). "31 units" contradicts the 25/30 used elsewhere. "No tuning" contradicts the LV tuning and the removed highlight. Regenerate the figure. |
| 2 | Fig. 4a x-axis tick | "all (≤ 22)" | Full fleets in E4 have 9–11 units (`e4_v2/*_curves.csv`, value = 99: n_units 9–11). This was flagged in round 1 and is unchanged (`make_figures.py` l.116). |
| 3 | §4.3, last paragraph (corn) | "predicted fleet risk of FR-PLS was optimistic (median ratio **0.55**)" | facts.json `E1fleet\|corn\|FR-PLS.ratio_median` = **0.71**. The ratio of means is 0.62 (0.210/0.337) and the row-wise median is 0.78. No computation gives 0.55. |
| 4 | §4.3, LFBC paragraph | "FR-PLS+LFBC gave the **lowest error of all target-label-free strategies** (RMS 0.98 %DM paired …)" | GLSW-FR+LFBC is lower on paired fruit: **0.966** vs 0.983 (E2_methods; Table 1 itself shows 0.97 vs 0.98). The claim is true only for all test fruit (1.07 vs 1.12). |
| 5 | §3.3 | LFBC used "on average **10–300** items per unit" | `n_pairs_target`: range 0–326. Mean 46, median 36 over 89 targets. **26 of 89** mango targets (29 % of runs) have **0** target transfer items, so LFBC is undefined for them. Among targets with items: 3.8–326, median 45. Round-1 issue, unchanged. |
| 6 | §4.2 | dropped cross-term "**−6 %** of the quadratic term" (master PLS, mango) | `cross_over_quad\|mango\|PLS-master` = −0.066 → **−7 %**. The −6 % figure is the share of the *risk* (−5.7 %). Either relabel it or change the number. |
| 7 | §4.2, fleet level | "median ratio 1.00 **over 310 unit × split cases**" | 310 is the number of rows. `analyse_v2.py` l.51–56 takes the median over the **30 season × seed** fleet-level comparisons (pred mean vs realised RMS). Describe it as such. |
| 8 | §4.4 | Grouped split "three seasons, **26** paired cases" for all eight RMS values | Master, FR-LV, FR-PLS, EPO-FR, GLSW-FR and pooled RMS are over **27** cases (`grouped.n_cases_paired` = 27). Only the LFBC RMS and the unit-risk statistics use 26, because target 18044 (2018) has 0 transfer items. Fig. 2b (n = 26) is correct. |
| 9 | Table S1, "Spec" column | 1.2 / 1.5 / 2.0 | `E4_decision.csv` and §3.5/§4.5 use **1.25**. All 30 rows of Table S1 otherwise match to 0.1 %. |
| 10 | §3.5 / §4.5 / Table S1 caption | "fit if realised RMSEP ≤ Spec × **master's** cross-validated RMSE" | For FR-PLS rows, `run_e4.py` l.59/77 sets `rmse_cv_master` = √(FR-PLS's own CV MSE), so the threshold differs per model. The effect is small (FR-PLS unfit 39.4 % with its own threshold vs 40.4 % with the master threshold), but the text and the code disagree. |
| 11 | Abstract vs Highlights vs Intro vs §3.1 vs Fig. 1 | Abstract: "30 handheld mango … units (six seasons)" with r = 0.98. Highlight 3: "25 units". Intro: "85 401 spectra … **31** units over **seven** seasons". Fig. 1: "31 mango units". | r = 0.98 is computed over **62 unit-seasons from 25 physical units**. 30 is the all-test unit count. The Intro still gives raw-file counts (round-1 B.3), not analysed ones. Harmonise, and state "62 unit-seasons (25 units)" wherever r = 0.98 is quoted. |
| 12 | §4.2 | Range coverage 77 % reported without its nominal level | Not a wrong number, but incomplete. The interval used in the code is [min, max] (`analyse_v2.py` l.55), not the symmetric order-statistic interval of §2.2. Its nominal level for N ≈ 10 is ≈ 0.82. **Soil coverage is 37 % (nominal 67 % for N = 5) and is not reported.** |

### 1.2 Verified claims (✓)

**Abstract / Highlights**
- 36 % median reduction (1 − 0.641) ✓
- r = 0.98 ✓; r = 0.69 grouped ✓
- 267 words including the sub-headings (still above about 250; see §4)
- Highlight lengths 69–83 characters ✓

**§4.1**
- Master CV RMSE 0.59–1.15 ✓; 11.7 LVs ✓
- Paired RMSEP 0.81–6.9 ✓
- 62 cases / 25 units ✓
- 2.39 ✓; ratio 2.7 (2.73) ✓
- LFBC 1.15 ✓
- Offset share 90 % (0.897) ✓; shape R² 91 % ✓; |shift| 1.2 nm (1.17) ✓
- Gain largest unique share (0.34 vs 0.14 / 0.01) ✓
- Soil shape R² 27 % ✓
- Realised/CV ratio: soil 1.07 (n = 36) ✓, mango 2.1 (2.14) ✓

**§4.2**
- r 0.98, ρ 0.96, median ratio 0.99, MdAPE 6.9 % ✓
- Soil: median ratio 1.00 (1.005), MdAPE 4.5 % ✓
- Corn MdAPE < 1 % (0.66 %) ✓
- Soil cross-term −1 % ✓
- Grouped split: r 0.69, MdAPE 13 % (12.8), median ratio 0.98 ✓
- FR-PLS: r 0.86, MdAPE 15 % ✓
- Fleet level: pred 2.42 vs realised 2.40 ✓; coverage 77 % ✓; soil 1.01 ✓
- FR-LV / FR-PLS median ratios 0.86 / 0.88 ✓; coverage 13 % ✓

**§4.3**
- Paired RMS 2.39 / 1.82 / 1.41 ✓; LVs 10.6 vs 11.7 ✓
- Median ratio 0.64 (0.59–0.70) ✓; 92 % of units better ✓; p < 0.001 ✓
- All-test 0.69 (0.64–0.76) ✓; 2.34 → 1.91 ✓
- EPO / GLSW default 2.25 / 2.28 ✓
- EPO-FR 1.52, GLSW-FR 1.49 ✓; ratios 0.86 / 0.93 ✓; Holm p 0.002 / 0.006 ✓
- Pooled 1.08 (0.98–1.17), p = 0.31 ✓
- Oracle ratios 1.18–1.23 ✓
- τ² = 0.3 or 3 in 45 % (138/310) ✓
- GLSW-FR smallest α in 43 % (191/445) ✓
- FR-PLS+LFBC: 92 % of units better, 0.90, p < 0.001 ✓
- Pooled+LFBC 1.01 (1.00–1.03) ✓
- Soil FR-PLS 0.95 ✓
- Corn: 1.35 / 0.48 / 0.38 / 0.36 / 0.27–0.30 ✓; 8/8 cases ✓

**§4.4**
- All 16 RMS values (2.51 … 0.92) ✓

**§4.5**
- Fleet size: 1.61 vs 1.85 ✓; 1.29 / 1.27 ✓; 0.80 ✓; 1.12–1.16 vs 1.27–1.44 ✓
- 3 items: 1.28 vs 1.27 ✓
- LFBC: 1.85 → 1.06 ✓; 1.27 → 0.88 ✓; m = 5: 0.96 / 0.83 ✓; 0.95 vs 0.96 ✓
- Single draw: r 0.95 ✓; MdAPE 11 % ✓
- Decision at m = 5, spec 1.5: 90 % correct, FA 8.9 %, FR 12.1 % ✓; unfit 66 % ✓
- Rule outcomes 36 / 55 / 9 % ✓; deployed out of spec 14 % ✓
- FR-PLS: 39 %, 87 %, 9 % ✓
- Sensitivity: 80–94 % ✓; 82 → 32 % and 41 → 6 % ✓

**Table 1**
- All 57 RMS / relative entries ✓
- All 14 ratio / CI entries and Holm asterisks ✓

**Conclusion**
- 25 units ✓; r 0.98 ✓; 7 % ✓; r 0.69 ✓
- "within 1 %" ✓ (master PLS only, which the sentence implies)
- 36 % ✓; ≈ 12 % ✓; r 0.95 ✓; 90 % ✓; 66 → 14 % ✓

**Captions**
- Fig. 2: n = 62 / 26 / 36 / 8 ✓
- Fig. 3: 25 / 6 / 8 ✓
- Fig. 4: 2016–2018, 33 targets ✓
- Fig. 5: n = 33 / 6 ✓

---

## 2. Status of the round-1 issues

### 2.1 Top-10 list

| # | Issue | Status | Justification |
|---|---|---|---|
| 1 | Number inconsistencies | **PARTIAL** | Table 1 and nearly all of §4 now match the files exactly. Twelve mismatches remain (§1.1), concentrated in Fig. 1, Fig. 4a, §3.3, the corn sentence and the unit/season counts. |
| 2 | Unfair label-free baselines | **PARTIAL** | k and α are now tuned by fleet risk, but the **LV count of EPO-FR/GLSW-FR is still chosen by master CV with the 1-SE rule** (mean 7.5 / 6.5 LVs, vs 17.6 for FR-PLS, which is tuned by fleet risk). Their tuning protocol (2-fold unit halves) also differs from FR-PLS (5 unit groups). Grids still hit the edge: EPO-FR k = 20 in 13 %, GLSW-FR α = 10⁻⁶ in 43 %, EPO-oracle k = 20 in 16 %, GLSW-oracle α = 10⁻⁶ in 28 %. TOP is not included. Tikhonov now excludes τ² = 1 (stated) ✓. |
| 3 | Selective metric | **RESOLVED** | The all-test metric is in Table 1 and the text, with its own tests (n = 30). |
| 4 | Pseudo-replication / equivalence | **PARTIAL** | Wilcoxon on per-physical-unit mean log-ratios, bootstrap CIs and a ±10 % equivalence criterion are good. Still open: oracles and LFBC competitors remain in the Holm family; there is no pre-specified confirmatory family; within-season LOUO dependence (shared master and fleet) is not addressed; log-scale r and Lin's CCC for unit risk are not reported. |
| 5 | Novelty / prior art | **PARTIAL** | CoRe, anchor regression, graph-CT, mdi-PLS, Ren 2026, Spiers, Hayes and the authors' Talanta paper are all cited ✓. The WinISI repeatability file is named but **not cited** (Shenk & Westerhaus; Tillmann & Paul 1998). The "theory-fixed weight" novelty is still argued with a non-sequitur (see C.8 below). |
| 6 | Optimistic FR-PLS risk | **PARTIAL** | Now disclosed: 12–14 % optimism and 13 % coverage. Not fixed: no nested CV, and per-unit fleet risks are still in-sample (`predUnitsF` uses the final b). |
| 7 | Session/population confound | **PARTIAL** | A population-grouped split was added. However, populations are **not sessions**: in 2015/2017/2018, 4/10/5 scanning dates contain more than one population. Re-running `split_items(..., 'population')` shows that 0–100 % of paired-test fruit share a scanning date with transfer fruit (2017: 100 % and 89 % for seeds 0 and 1). The `'session'` option exists in protocol.py but was not run. No cross-season deployment was done. |
| 8 | Theory gaps | **PARTIAL** | Done: the RMSEP downward bias is stated; the cross-term is estimated; LFBC "exactly" is removed. Not done: the condition E[c_i] = 0 for additive effects is still missing (§2.2). The LFBC variance term is incomplete (§3.2 below). The size of the dropped noise term in Eq. (6) is not reported. The weight/LV-truncation confound is not resolved: no ridge variant and no τ² curve. |
| 9 | Qualification rule not evaluated; LFBC vs FR-PLS | **RESOLVED** | Operating characteristics vs m and spec are now given (Table S1). LFBC methods are compared separately. An ASTM D6122-style comparison is still missing (minor). |
| 10 | Soil before results; E7 bug; tablets; code | **PARTIAL** | Soil results are present ✓. E7 now uses uncentred offset shares and partial R² ≤ 0.95 ✓. **Tablets are still unreported and unexplained. Code is still "available on request".** |

### 2.2 Overclaim table (C.1–C.20)

| # | Status | Note |
|---|---|---|
| C.1 | PARTIAL | "25 units", but r is over 62 unit-seasons. |
| C.2 | RESOLVED | |
| C.3 | RESOLVED | |
| C.4 | RESOLVED | The rule is now evaluated. |
| C.5 | RESOLVED | |
| C.6 | PARTIAL | "not differing from" still reads as a match. Equivalence was *not* established (CI 0.98–1.17). Say so in the abstract. |
| C.7 | RESOLVED | |
| C.8 | **OPEN** | "the theory-fixed weight is the appropriate choice when the target is unknown" still rests on per-target oracle picks. With τ² = 1 excluded from the grid, the oracle distribution cannot show that τ² = 1 is optimal. A fleet-level τ² curve is needed. |
| C.9 | RESOLVED | |
| C.10 | RESOLVED | |
| C.11 | RESOLVED | |
| C.12 | PARTIAL | "usable from four units" while 22 % optimistic at N = 4 (1.12 vs 1.44), with 3 subsets and no CIs. |
| C.13 | **OPEN** | |
| C.14 | RESOLVED | The text is fixed; the formula is not (see §3.2). |
| C.15 | RESOLVED | |
| C.16 | PARTIAL | "to our knowledge" added. |
| C.17 | RESOLVED | |
| C.18 | RESOLVED | |
| C.19 | **OPEN** | The Significance section still says "quantified, **laboratory-free** procedure". Master labels are required, and the FR-PLS risk is optimistic. |
| C.20 | RESOLVED | |

### 2.3 Missing analyses (D.1–D.15)

| # | Analysis | Status |
|---|---|---|
| D.1 | Label-free tuned EPO/GLSW | PARTIAL (LVs not tuned; TOP missing) |
| D.2 | All-test metric | RESOLVED |
| D.3 | Grouped split and cross-season deployment | PARTIAL (population ≠ session; no cross-season) |
| D.4 | Cluster-aware inference | PARTIAL |
| D.5 | Honest FR-PLS / FR-LV risk | PARTIAL (disclosed only) |
| D.6 | Cross-term and dropped noise term | PARTIAL. Master −7 % ✓. FR-PLS cross-term is −30 % of its quadratic term and is unreported, although FR-PLS unit risk drives the decision rule. Noise-term size not reported. |
| D.7 | Corrected post-LFBC risk | PARTIAL (incomplete; still −10 % at m = 1) |
| D.8 | Operating characteristics of the rule | RESOLVED |
| D.9 | Simulation study | OPEN |
| D.10 | Additional baselines | Mostly OPEN. Pooled+LFBC added ✓. Missing: per-unit SBC/PDS, di-PLS/mdi-PLS, CoRe/repeatability-file with tuned λ, MDPS, pooled with leave-unit-out LV selection. |
| D.11 | Ridge FR variant / fleet-level τ² curve | OPEN |
| D.12 | Master-choice sensitivity | OPEN |
| D.13 | Design curves with more subsets and CIs | OPEN (still 3 subsets, no CIs) |
| D.14 | Second real fleet | PARTIAL (soil done; tablets not explained) |
| D.15 | E7 fix and scale-free heterogeneity index | RESOLVED (realised/CV ratio 1.07 vs 2.1 now serves as the scale-free index) |

### 2.4 Editor's items (A.4 / E)

| Item | Status |
|---|---|
| Code DOI | OPEN |
| ASTM E1655/D6122 framing | OPEN |
| Separate, simple graphical abstract | OPEN (Fig. 1 is reused, with stale numbers) |
| Abstract ≤ ~250 words | OPEN (267) |
| Author/affiliation/CRediT placeholders | OPEN |
| Table 1 / Table 2 | RESOLVED |
| Limitations subsection | PARTIAL (a short paragraph in §5) |
| Corn citation (Wise & Gallagher) | OPEN (URL only) |

---

## 3. New problems introduced by the revision

### 3.1 Code

**1. `methods.fr_select` (label-free EPO/GLSW tuning)**
- **LVs are not part of the search.** Each candidate keeps its master-CV/1-SE LV and `mse0`, and only k/α is chosen. FR-PLS's advantage over EPO-FR/GLSW-FR (ratios 0.86 / 0.93) is therefore still partly an advantage of fleet-risk LV selection: FR-LV alone takes the master from 2.39 to 1.82. The text ("tuned … by the same criterion"; §2.3 "The criterion can tune any transfer method") overstates the symmetry.
- **Mismatched quantities.** `mse0` comes from the full-D projection, while the quadratic term comes from half-D projections. The two terms of R̂ therefore belong to different models.
- **Bug:** `nt = noise_term(...)` is overwritten inside the `for h in (0, 1)` loop, so only the second half's noise term is used. Average it, or compute it for the full-D model.
- The projections are built from only half the fleet units. This weakens EPO with large k and is a different design from FR-PLS's 5-group unit CV. Use the same unit-held-out scheme for all methods.
- §4.3 argues that as α → 0 "GLSW converges to whitening by the difference covariance". With `s2` clipped at 0, directions with zero eigenvalues keep weight 1 while all others shrink like √α. For rank-deficient or near-singular C (SG-2nd-derivative spectra are strongly smoothed), the limit is a projection onto the null space of C, i.e. EPO with all components, not whitening. Check the rank of C, or extend the grid until the optimum is interior.

**2. LFBC offset-variance term (`protocol._lfbc_offset_var`, used in run_scenario l.240–241 and run_e4.py l.61/72)**
- The prediction is mse0 + mean(pk²) − off² − nt + s²_F/m. Here mean(pk²) − off² is the **divisor-m** in-sample variance, whose expectation is s²(m−1)/m. The expected post-LFBC risk is s²(1 + 1/m), where (1 + 1/m) = new-item variance plus offset sampling variance. The predicted quadratic part is therefore s²(m−1)/m + s²/m = s², which still falls short by ≈ s²/m.
- This explains the residual optimism at small m: master 0.96 predicted vs 1.06 realised at m = 1; FR-PLS 0.83 vs 0.88.
- Use the (m−1) divisor (or the pooled s²_F) for the in-sample term and add s²_F/m; equivalently, predict MSE₀ − noise + s²(1 + 1/m).
- Two related points: pk is per scan (about 2 per item) while m counts items, so the variance should be defined consistently at item level. And §2.2 should give the full expression, not only "+ s²_F/m".

**3. Population-grouped split (`protocol.split_items`, grouped = 'population')**
- Group key = `date|population`. As shown in §2.1 (issue 7), this does **not** prevent transfer and paired-test fruit from being scanned on the same date by the same units. §3.4's rationale ("to ensure that the unit effects learned from transfer fruit are not session effects") and §4.4's conclusion ("therefore not an artefact of shared sessions") are not supported. Run `grouped='session'` (date), or better a cross-season deployment.
- Secondary issues:
  - `off` items (never scanned on the master) still go to E regardless of group, so the all-test metric under the grouped split mixes populations again;
  - greedy size-balancing over a handful of large groups gives very unequal unit coverage, which is why only 27 of 44 grouped targets have paired data.

**4. Physical-unit aggregation (`analyse_v2.py`)**
- Correct in principle: the mean log-ratio per serial across seasons; for soil, across properties.
- The Holm families are grouped by (family, metric, A). They therefore include the oracle comparisons, which are not confirmatory and inflate the family size inconsistently between metrics.
- Per-target values are arithmetic means of RMSEP over seeds. rmseP is NaN for seeds with fewer than 10 paired items, so targets are averaged over different numbers of seeds (selective).
- The fleet-level `ratio_median` is over 30 season × seed groups, not 310 cases (§1.1 #7).
- Range coverage uses [min, max], which is not the symmetric interval described in §2.2. Soil coverage (37 %) is computed but not reported.
- `F['mango_units_in_seasons']` is a dead line that always returns None.

**5. Decision evaluation (`analyse_e4.py` / run_e4.py)**
- The spec threshold for FR-PLS uses FR-PLS's own CV RMSE (§1.1 #10).
- "Deployed out of spec" uses deployed units as the denominator, while "unfit without rule" uses all units. The conclusion's "66 % → 14 %" mixes the two denominators. Say "14 % of deployed units (9 % rejected)".

### 3.2 Logic, overclaims and contradictions

1. **"Outperforming EPO and GLSW tuned by the same criterion"** (Abstract, §5).
   - The tuning criterion is not the same (LVs; see 3.1.1).
   - By the paper's own ±10 % criterion, FR-PLS is **equivalent** to GLSW-FR (CI 0.90–0.96, `equivalent_10% = True`).
   - On all test fruit, EPO-FR has *lower* RMS than FR-PLS (1.82 vs 1.91) and the per-unit difference is not significant (median 0.91, Holm p = 0.14).
   - Qualify the claim: paired metric only, and an improvement of under 10 % over GLSW-FR.
2. **"FR-PLS+LFBC gave the lowest error of all target-label-free strategies"** is false on the paired metric (§1.1 #4).
3. **Session robustness** is overclaimed (3.1.3). Cross-season deployment, the scenario the Introduction promises ("units bought later"), is still not tested.
4. **"Calibrations are released with their expected error on future units"** (Significance) and "laboratory-free" do not fit the proposed calibration: the FR-PLS fleet risk is optimistic by 12 % (37 % in corn by mean) and its order-statistic interval covers 13 %. For the master PLS, the soil interval covers 37 % against a nominal 67 %. The distribution-free interval in §2.2 is therefore not validated on either fleet and should be presented as approximate or dropped.
5. **Oracle τ² argument** (§4.3, C.8). Because τ² = 1 is excluded from the oracle grid, the observation that oracle weights scatter on both sides of 1 cannot show that 1 is the best fixed choice. Every unit has some τ² ≠ 1 that beats FR-PLS (0 % FR-PLS wins), which is a selection effect over 8 candidates. Replace the argument with a fleet-level curve of mean log-ratio vs τ², including τ² = 1.
6. **Corn**: "the ranking was the same as for mango" is still false for the default baselines. In mango FR-LV (1.82) beats EPO/GLSW-default (2.25 / 2.28); in corn it does not (0.48 vs 0.44 / 0.42). The one-unit optimism ("a single secondary instrument cannot represent a population") is partly a design artefact: with fewer than 3 units, FR-PLS CV holds out items, not units (S2). Say so.
7. **Soil and Mitu et al. 2024.** §4.1 now says the result "agrees with" Mitu. Round 1 noted that Mitu reported a *significant* cross-unit loss. Reconcile the two, or cite precisely.
8. **FR-PLS cross-term**: −30 % of its quadratic term (vs −7 % for master PLS). This matters because the qualification rule is also applied to FR-PLS. Report it.
9. **Intro typo / fragment**: "… [@Mitu2024; @Sun2019]. and our own earlier work …".
10. **§2.2**: "The last term vanishes … for additive unit effects" still lacks the condition that the master is unbiased on the item population, E[c_i] = 0. Under the all-test metric this fails.
11. **N-curve non-monotonicity**: m = 5 gives 1.33 vs 1.28 at m = 3 and 1.27 at m = 10. "Three items gave the same accuracy" holds, but with 3 subsets and no CIs it is noise-level evidence.

---

## 4. Desk-rejection risk and the most valuable remaining improvements

**Updated desk-rejection risk at ACA: about 20–25 %** (down from 35–45 %).
- Points in favour: a coherent principle with honest reporting of both metrics; physical-unit inference with CIs; an evaluated decision rule; a soil negative control; label-free tuned competitors; a tidy Table 1 whose numbers match.
- What an editor will still notice:
  - the evidence rests on one positive fleet (mango), with a tiny corn benchmark and a soil null result;
  - no analytical-standards framing (ASTM E1655/D6122);
  - "code on request";
  - a graphical abstract with numbers that contradict the abstract (−41 %, 31 units);
  - the abstract is above the length limit;
  - placeholder author and affiliation fields.

After the fixes below, I would expect about 10–15 %.

**The three most valuable remaining improvements**

1. **Make the baseline comparison airtight.** Tune EPO/GLSW (and TOP) jointly over (k or α, LV) with the *same* unit-held-out fleet-risk CV that FR-PLS uses. Extend the grids until optima are interior. Fix the `fr_select` noise-term bug. Add the fleet-level τ² curve (including τ² = 1) and a ridge/closed-form FR variant, to test the "theory-fixed weight" claim directly. Without this, the core novelty claim (contribution 2) remains contestable: FR-PLS is already within 10 % of GLSW-FR and not better than EPO-FR on all test fruit.
2. **Test the deployment scenario the paper promises.**
   - Run a **date/session-grouped split** and a **cross-season deployment**: calibrate and estimate risk in season s, deploy to units in season s+1, with separate results for units new in s+1.
   - Make the FR-PLS risk honest with nested unit-held-out CV and unit-held-out per-unit risks.
   - Fix the LFBC variance term with the (m−1) divisor and s²(1 + 1/m), then re-validate Fig. 4b.
   - Report interval coverage against nominal for mango and soil. This decides whether "released with the expected error on future units" can stay in the abstract.
3. **A final consistency and presentation pass.**
   - Correct the 12 mismatches in §1.1: Fig. 1 / GA, the Fig. 4a label, corn 0.55, the "lowest error" claim, §3.3 item counts, the cross-term %, the 310-case wording, 26/27, Table S1 spec, and the threshold definition.
   - Unify unit and season counts.
   - Drop "laboratory-free" and qualify "outperforming".
   - Make a separate, simple graphical abstract.
   - Deposit the code with a DOI.
   - Add the ASTM/ICH paragraph.
   - Report or explain the tablets.
   - Trim the abstract to ≤ 250 words.
   - Complete the back matter.
