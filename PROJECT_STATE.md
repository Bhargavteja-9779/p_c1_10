# PROJECT_STATE (persistent checkpoint — update after every significant stage)

Last update: 2026-11-15 (session 1)

## Selected target journal
Analytica Chimica Acta (Elsevier). Median measured submission→acceptance 60.5 d (n=300), 90.3% <= 100 d.
See journal_selection/selected_journal.md.

## Constraints discovered
- Compute: 4 CPU cores, 15 GB RAM, no GPU; ~31 GB free disk.
- Network: Crossref, PubMed/Europe PMC, arXiv, Zenodo, UCI, OpenML, PyPI reachable; ScienceDirect/ACS/T&F/IEEE pages blocked to automated access.
- Topic domain constraint: project deliberately avoids toxicology / hazardous-chemistry / molecular property prediction.

## Data acquired (checksummed, data/MANIFEST.json)
- mango_v3 (12,011 spectra; Anderson 2020 benchmark sets Cal/Tuning/Val Ext/Val Ext 2), mango_v4 (85,401 spectra; 7 seasons
  2015-2021; 31 instrument units; 13,953 fruit IDs; fruits scanned on up to 11 units; temperature subset; outlier flags),
  CC BY 4.0, doi:10.17632/46htwnp833 (publisher SHA-256 verified). Authors warn: no random splits (replicate leakage).
- corn (80 x 700, 3 instruments, 4 properties), tablets (655 x 650, 2 instruments, weight/hardness/assay),
  diesel (784 x 401, 7 properties, property-specific subsets). Eigenvector; no explicit licence stated.
- OSSL available on GCS (ossl_all_L1_v1.2.csv.gz 622 MB) if needed.

## Infrastructure built (code/)
- utils (seed, device, config, io/provenance, log), statistics/inference.py (bootstrap, Wilcoxon+r, sign-flip,
  Holm/BH, Clopper-Pearson, McNemar), visualization/style.py (validated palette, Elsevier sizes),
  data/registry+download+loaders, preprocessing/spectral.py, models/pls.py (fast PLS1, all-LV CV), evaluation/metrics.py.
- 14 unit tests pass. Pipeline validation: PLS on mango v3 Anderson split -> RMSEP 1.05 %DM (13 LV, 1-SE rule).
- manuscript/tools: pandoc 3.1.3, elsevier-with-titles.csl (ACA dependent style parent), reference_elsevier.docx.

## Running workflows
- topic-discovery-aca (wf_a38edf5a-8d5): 7 generators -> 21 stress tests -> 3 judges.
- aca-journal-benchmark (wf_9f0b2565-3f9): 30 ACA papers, 18-item template + synthesis.

## Status
- [x] Phase 0 journal selection (117 journals measured)
- [ ] Phase 1–4 topic discovery & novelty defence  <-- NEXT
- [ ] Phases 5–20 experiments
- [ ] Phases 21–23 manuscript
- [ ] Review cycles (10 agents x 10 cycles)
- [ ] Final packaging

## Topic-discovery findings so far
- See literature/prior_art_notes.md. Label-free conformal NIR intervals under shift are PRE-EMPTED by Talanta 2026 (likely the user's own paper).
- Data hosts reachable: Mendeley Data, Eigenvector, ucphchemometrics.com, soilspectroscopy.org, Zenodo, figshare, Dryad, OSF, UCI, HF, GitHub. Not: Kaggle, models.life.ku.dk.

## Exact next step
Run topic-discovery workflow (7 sub-domain generators x 3 candidates -> adversarial stress test each -> 3-judge panel), then select ONE topic.
