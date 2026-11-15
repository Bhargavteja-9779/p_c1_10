# PROJECT_STATE (persistent checkpoint — update after every significant stage)

Last update: 2026-11-15 (session 1)

## Selected target journal
Analytica Chimica Acta (Elsevier). Median measured submission→acceptance 60.5 d (n=300), 90.3% <= 100 d.
See journal_selection/selected_journal.md.

## Constraints discovered
- Compute: 4 CPU cores, 15 GB RAM, no GPU; ~31 GB free disk.
- Network: Crossref, PubMed/Europe PMC, arXiv, Zenodo, UCI, OpenML, PyPI reachable; ScienceDirect/ACS/T&F/IEEE pages blocked to automated access.
- Topic domain constraint: project deliberately avoids toxicology / hazardous-chemistry / molecular property prediction.

## Status
- [x] Phase 0 journal selection (117 journals measured)
- [ ] Phase 1–4 topic discovery & novelty defence  <-- NEXT
- [ ] Phases 5–20 experiments
- [ ] Phases 21–23 manuscript
- [ ] Review cycles (10 agents x 10 cycles)
- [ ] Final packaging

## Exact next step
Literature search on uncertainty quantification / conformal prediction / calibration maintenance in
multivariate (NIR) calibration under domain shift; generate >= 15 candidate directions; stress test.
