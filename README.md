# Fleet calibration of handheld NIR spectrometers

Code, results and manuscript for *"Fleet calibration of handheld near-infrared spectrometers: label-free prediction and minimisation of the error on instrument units never seen in calibration"* (P N Bhargav Teja et al.), prepared for *Analytica Chimica Acta*.

| Folder | Content |
|---|---|
| `code/` | Method (`src/fleet`), PLS and pre-processing, experiment and figure scripts (`scripts/`), unit tests (`tests/`) |
| `data/` | `MANIFEST.json`; raw data are public and re-downloaded with `cd code && python -m src.data.download` |
| `results/` | Per-run CSVs and summaries (`summary_v3/` is the version reported in the paper) |
| `manuscript/` | Section sources, figures, `build.py` (DOCX) and `package.py` (submission package) |
| `submission/` | `ACA_submission.zip` - files to upload to Editorial Manager |
| `journal_selection/`, `literature/` | Journal choice and literature/reference records |

Rebuild: `cd manuscript && python build.py && python package.py`.
