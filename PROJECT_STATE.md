# PROJECT_STATE (persistent checkpoint — update after every significant stage)

Last update: 2026-11-22 (session 2)

## Fixed user requirements (session 2)
- Authors: **P N Bhargav Teja** (first author, corresponding); second author = placeholder "[Second Author]".
- Funding: "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors."
- Competing interests: none declared.
- Code availability: "Code will be made available on request." Data: public (cite DOIs).
- Goal: very high novelty, avoid desk rejection; real-world problem framing welcome; compare against recent ACA papers.
- Work fully autonomously; scheduled task trig_015TacCvu2DnPWKUau3fRNyv auto-resumes every 3 h (delete when COMPLETE).

## Selected target journal
Analytica Chimica Acta (Elsevier). Median measured submission->acceptance 60.5 d. See journal_selection/selected_journal.md.

## SELECTED TOPIC (session 2) — "Fleet calibration"
Real-world problem: commercial fleets of handheld NIR units (mango DM in Australian orchards; handheld soil NIR).
A model built on one unit loses accuracy on other units of the same model (feasibility: mango master RMSE 0.7 %DM ->
1.0-4.3 %DM on other units, bias-dominated). Calibration transfer literature treats ONE master->slave pair with
standards on the target; nobody models the fleet as a POPULATION of instruments and predicts/minimises error on
units never seen.
Contributions (planned):
 1. Exact error identity e_k = e_0 + b'D (D = paired spectral difference) -> unbiased label-free estimator of the RMSEP a
    model will have on a random UNSEEN unit (fleet risk), with replicate-noise correction and unit-bootstrap CI.
 2. Fleet-risk-minimising calibration (augmented PLS with theory-fixed weight, no tuning) + LV selection by fleet risk.
 3. Label-free unit qualification test from m paired items (accept / bias-correct / recalibrate) + sample-size rule.
 4. Fleet design laws: how many fleet units N and paired items m are needed (learning curves + theory).
 5. Validation: mango v4 (31 units, 7 seasons, LOUO) + NeoSpectra soil (9 units, 2,106 soils, 6 properties) + corn (3) / tablets (2).
Baselines: master PLS, pooled multi-unit PLS (labelled), EPO, GLSW, Tikhonov transfer (Kalivas 2009), di-PLS/unit
centring, PDS/DS/SBC with target standards (scenario B).
Prior-art closest: Kalivas 2009 Appl Spectrosc (Tikhonov transfer, tuned); Hayes/Walsh 2016 JNIRS (Si PDA transfer);
Ren 2026 CILS (instrument-shift augmentation); Robert & Gosselin 2024 IPT (likelihood, multiple instruments);
UCT-LMIR ACA 2026; Talanta 2026 group-conformal (intervals); Kayaoglu & Erdem (Applied Sci, conformal under transfer).

## Data acquired (data/MANIFEST.json; data/raw is gitignored -> re-download: cd code && python -m src.data.download)
- mango_v3, mango_v4 (85,401 spectra, 31 units, 7 seasons), corn, tablets, diesel, neospectra (48,568 scans,
  2,106 soils x up to 8 of 9 units x 6 reps; CC BY 4.0, doi:10.5281/zenodo.13122321).

## Status
- [x] Phase 0 journal selection; [x] topic (fleet calibration); [x] novelty audit (literature/novelty_audit.md:
      items 1,3,4 novel; item 2 partly pre-empted by Kalivas Tikhonov -> claim theory-fixed weight + fleet pooling +
      FR LV selection; cite Grelet 2017 (66 milk MIR), Mitu 2024 (5 NeoSpectra), Ren 2026 CILS)
- [x] Method module + 17 unit tests pass
- [~] E1-E3 grid running: code/scripts/run_e1e2.py {mango,neo,corn} -> results/e1e2/*.csv (skips finished files)
- [ ] E4 learning curves: code/scripts/run_e4.py 2016 2017 2018 oc   (run AFTER e1e2 finishes)
- [x] E7 mechanism: results/e7/unit_effect_decomposition.csv (mango: offset+gain+shift explain ~90%; neo ~27%, tiny effects)
- [ ] E6 simulation figure (optional), figures, manuscript (sections in manuscript/sections/; 01_intro, 02_theory drafted)
- [ ] internal review, final packaging (docx via pandoc + CSL in manuscript/tools)

## Status (session 2, final stages)
- v3 protocol (after review rounds 1-2) complete: results/e1e2_v3, results/e4_v3, results/e6; summaries results/summary_v3.
- Manuscript fully on v3 numbers: manuscript/manuscript.docx, supplementary.docx (build: cd manuscript && python build.py),
  cover_letter.md. Figures 1-6 in manuscript/figures (scripts: code/scripts/make_figures.py, make_fig1.py, make_table1.py).
- Round-3 number audit running -> manuscript/review_round3.md

## PROJECT STATUS: COMPLETE (2026-11-22)
Manuscript package in manuscript/ (see manuscript/README.md). Only author-information placeholders remain for the user.
Scheduled auto-resume task trig_015TacCvu2DnPWKUau3fRNyv deleted.
