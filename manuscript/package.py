"""Build the Analytica Chimica Acta submission package (submission/ACA_submission.zip)."""
import shutil, subprocess, zipfile
from pathlib import Path
from PIL import Image
import docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

H = Path(__file__).parent
OUT = H.parent / 'submission' / 'ACA_submission'
shutil.rmtree(OUT, ignore_errors=True); OUT.mkdir(parents=True)
REF = str(H / 'tools/reference_elsevier.docx')
AUTHOR = 'P N Bhargav Teja'
front = (H / 'sections/00_front.md').read_text()
title = front.split('title: "')[1].split('"')[0]


def md2docx(md, out):
    src = OUT / '_tmp.md'; src.write_text(md)
    subprocess.run(['pandoc', str(src), '--reference-doc', REF, '-o', str(out), '--resource-path', str(H)], check=True)
    src.unlink()


def clean_meta(path, line_numbers=False):
    d = docx.Document(path)
    cp = d.core_properties
    cp.author = AUTHOR; cp.last_modified_by = AUTHOR; cp.comments = ''; cp.keywords = ''; cp.title = title
    if line_numbers:
        for s in d.sections:
            ln = OxmlElement('w:lnNumType')
            ln.set(qn('w:countBy'), '1'); ln.set(qn('w:restart'), 'continuous'); ln.set(qn('w:distance'), '284')
            s._sectPr.append(ln)
    d.save(path)


# 1 manuscript (full, with line numbers) + PDF
shutil.copy(H / 'manuscript.docx', OUT / '01_Manuscript.docx'); clean_meta(OUT / '01_Manuscript.docx', True)
shutil.copy(H / 'supplementary.docx', OUT / '08_Supplementary_material.docx'); clean_meta(OUT / '08_Supplementary_material.docx')
# 2 title page
tp = front.split('## Highlights')[0]
tp += '\n**Declarations**\n\n' + (H / 'sections/06_backmatter.md').read_text().replace('## ', '### ')
md2docx(tp, OUT / '02_Title_page.docx'); clean_meta(OUT / '02_Title_page.docx')
# 3 highlights
hl = front.split('## Highlights')[1].split('## Graphical')[0]
md2docx('# Highlights\n' + hl, OUT / '03_Highlights.docx'); clean_meta(OUT / '03_Highlights.docx')
# 4 cover letter
md2docx((H / 'cover_letter.md').read_text(), OUT / '00_Cover_letter.docx'); clean_meta(OUT / '00_Cover_letter.docx')
# 5 declaration of interests
md2docx('# Declaration of interests\n\n**Manuscript title:** ' + title +
        '\n\n☒ The authors declare that they have no known competing financial interests or personal relationships '
        'that could have appeared to influence the work reported in this paper.\n\n'
        '☐ The authors declare the following financial interests/personal relationships which may be considered as '
        'potential competing interests:\n\n' + AUTHOR + ' (corresponding author), on behalf of all authors\n',
        OUT / '05_Declaration_of_interests.docx'); clean_meta(OUT / '05_Declaration_of_interests.docx')
# 6 figures: RGB TIFF 600 dpi, LZW; graphical abstract
figs = ['fig1_workflow', 'fig2_unit_risk', 'fig3_methods', 'fig4_design_curves', 'fig5_unit_effects', 'fig6_tau_curve']
for i, f in enumerate(figs, 1):
    im = Image.open(H / f'figures/{f}.tiff')
    bg = Image.new('RGB', im.size, 'white'); bg.paste(im, mask=im.split()[-1] if im.mode == 'RGBA' else None)
    bg.save(OUT / f'06_Figure_{i}.tif', dpi=(600, 600), compression='tiff_lzw')
    if i == 1:
        bg.save(OUT / '04_Graphical_abstract.tif', dpi=(600, 600), compression='tiff_lzw')
# 7 reference PDFs (HTML + MathML printed by headless Chromium; LibreOffice drops Word equations)
import glob, tempfile
CH = (glob.glob('/opt/pw-browsers/chromium-*/real/chrome-linux64/chrome') or ['chromium'])[0]
CSS = H / 'tools/pdf.css'
with tempfile.TemporaryDirectory() as td:
    for src, args, name in [(H / 'manuscript.md', ['--citeproc', '--bibliography', str(H / 'references.json'), '--csl',
                             str(H / 'tools/elsevier-with-titles.csl')], '01_Manuscript.pdf'),
                            (H / 'sections/S1_derivation.md', ['--metadata', 'title= ', '--metadata', 'pagetitle=Supplementary material'], '08_Supplementary_material.pdf')]:
        html = Path(td) / 'x.html'
        subprocess.run(['pandoc', str(src), *args, '--mathml', '-s', '--embed-resources', '--resource-path', str(H),
                        '--css', str(CSS), '-o', str(html)], check=True, capture_output=True)
        subprocess.run([CH, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                        f'--print-to-pdf={OUT / name}', str(html)], check=True, capture_output=True)
# 9 submission-system entries
shutil.copy(H / 'submission_form_entries.txt', OUT / '09_Submission_form_entries.txt')
z = OUT.parent / 'ACA_submission.zip'
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    for p in sorted(OUT.iterdir()):
        zf.write(p, f'ACA_submission/{p.name}')
print(z, z.stat().st_size // 1024, 'KB'); [print(' ', p.name) for p in sorted(OUT.iterdir())]
