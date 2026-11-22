# Review round 1: "Fleet calibration of handheld near-infrared spectrometers" (draft for Analytica Chimica Acta)

Reviewer roles: (1) handling editor deciding on desk rejection; (2) expert chemometrics referee.
Material checked: `manuscript/sections/*.md` (00–07, S1), all five figures (PNG), `code/src/fleet/*.py`, `code/scripts/analyse_e1e2.py` and `e7_mechanism.py`, `results/e1e2/summary/*.csv`, the raw `results/e1e2/*.csv`, `results/e4/*.csv`, `results/e7/*.csv`, `literature/novelty_audit.md`. I recomputed every number below from the CSVs. The [SOIL] placeholder is not counted against the paper, but statements that already rely on soil results are flagged.

Overall recommendation as referee: **major revision**. The idea is useful and the mango data set suits it well. But the paper has many numerical inconsistencies. Its label-free baselines are set up unfairly. It reports one metric and omits the other. Its inference has a pseudo-replication problem. Its novelty claims about Eq. (3) and Eq. (6) are not supported by the prior art. Each of these can be fixed, but together they would sink the paper at review.

---

## A. Editor: desk-rejection risk assessment

**Estimated desk-rejection risk: moderate to high (about 35–45 %) in the current form; about 15–20 % after the fixes in A.4.**

### A.1 Scope fit
- ACA does publish chemometrics methodology, and calibration transfer with the PDS, di-PLS and UCT-LMIR line is in scope. The paper cites three 2026 ACA papers, which helps. Points in favour: the method is general across linear models, it uses public data, and its output (an expected RMSEP and a decision for each unit) is practical.
- Points against: the empirical weight rests almost entirely on one agricultural data set (mango, a single instrument model). The corn set has 3 instruments and only 2 targets per property, and the soil set is unfinished. An editor may decide that the contribution is specific to applied NIR or agriculture (JNIRS, Postharvest Biol Technol, Comput Electron Agric) or to chemometrics theory (Chemom Intell Lab Syst, J Chemom). ACA editors look for *analytical* significance: metrological qualification of instruments, links to ASTM E1655/D6122 or to ICH Q2(R2)/Q14, and pharma or process use. That case is barely made. Add a paragraph that ties the qualification rule to analyser qualification standards (ASTM D6122, E1655), and if possible a non-agricultural fleet (the tablet loader exists in `builders.py`).

