import io, os
from xhtml2pdf import pisa
import pymupdf

font_reg = os.path.abspath('media/templates/offer_letter/default-c43d595d/fonts/Poppins-Regular.ttf').replace('\\', '/')
font_bold = os.path.abspath('media/templates/offer_letter/default-c43d595d/fonts/Poppins-Bold.ttf').replace('\\', '/')

html = f"""<!DOCTYPE html><html><head><style>
@page {{ size: A4 portrait; margin: 8mm; }}
@font-face {{
    font-family: Poppins;
    src: url('{font_reg}');
}}
@font-face {{
    font-family: Poppins;
    src: url('{font_bold}');
    font-weight: bold;
}}
body {{ font-family: Poppins, sans-serif; font-size: 14px; }}
h1 {{ font-family: Poppins, sans-serif; font-weight: bold; color: red; }}
</style></head><body><h1>REDBACK IT SOLUTIONS</h1><p>Testing Poppins regular and <b>bold text</b>.</p></body></html>"""

buf = io.BytesIO()
pisa.CreatePDF(html, dest=buf)
doc = pymupdf.open(stream=buf.getvalue(), filetype='pdf')
print('Page count:', len(doc))
for f in doc[0].get_fonts():
    print('Font in PDF:', f)
pix = doc[0].get_pixmap(dpi=150)
pix.save('scratch/poppins_test.png')
print('Saved poppins_test.png!')
