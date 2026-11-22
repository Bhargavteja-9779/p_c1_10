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

## Key results (final for mango/corn; soil pending)
- Mango (62 target units w/ paired test): label-free unit risk r=0.98, MAPE 6.9%, ratio 0.99; corn r=1.00.
- Fleet-level (LOUO): master predicted 2.42 vs realised 2.40 %DM; range coverage 77%.
- RMS RMSEP unseen units: master 2.39, FR-LV 1.82, FR-PLS 1.40 (-41%), pooled-labelled 1.34, GLSW-oracle 1.32,
  EPO-oracle 1.15, Tikhonov-oracle 1.10, master+LFBC 1.15, FR-PLS+LFBC 0.98. FR-PLS vs master: 81% wins, p<1e-4.
- E4: N units: 1 unit already helps; prediction reliable from N>=4. m=5 paired fruit: LFBC 1.85->0.96 (master),
  1.24->0.82 (FR-PLS); single-draw unit risk r=0.95, MAPE 16%.
- E7: mango unit effects 91% explained by offset/gain/shift/bandwidth (gain dominant); soil tiny & unstructured.

## Manuscript
- manuscript/sections/*.md ; build: `cd manuscript && python build.py` -> manuscript.docx, supplementary.docx
- Figures: `cd code && python scripts/analyse_e1e2.py && python scripts/make_figures.py && python scripts/make_fig1.py`
- Abstract contains "[SOIL]" placeholder; results 4.x lacks soil paragraph -> fill when neo runs finish.

## Exact next step (resume here)
1. Wait/finish NeoSpectra jobs: results/e1e2/neo_{oc,clay,ph,n,cec,sand}.csv (relaunch missing ones:
   `cd code && nohup python scripts/run_e1e2.py neo 5 <props> &`), and results/e4/neo_oc_*.csv (`python scripts/run_e4.py oc`).
2. analyse_e1e2.py -> add soil paragraph (negative control) in 04_results.md, replace [SOIL] in 00_front.md, Fig 2/3 regenerate.
3. Internal review pass (reviewer-style critique), polish, build docx, final commit. Then delete scheduled task trig_015TacCvu2DnPWKUau3fRNyv.