### A.2 Novelty versus the closest prior art
| Prior work | What the manuscript claims | Editor's view |
|---|---|---|
| Eq. (3): e_k = ē_0 + b'd | "purely algebraic"; the novelty is the *use* | Correct and honest. However, Highlight 2 ("An exact identity predicts a model's RMSEP …") presents the identity as the discovery. The identity is textbook (IUPAC/Olivieri 2006, NAS, slope/bias practice). The new parts are the **population expectation, the replicate-noise correction and the unseen-unit estimator**, and the highlights and abstract should say so. |
| Kalivas 2009 / Kunz 2010 / Kalivas 2012 Tikhonov transfer | FR-PLS differs because (i) the weight is fixed by theory and (ii) the D block pools many units | (ii) is weak. Augmenting with several conditions or instruments is routine in TR transfer and is the WinISI **"repeatability file"** (Shenk & Westerhaus; Tillmann & Paul 1998, doi:10.1255/jnirs.122). Both stack difference spectra with target 0, often from several instruments. The audit found this reference, but the manuscript does not cite it. (i) is the real novelty, and the paper's own results weaken it: the oracle-τ Tikhonov is 12 % better by median ratio and 21 % better by RMS (1.10 vs 1.40), the theoretical weight is chosen in only 14 % of oracle selections, and PLS truncation at about 17 LVs is a second regulariser that changes the effective penalty (see B.6). |
| EPO / TOP / GLSW | "hard-threshold or re-weighted limits of the same idea" | Plausible, but no derivation or citation is given. Either show it (for example, GLSW as a generalised-ridge penalty with b'C_D b) or soften it. |
| di-PLS / mdi-PLS (Nikzad-Langerodi 2018; Mikulasek 2023), graph-based CT (Nikzad-Langerodi & Sobieczky 2021), CoRe (Heinze-Deml & Meinshausen 2021), anchor regression | Only di-PLS is cited | CoRe is *exactly* a penalty on the variance of predictions across repeated observations of the same object (the paired-item structure), with a tuned λ. Graph-CT penalises paired standards on two instruments. A referee will raise both. mdi-PLS handles many domains. Cite all of them and show where the fixed weight and the unit-population view differ. |
| Grelet 2017 (66 MIR milk analysers) | Cited and contrasted | Adequate. Add that Grelet's master–slave prediction differences are exactly the label-free b'd statistic. The contribution here is to aggregate it into a risk and project it onto unseen units. |
| Spiers et al. 2021 (Anal Chem; JCIM) label-free model/LV selection | Not cited | This is the closest prior work for FR-LV (label-free LV selection under instrument change), and it is missing. |
| Ren et al. 2026 CILS (instrument-shift-informed augmentation) | Not cited, and not read according to the audit | This is the main unchecked threat to contribution 2. Read it before submission. |
| Hayes et al. 2016/2019 (same Si-PDA/F750 lineage, a global multi-unit model, bias adjustment from mean difference spectra) | Cited only for hardware tolerances | Hayes already used **bias adjustment from mean difference spectra**, which is the LFBC of this paper. Credit it explicitly, and do not present LFBC as new (§2.2 names it as if it were). |
| Own prior work: group-conformal intervals for new instruments/seasons on the same mango data (Talanta 2026, doi:10.1016/j.talanta.2026.130941) | **Not cited** | This must be cited. The data, scenarios and author overlap make it a transparency issue, and an editor who finds it uncited may treat it as redundant publication. Cite it in the Introduction as the step from labelled intervals to label-free risk. |

### A.3 Clarity of the "new principle"
The principle is clear: units are a random population, the risk on an unseen unit is identifiable from paired spectra, and that risk is minimised. However:
- The front matter frames contributions 1–4 as a package. An editor wants a one-sentence principle, followed by the evidence that it works *and* beats the obvious alternative. The obvious alternative is "scan five items on each new unit and bias-correct" (LFBC). Master+LFBC already gives RMS 1.15 %DM, which beats FR-PLS (1.40 %DM, Holm p = 0.051 the other way). The paper must explain when FR-PLS matters, namely when no unit-specific scans are possible.
- "Label-free" is used loosely. Master labels are required, so the accurate term is "target-label-free" or "without reference analyses on fleet units". Define the term once in the abstract.

### A.4 What would lower the desk risk
1. Make every number consistent (section B.3). 2. Cite the missing prior art (A.2), including the authors' own Talanta paper. 3. Drop "exact identity" and "no tuning" from the highlights. 4. Add a second fleet with real units: soil (in progress) or tablets. 5. Publish the code in a repository (Zenodo or GitHub) rather than "on request".

---

## B. Major methodological concerns

### B.1 Leakage audit (code)
I checked `protocol.split_items`, `run_scenario`, `methods.*` and `data.paired_differences`.
- **No direct leakage found.** Calibration (C), transfer (T) and test (E) items are disjoint. The target unit k is excluded from the fleet F (`F = [u for u in units if u != k ...]`), so it contributes no D rows to FR-LV, FR-PLS, EPO, GLSW, Tikhonov, pooled PLS or the fleet-risk prediction. Σ₀ comes only from master calibration items. The transfer-item labels are used only by pooled PLS, as stated. Pre-processing is row-wise. The master is chosen from the coverage table (label-free), using the target's coverage, which is harmless.
- **Indirect leakage through sessions and populations (important).** In the mango data, *every* multi-unit item was scanned on all its units on one date (checked for 2018: 1 097 multi items, 1 date each). Populations are scanned by subsets of 2–10 units. T and E are a random split of the same multi-unit items, so transfer and test fruit come from the same populations, dates and scanning sessions. As a result:
  - The fleet units' D rows were acquired in the same sessions (temperature, operator, warm-up) as the target's test scans. Unit effects that are really session effects are "learned" by FR-PLS and then evaluated under the same session conditions.
  - In scenario B (unit risk), the target's own transfer and test scans come from the same sessions. The r = 0.98 is therefore close to an internal-consistency check of Eq. (3), as §4.2 partly admits ("Agreement holds because Eq. (3) is exact").
  - Required: split T and E **by population or date**, so that transfer fruit and test fruit come from different sessions. Also run a **cross-season** validation: build the calibration and fleet risk in season s and deploy to units in season s+1, especially units that are new in s+1. That is the "unit bought next year" scenario the paper promises.
- `fr_pls` with fewer than 3 fleet units holds out *items*, not units (S2). The CV quadratic term then comes from units the model was trained on, which explains much of the optimism at N = 1–2 in Fig. 4a (predicted 0.80 vs realised 1.50 %DM). §4.3–4.4 attribute this to "a single secondary instrument cannot represent a population", but part of it is a design artefact. Say so.

### B.2 Fairness of the baselines
1. **Default EPO and GLSW are straw men, and the paper's own tool could tune them label-free.** EPO (k = 2) and GLSW (α = 0.01) use arbitrary defaults, and their LVs are chosen by master CV with the 1-SE rule. FR-LV and FR-PLS choose LVs by fleet risk. FR-LV alone cuts RMS from 2.39 to 1.82, so LV choice by fleet risk is itself a large effect. Eq. (5) applies to *any* linear b, so a fair label-free comparison is **EPO/GLSW/TOP with (k or α, LV) chosen by minimum R̂_F (unit-held-out)**. Without it, "FR-PLS beats EPO/GLSW" mostly shows that fleet-risk selection beats arbitrary defaults. This is the single most important missing analysis.
2. **The oracle grids are truncated, so the oracles are not upper bounds.** Across the 445 mango target × seed cases:
   - EPO picks k = 10, the largest grid value, in 99 cases and k = 8 in 81. The grid is {1–6, 8, 10}, while the text says {1,…,10}.
   - GLSW picks α = 10⁻⁴, the smallest grid value, in 223 cases (50 %).
   The optimum is usually at or beyond the grid edge. Extend the grids until the optimum is interior, or drop "upper bounds".
3. **Tikhonov oracle.** Its LVs are fixed at FR-PLS's LV count, and the τ² grid {0.01, …, 100} contains τ² = 1, which *is* FR-PLS. FR-PLS therefore can never beat it (0 % wins is guaranteed, not a finding). This must be stated in Methods. The selected τ² values are 10: 91, 3: 82, 0.01: 71, 1: 63, 0.1: 62, 0.3: 47, 100: 29. τ² = 1 wins in only 14 % of cases. The claim that a spread "with no systematic direction confirm[s] that τ² = 1 is the appropriate unbiased choice" is a non-sequitur: per-target oracle picks on noisy test errors say nothing about the population optimum. Replace it with a **fleet-level τ² curve** (mean log RMSEP ratio vs τ², with CI over targets) or with τ² chosen label-free by unit-held-out R̂_F.
4. **Pooled PLS.** Its LVs are chosen by item-grouped CV with the 1-SE rule on pooled data, not by unit-held-out CV. Units are unweighted, so units with more transfer items dominate. It uses labels for only one third of the multi-unit items. Calling it "a fully labelled multi-instrument calibration" overstates it. Add pooled PLS with leave-unit-out LV selection, and pooled + LFBC.
5. **LFBC appears only for master PLS and FR-PLS.** Fig. 3 puts FR-PLS+LFBC beside methods that use no target scans. Either give every method its LFBC variant (EPO+LFBC, pooled+LFBC) or show unit-specific methods in a separate panel. Also add the classical per-unit methods that use the same target scans: SBC on master predictions, PDS/DS from the target's transfer items, and TOP.
6. **The oracle is selected on the test set itself.** It is chosen on the same test scans on which it is scored, so it is optimistically biased by selection noise as well as by information. State this, or use a separate labelled target subset for tuning.

### B.3 Do the claims match the tables? (recomputed from CSVs)
| Location | Manuscript says | Tables/figures say | Verdict |
|---|---|---|---|
| Abstract, Fig. 1, Intro | 31 units | 31 instruments in v4, but **30** units in the analysed seasons 2015–2020 and **25** physical units with paired test data | Fix |
| Highlight 3 | "across **62 handheld mango units**" | 62 unit×season cases from **25 physical units** | **False as worded** |
| Abstract vs Intro vs §3.1 | "six seasons" / "seven seasons" / 2015–2021 with 2021 excluded | 6 analysed seasons | Harmonise |
| Abstract, Intro | 85 401 spectra; 13 953 fruit | Raw file size. After `outlier_flag==0`, 78 159 spectra and 12 970 items, including 2021, which is not analysed | Report the analysed numbers |
| §3.2 | "56 mango target-unit/season combinations" | 89 (all-test), 62 (paired), 59 (Fig. 3), 40 (Fig. 2) | **Four different n's.** Fig. 2 (n = 40) gives r = 0.955, not 0.98 |
| §4.3 | FR-PLS better than master on "81 % of the **89**" cases, "median ratio **0.68**" | Paired: 82.3 % of 62, median 0.658 (E2_tests). All-test: 78.7 % of 89, median 0.699. Fig. 3: n = 59, median 0.683 | Mixed sources; fix |
| §4.3 | FR-PLS better than EPO and GLSW defaults in "79 % and 83 %" | 82.3 % and 85.5 % | Fix |
| §4.3 | GLSW-oracle vs FR-PLS "p = 0.44" | p = 0.80 (Holm 0.80) | **Wrong** |
| §4.3 | FR-PLS vs pooled "p = 0.15" | p = 0.235, Holm 0.47 | **Wrong** |
| §4.3 | Gap to oracle EPO/Tikhonov "≈ 15 %" | Median ratios 1.11 and 1.12; RMS ratios 1.22 and 1.27 | Fix |
| §4.2 | Range coverage 77 % "close to the nominal (N−1)/(N+1) of 85–90 % for fleets of 10–22 units" | Fleet sizes 5.6–13 (mean 10.1). Mean nominal level is 0.81 | Fix the numbers. The observed 77 % is below nominal |
| §4.2 | Unit risk "equally good" after FR-LV/FR-PLS (r = 0.85–0.87) | r = 0.85 and 0.87, Spearman 0.79 and 0.74, MAPE 8.4 % and **14.9 %** (vs 6.9 % for master) | Not "equally good" |
| §4.2, §5 | Fleet-level prediction "within 1 %" | True for master PLS only. FR-LV: 1.51 predicted vs 1.83 realised; FR-PLS: 1.20 vs 1.39; corn FR-PLS: 0.21 vs 0.34 | Report all |
| §4.3 corn | "Ranking was the same", FR-PLS better than master in 8/8 | Correct, but Holm p = 0.078 (n = 8 is the minimum attainable). In corn, EPO-default (0.44) and GLSW-default (0.42) also improve hugely on master (1.35) and are not significantly worse than FR-PLS (Holm 0.31 and 0.12) | Remove "same ranking" for the default baselines |
| §4.3 mango | EPO/GLSW defaults "did not improve on the master" | True for mango; false for corn (ratio ≈ 0.29) | Qualify |
| §4.4 | 4-unit prediction "1.15 vs 1.26–1.40 realised", "reliable from four units" | 1.14 vs 1.40 at N = 4 (19 % optimistic); 1.17 vs 1.24 at "all" | "Reliable" overstated |
| Fig. 4a axis | "all (≤ 22)" | max n_fleet = 13 | Fix the label |
| §4.4 | r = 0.95 (Spearman 0.88), MAPE 16 % with five fruit | Median over draws: r = 0.954, Spearman 0.889, MAPE **12.6 %** | Recheck MAPE and define the aggregation clearly |
| §3.3 | LFBC used "10–300 items per unit" | n_pairs_target 0–326, median 36; 25 % of mango targets have **0** transfer items, hence n = 40 in Fig. 3 | Fix and explain the missing targets |
| §4.1 | "gain differences contributing most" | `partR2_offset` has median 8.6 and maximum 168. Partial R² > 1 is a **bug** in `e7_mechanism.py`: the drop-one comparison uses a centred TSS, so dropping the intercept is not comparable | Fix the computation before making any claim |
| §4.1 | FR-LV LVs 10.6 vs 11.7 | Correct | OK |
| §4.1–4.3 | 2.39, 1.15, 1.82, 1.40 (−41 %), 2.25, 2.28, 1.32, 1.15, 1.10, 1.34 | Correct (paired metric, 62 targets), **but** E2_methods_rms labels them n_targets = 89 | Fix the table label |

### B.4 Selective reporting of the error metric (important)
§3.2 says mango errors are reported "also on all test items", but §4 never shows them. On all test items (89 targets), the RMS values are:

| Method | RMS (%DM) |
|---|---|
| Master | 2.34 |
| FR-LV | 2.21 |
| FR-PLS | 1.90 (**−19 %**, not −41 %) |
| Pooled | 1.75 |
| EPO-oracle | 1.40 |
| Tikhonov-oracle | 1.26 |
| Master+LFBC | 1.37 |
| FR-PLS+LFBC | 1.07 |

The paired metric isolates the unit effect, which is legitimate for E1. But an operator deploys the model on new fruit populations, so the all-test metric is the deployment-relevant one. Both must be reported, and the abstract and highlights must make clear which metric the 41 % refers to. Note also that Eq. (2) assumes that the item distribution in deployment matches that of the master calibration and transfer items. It ignores the covariate shift across orchards that the all-test metric shows.

### B.5 Statistics: is the target unit an appropriate unit of inference?
- Averaging over seeds before testing is good practice. However, the **62 "target units" are 25 physical units observed in up to 6 seasons**, so the same serial number enters several times. In addition, LOUO targets within a season share the same master, calibration set and most of the fleet, so their outcomes are positively correlated. The Wilcoxon test's independence assumption is violated, and the p-values (down to 10⁻¹¹) are anticonservative.
- Remedies:
  - a linear mixed model on log(RMSEP ratio) with random effects for physical unit and season (crossed); or
  - a cluster (physical-unit) bootstrap or permutation test; or
  - a Wilcoxon test on per-physical-unit means (n = 25).
  Report CIs on the RMS and median ratios, not only p-values.
- Testing FR-PLS against oracle methods is not meaningful, because oracles are reference bounds. The Holm family mixes competitors, oracles and LFBC variants. Define a small set of pre-specified confirmatory comparisons: FR-PLS vs master, vs label-free tuned EPO/GLSW, and vs pooled. Treat the rest as descriptive.
- "Indistinguishable" and "matched" are claimed from non-significance (GLSW-oracle p = 0.80; pooled p = 0.23). That is absence of evidence. Use **equivalence testing** (TOST on the log ratio with a margin set beforehand, for example ±10 %) with a CI. FR-PLS is in fact 5 % *worse* than pooled by median ratio (1.05).
- Corn: n = 8 consists of 2 targets × 4 properties. The Pearson r = 1.00 is computed across properties with different units and scales (moisture, oil, protein, starch), so it is inflated by between-property scale. Report it per property, or on relative errors, or drop it. Corn cannot support inferential statements.
- Unit-risk correlations (r = 0.98) on a linear scale are dominated by a few large-error units (up to 6.9 %DM). Report log-scale r and Lin's concordance correlation coefficient. Log-r in E4 is 0.90 for master PLS and 0.85 for FR-PLS at m = 5.

### B.6 Is the derivation in S1 correct?
- **The algebra is correct** under the stated assumptions. b is fixed and independent of the test/transfer items. Noise is zero-mean and independent across scans, items and units, and independent of a. I verified the elimination step, the claim that Σ_k cancels, and the harmonic-mean r₀ used in `paired_differences`, which matches "mean of 1/r₀ᵢ".
- Problems and gaps:
  1. **"Unbiased"** is overstated:
     - (a) MSE₀ is a CV estimate for models trained on 80 % of the data and selected with a 1-SE rule, not the error of the final b.
     - (b) The estimate is unbiased for the MSE, not the RMSEP. The paper reports √R̂, which is biased low by Jensen's inequality.
     - (c) R̂ is clipped at 10⁻¹².
     - (d) MSE₀ (calibration-item population) and the D term (transfer-item population) are taken over different item populations, because master-only items are added to calibration.
     Say "unbiased for the MSE under (1) and with an unbiased MSE₀", and quantify the RMSEP bias.
  2. **The cross-term argument is incomplete.**
     - For a purely additive effect a_ik = a_k, the term equals 2(b'a_k)·E[c_i], which is zero only if the master is unbiased on the deployment item population. That fails on the all-test (other-orchard) metric.
     - For gain effects, a_ik = G_k s_i, the term is 2·cov(c_i, b'G_k s_i). PLS shrinkage makes residuals correlate with y and with the prediction, so this term need not vanish.
     - The text says the term "can be tested with labelled pairs (Section 4.2)", but §4.2 does not test it. It only infers its smallness from a median ratio of 0.99. The labels exist: **estimate the cross-term directly** on the labelled paired test items for every unit and report its distribution relative to R_k.
  3. **LFBC is described as "removed exactly". It is not.** The offset is estimated from m items with sampling variance about Var(b'd)/m, plus noise. That error carries into every subsequent prediction. The corrected-risk formula (Eq. 5 with the squared mean removed; code line `q = mean((Dk@b)^2) - off^2`) omits this term and also uses the biased variance estimator (divisor m). The results show the predicted post-LFBC RMSEP is **optimistic at small m**:

     | m | Predicted (%DM) | Realised (%DM) |
     |---|---|---|
     | 1 | 0.78 | 1.06 |
     | 5 | 0.91 | 0.96 |

     At m = 1 the predicted value is just MSE₀ minus noise. Derive the correct expression: approximately MSE₀ + s²_{b'd}(1 + 1/m) − noise terms, with an (m−1) divisor.
  4. **The "theory-fixed weight" claim (Eq. 6).** The fixed weight minimises the empirical risk only for the full least-squares solution. FR-PLS truncates the PLS solution at about 17 LVs (mean 16.9; 19 % of cases at 19 or more, near the A = 20 cap), and LV truncation is a second, data-chosen regulariser that interacts with the weight. "No tuning" is therefore not accurate: the LV number is tuned label-free. Either present a ridge or closed-form variant in which the weight is the only regulariser, or reword the claim (C below).
     - The dropped noise term −(1+1/r₀)b'Σ₀b is negative semidefinite. Omitting it means FR-PLS minimises an upward-biased risk that over-penalises noise directions. The text calls it "small, b-shrinking", but its size is never reported. Report it.
     - Also explain why the augmented model needs so many more LVs (17 vs 12). Augmented rows of D are added to the X-space, so PLS has to model D-variance with target 0.
  5. **Order-statistic prediction interval.** Exchangeability holds for the *true* risks. The paper compares *estimated* fleet-unit risks with the *realised* RMSEP of the new unit, and the two are computed on different items with different noise. Coverage is then only approximate. Coverage was also computed with the [min, max] range, not the symmetric (j, N+1−j) interval described in §2.2. State this.
  6. **"Five items suffice" (S1, last sentence)** is not derived. Give Var(R̂_k) ≈ Var[(b'd)²]/M_k, and from it the m needed to reach a target relative precision.

### B.7 Is the risk estimator honest for FR-PLS?
- **Fleet level.** `predF|FR-PLS` is `risk_cv` at its own argmin, so the same CV curve is used to select the LV count and to report the risk (winner's curse). The noise term uses the final B, while MSE₀ and q come from fold models. Result: FR-PLS fleet risk is optimistic by about 14 % in mango (1.20 vs 1.39; median ratio 0.91) and 37 % in corn (0.21 vs 0.34). FR-LV has the same issue (`fleet_risk` evaluated at the argmin of the same R), with 1.51 vs 1.83. Use nested CV, or report the risk at the selected LV from an outer unit-held-out loop.
- **Unit level within the fleet (`predUnitsF`).** For FR-PLS this is computed with the final m.b, which was *fitted to those same D rows*, so it is an in-sample estimate. The resulting range coverage is **13 %** for FR-PLS and 62 % for FR-LV, against 77 % for master PLS. This is unreported, and it means the "expected error of a calibration on units bought later" interval does not work for the proposed calibration. Fix it with unit-held-out per-unit risks, or report it as a limitation.
- **Unit level for the target (`predK|FR-PLS`).** This uses the target's own D, which was not used in fitting, so it is honest. Its MAPE is still 15 %, double that of master PLS.

### B.8 Other concerns
- **The qualification rule (contribution 3) is never evaluated as a decision.** No specification limit is set, and no false-accept or false-reject rates or confusion matrices against the realised RMSEP are reported. "Accept / bias-correct / reject" needs operating characteristics vs m. ASTM D6122-style acceptance is the benchmark.
- **The master choice is fixed** (the unit with most shared items). Show sensitivity to a random or worst-case master.
- **Fig. 5 / §4.1, comparison of mango vs soil absorbance RMS ("five times smaller").** The instruments, wavelength ranges, optical geometries (interactance vs diffuse reflectance) and reference definitions differ, so raw-absorbance RMS is not comparable across fleets. Compare b'd̄ relative to the SD of y, or the risk ratio R_F/MSE₀, instead. The decomposition uses the *mean* difference only, so item-dependent gain is not tested. "Explained 91 %" is a centred R² that excludes the offset.
- **Soil statements made before the soil results exist.** §4.1 calls the soil fleet a "natural negative control". §5 says "the estimator correctly predicted that little was to be gained". Both need the E1/E2 soil results. Note also that Mitu et al. 2024 report a *significant* cross-unit loss on 5 NeoSpectra units, so the negative-control framing has to be reconciled with that.
- **Tablets.** `builders.tablets()` exists, but no results are reported. A referee who reads the code will ask whether data sets were dropped selectively. Either report the tablets or explain why they were not used.
- **Reproducibility.** "Code will be made available on request" is weak for a methods paper. Deposit the code with a version DOI. State the PLS LV cap A = 20, and note that FR-PLS approaches it.

---

## C. Overclaims and suggested rewording

| # | Location | Current | Problem | Suggested |
|---|---|---|---|---|
| 1 | Highlight 3 | "Predicted and realised errors agree (r = 0.98) across 62 handheld mango units." | 62 cases from 25 units; paired metric | "Label-free unit-error predictions tracked realised RMSEP (r = 0.98, 62 unit-seasons)." (79 chars) |
| 2 | Highlight 4 | "…cuts error on unseen units by 41 % with no tuning or target labels." | LVs are tuned; −41 % holds for the paired metric only (−19 % on all test fruit) | "Fleet-risk PLS lowered unseen-unit error by 41 % (paired fruit) without target labels." (shorten to ≤ 85 characters) |
| 3 | Highlight 2 | "An exact identity predicts a model's RMSEP on any unit without reference analyses." | The identity is textbook; the estimator is the contribution | "A population risk estimator predicts RMSEP on unseen units from paired spectra." |
| 4 | Highlight 5 | "Five paired items qualify a new unit … lab-free." | The decision rule is never evaluated | "Five paired items predict a new unit's error and remove most of its bias." |
| 5 | Abstract | "unbiased, label-free estimate" | See B.6.1 | "approximately unbiased (for MSE) estimate that needs no reference analyses on fleet units" |
| 6 | Abstract, §5 | "matched a fully labelled multi-instrument calibration" | Only transfer items are labelled; no equivalence test; FR-PLS is 5 % worse by median | "performed similarly to a pooled calibration that used reference values of the transfer fruit (median ratio 1.05; equivalence not tested)" |
| 7 | §4.3 | "indistinguishable from FR-PLS, p = 0.44" | Wrong p; non-significance ≠ equivalence | "not significantly different (p = 0.80)", plus a TOST |
| 8 | §4.3 | "confirming that the theoretical weight τ² = 1 is the appropriate unbiased choice" | Non-sequitur | "Per-target optimal weights varied widely (0.01–100) and τ² = 1 was selected in 14 % of cases; across the fleet, …" (add the fleet-level curve) |
| 9 | §4.3 | "FR-PLS reaches the accuracy … of an oracle-tuned GLSW … with … no tuning" | GLSW oracle grid truncated; LVs tuned | "…without target labels; its LV number is selected by unit-held-out fleet risk" |
| 10 | §4.2 | "This is the first quantity a fleet operator needs and … has not previously been obtainable" | Strong priority claim | "…to our knowledge has not been estimated before deployment" |
| 11 | §4.2 | "The prediction is equally good after the calibration has been made fleet-robust" | MAPE doubles; fleet-level 14 % optimistic; 13 % coverage | "The unit-level prediction remained informative (r = 0.87, MAPE 15 %), but the fleet-level risk of FR-PLS was optimistic by ~14 %" |
| 12 | §4.4 | "the *claimed* fleet accuracy should be backed by at least four units" / "reliable from four units" | Still 19 % optimistic at N = 4; 3 random subsets only | "was less optimistic from four units on (−19 % at N = 4, −6 % with all units)" |
| 13 | §2.2 | "The last term vanishes … for additive unit effects" | Only if the master is unbiased on the item population | Add the condition E[c_i] = 0 |
| 14 | §2.2 | "The bias term is removed exactly by … LFBC" | Offset estimation error | "removed up to the sampling error of the estimated offset (variance ≈ s²/m)" |
| 15 | §2.3 | "Projection methods … are hard-threshold or re-weighted limits of the same idea" | Unproven | Cite or show it; otherwise "are closely related" |
| 16 | Intro | "the two largest public multi-unit NIR data sets" | Unverified superlative | "two large public multi-unit NIR data sets" |
| 17 | §4.1, §5 | Soil "negative control … correctly predicted little to be gained" | No soil results yet | Remove until the [SOIL] results exist |
| 18 | §3.3 | "Oracle settings … serve as upper bounds" | Grids truncated; the Tikhonov grid contains FR-PLS | "serve as optimistic references within the grids used" |
| 19 | Abstract, Significance | "converts … from a trial-and-error exercise into a quantified, laboratory-free procedure" | Master labels are still needed; decision accuracy is untested | "…into a procedure that needs reference analyses only on the master unit" |
| 20 | §4.1 | "gain differences contributing most" | The partial-R² computation is buggy | Recompute; use uncentred TSS or the LMG/Shapley decomposition |

---

## D. Missing analyses, ranked by importance (effort in brackets)

1. **Label-free tuned EPO, GLSW and TOP**, with (k or α, LV) chosen by minimum unit-held-out R̂_F, plus extended oracle grids. [Low–medium: code exists. One more loop in `run_scenario`; about 1 day of compute.]
2. **Report the all-test-fruit metric alongside the paired metric** in every table and figure. [Low: already in `per_target.csv`.]
3. **Session- and population-grouped T/E split, plus cross-season deployment** (calibrate and estimate in season s; deploy to units in s+1, including units new in s+1). [Medium–high: needs a new split function and 1–2 days of compute.]
4. **Cluster-aware inference**: a mixed model or physical-unit bootstrap, CIs for all RMS and ratio values, TOST equivalence against pooled and the GLSW oracle, and a pre-specified confirmatory family. [Low.]
5. **Honest FR-PLS and FR-LV risk**: nested CV for the fleet risk, unit-held-out per-unit risks, and coverage for all three models. [Medium.]
6. **Direct estimate of the cross-term** on the labelled paired test items, per unit; also the size of the dropped noise term in Eq. (6). [Low.]
7. **Corrected post-LFBC risk formula with the 1/m term, re-validated in Fig. 4b.** [Low.]
8. **Operating characteristics of the qualification rule**: for specification limits (for example 1.0 and 1.5 %DM), false-accept and false-reject rates vs m, compared with an ASTM-style labelled check. [Low–medium.]
9. **A simulation study** with known population unit-effect distributions (additive, gain, shift; varying N, M_k and r₀). It should report the bias of R̂ (MSE and RMSEP), interval coverage, and FR-PLS vs a ridge-form solution. The unit tests exist, but a reader needs this in the SI. [Medium.]
10. **Additional baselines.** [Medium: di-PLS has a public implementation.]
    - mdi-PLS / di-PLS (multi-domain, unlabelled);
    - CoRe / repeatability-file augmentation with a tuned λ;
    - Spiers MDPS for label-free LV selection (vs FR-LV);
    - per-unit SBC and PDS using the target's transfer items (vs LFBC);
    - pooled PLS with leave-unit-out LV selection;
    - pooled + LFBC.
11. **A ridge or closed-form FR variant (Tikhonov without PLS truncation)**, to test the "theory-fixed weight" claim cleanly; and a fleet-level curve of τ² vs error. [Low–medium.]
12. **Master-choice sensitivity** (random master; worst-case master). [Low.]
13. **Design curves (Fig. 4a) with more than 3 random subsets per N**, separating the number of units from the number of D rows (n_D grows with N); add CIs. [Medium compute.]
14. **A second real fleet**: complete the soil analysis, and report tablets or explain why they were excluded. [In progress / low.]
15. **Fix the E7 decomposition** and use a scale-free fleet heterogeneity index, for example R_F/MSE₀ or b'd̄/SD(y). [Low.]

---

## E. Writing and structure against ACA conventions

- **Structured abstract.** The Background / Results / Significance format matches ACA. The abstract is 289 words. Check the current ACA Guide for Authors limit (about 250 words) and trim. The Results paragraph should give the metric (paired fruit) and n for every number.
- **Highlights.** There are five highlights of 78–83 characters (excluding the bullet), all ≤ 85, so the format is compliant. The content of highlights 2–5 needs correcting (C.1–C.4). Avoid "exact identity" and "lab-free".
- **Graphical abstract (Fig. 1).** It is readable, but it has six boxes, crossing arrows and long equations, and it hard-codes "−41 %" and "31 mango units", which are inconsistent with the text. ACA graphical abstracts should be simple: one flow and no equations. Make a separate, simpler GA, and keep Fig. 1 as the workflow figure with the numbers corrected.
- **Length.** About 4 900 words of main text, 5 figures and no tables, which is fine for an ACA full-length article. Add **Table 1** (data sets: units, seasons, items, multi-unit items, spectra analysed, fleet sizes, paired items per unit) and **Table 2** (method × data set RMS with CIs, both metrics, n). Numbers are currently scattered through the prose, which is why they drifted apart.
- **Figure-specific issues.**
  - Fig. 2: n = 40 does not match the 62 in the text.
  - Fig. 3: n = 59 does not match 62; FR-PLS+LFBC (which uses target scans) is mixed with methods that use none.
  - Fig. 4a: the "≤ 22" label is wrong, and N = 1, 2, 4 is non-monotone with only 3 subsets and no CIs.
  - Fig. 4b: the predicted LFBC curve rises with m while the realised curve falls. This shows the missing 1/m term, and it needs discussion.
  - Fig. 5: the y-axis is a centred R², and mango and soil are on non-comparable absorbance scales.
- **Methods details to add.** State:
  - the LV cap (A = 20);
  - the exact EPO and GLSW grids;
  - that Tikhonov uses FR-PLS's LV count and contains τ² = 1;
  - that oracles are chosen on the same test scans;
  - outlier exclusion counts;
  - why 2015 is in E2 but not E4 or E7;
  - how scans per unit differ (r_k);
  - that the mango spectra are absorbance;
  - the E4 aggregation, "median over repeated draws … single draw per unit", which is ambiguous.
- **Discussion.** Section 4 is all results. A short "Limitations and relation to prior work" subsection is needed. It should cover the cross-term, session confounding, the all-test metric, time drift, master dependence, the fact that the risk is an MSE quantity, and the relation to repeatability files, TR and CoRe.
- **Terminology.** Use "target-label-free" consistently, and "unit–season" for the inferential unit. %DM formatting: ACA style is "% DM" or "%DM". Pick one.
- **Back matter.** Placeholder author, affiliation and CRediT text need completing. The data availability statement is good. Add the code DOI. The AI declaration is fine. Cite the corn data properly (Wise & Gallagher / Eigenvector), not only by URL.
- **Self-citation.** The Talanta 2026 paper by the same author on the same mango data must be cited. Disclose the overlap in the cover letter.

---

## Top 10 issues by severity

1. **Numbers in the text do not match the tables and figures.** Three different unit counts (31/30/25), five target counts (56/62/89/59/40), two wrong p-values (0.44 vs 0.80; 0.15 vs 0.23/0.47), wrong win rates, a wrong fleet-size range and a wrong gap percentage. Highlight 3 ("62 units") is false as worded.
2. **Unfair label-free baselines.** EPO and GLSW use arbitrary defaults and master-CV LV selection, while FR methods get fleet-risk selection. The oracle grids are truncated (optimum at the grid edge in 22–50 % of cases), and the Tikhonov oracle grid contains FR-PLS itself.
3. **Selective metric.** The −41 % is on paired fruit only. On all test fruit it is −19 % (1.90 vs 2.34), and that metric is omitted even though Methods promises it.
4. **Pseudo-replication.** The 62 cases are 25 physical units across seasons, and LOUO targets are correlated. The Wilcoxon/Holm p-values are anticonservative. "Matched" and "indistinguishable" rest on non-significance (no TOST). Corn has n = 8 with Holm p = 0.078.
5. **Novelty and prior art.** The repeatability file, CoRe, graph-CT, mdi-PLS, Spiers MDPS, Ren 2026, Hayes' bias adjustment and the authors' own Talanta 2026 paper are not cited. The "fixed weight" claim is the real novelty, but the oracle-τ result and PLS truncation undercut it.
6. **The FR-PLS risk estimator is optimistic.** It has a winner's curse (fleet level 14 % optimistic in mango, 37 % in corn), and its in-sample per-unit risks give 13 % interval coverage. Neither is reported.
7. **Session and population confound.** Transfer and test fruit come from the same scanning dates and populations. A grouped split and cross-season validation are needed.
8. **Theory gaps.** "Unbiased" is overstated (RMSEP, CV-based MSE₀). The cross-term is not tested although labels exist. LFBC is said to remove bias "exactly" but the 1/m term is ignored, so the post-LFBC prediction is optimistic at small m (0.78 vs 1.06 at m = 1). The theory-fixed weight is confounded by LV truncation (about 17 LVs).
9. **The qualification rule is never evaluated as a decision** (no error rates). Master+LFBC (1.15) beats FR-PLS (1.40), and the paper must explain when FR-PLS is needed.
10. **Soil claims made before the soil results exist.** Also: the E7 partial-R² bug (values > 1) and the non-comparable absorbance scales, tablets loaded but not reported, and code available only "on request".
