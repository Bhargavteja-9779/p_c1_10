# Manuscript sources

- `sections/*.md` - manuscript text (`S1_derivation.md` = supplementary material)
- `figures/` - Fig. 1-6 (PDF/PNG/TIFF, 600 dpi) and CSV of plotted values
- `cover_letter.md`, `submission_form_entries.txt`
- `build.py` - Markdown -> `manuscript.docx`, `supplementary.docx` (pandoc, Elsevier numbered references)
- `package.py` - builds `../submission/ACA_submission.zip`

Still to complete before upload: second author's name, affiliation and CRediT roles (`[Second Author]` in `sections/00_front.md` and `sections/06_backmatter.md`), then rerun both scripts.
