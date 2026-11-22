"""Assemble the manuscript (Markdown -> DOCX) with numbered Elsevier references from verified Crossref metadata."""
import json, re, subprocess
from pathlib import Path
H = Path(__file__).parent
refs = json.load(open(H / '../literature/references_verified.json'))
csl = []
for r in refs:
    year = r['year']
    m = re.search(r'print (?:issue|year) is (\d{4})', r.get('note') or '')
    if m:
        year = int(m.group(1))
    auth = []
    for a in r['authors']:
        parts = a.strip().split(' ')
        if len(parts) >= 2 and parts[-1].isupper() and len(parts[-1]) <= 4:
            auth.append({'family': ' '.join(parts[:-1]), 'given': '.'.join(parts[-1]) + '.'})
        else:
            auth.append({'literal': a})
    pages = r.get('pages_or_article_number') or ''
    j = r.get('journal') or ''
    typ = 'dataset' if any(t in j for t in ('Zenodo', 'Mendeley')) else ('standard' if 'ASTM' in j or 'Bureau' in j else 'article-journal')
    csl.append({'id': r['key'], 'type': typ, 'author': auth, 'title': r['title'], 'container-title': j,
                'issued': {'date-parts': [[int(year)]]}, 'volume': r.get('volume') or None, 'issue': r.get('issue') or None,
                'page': pages if '-' in pages else None, 'number': None if '-' in pages else (pages or None), 'DOI': r['doi']})
csl = [{k: v for k, v in c.items() if v is not None} for c in csl]
json.dump(csl, open(H / 'references.json', 'w'), indent=1, ensure_ascii=False)
order = ['00_front.md', '01_intro.md', '02_theory.md', '03_methods.md', '04_results.md', '04b_table1.md', '05_conclusion.md',
         '06_backmatter.md', '07_figures.md']
text = '\n\n'.join((H / 'sections' / f).read_text() for f in order if (H / 'sections' / f).exists())
text += '\n\n## References\n\n::: {#refs}\n:::\n'
(H / 'manuscript.md').write_text(text)
cmd = ['pandoc', str(H / 'manuscript.md'), '--citeproc', '--bibliography', str(H / 'references.json'), '--csl',
       str(H / 'tools/elsevier-with-titles.csl'), '--reference-doc', str(H / 'tools/reference_elsevier.docx'),
       '-o', str(H / 'manuscript.docx'), '--resource-path', str(H)]
subprocess.run(cmd, check=True)
# supplementary
subprocess.run(['pandoc', str(H / 'sections/S1_derivation.md'), '--reference-doc', str(H / 'tools/reference_elsevier.docx'),
                '-o', str(H / 'supplementary.docx')], check=True)
missing = sorted(set(re.findall(r'@([A-Za-z0-9]+)', text)) - {r['key'] for r in refs})
print('missing citation keys:', missing)
print('cited:', len(set(re.findall(r'@([A-Za-z0-9]+)', text)) & {r['key'] for r in refs}))
