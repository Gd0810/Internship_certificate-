import io, fitz
from xhtml2pdf import pisa

def test_approach(name, css, body_html):
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: A4 portrait;
    margin: 8mm 10mm 8mm 10mm;
  }}
  * {{ margin: 0; padding: 0; }}
  body {{
    font-family: Arial, Helvetica, sans-serif;
    color: #26313c;
    background: #ffffff;
  }}
  {css}
</style>
</head>
<body>
{body_html}
</body>
</html>"""
    out = io.BytesIO()
    pisa.CreatePDF(html, dest=out)
    doc = fitz.open(stream=out.getvalue(), filetype='pdf')
    pix = doc[0].get_pixmap(dpi=150)
    pix.save(f'scratch/{name}.png')
    print(f'{name}: pages={len(doc)}')

test_approach('appr1_table_full', """
.full-table {
  width: 100%;
}
.strip-red {
  width: 14px;
  background-color: #bb0004;
}
.strip-black {
  width: 6px;
  background-color: #151c27;
}
.content {
  padding: 20px 30px;
  vertical-align: top;
}
""", """
<table class="full-table" cellpadding="0" cellspacing="0">
  <tr>
    <td class="strip-red" style="height: 980px;">&nbsp;</td>
    <td class="strip-black" style="height: 980px;">&nbsp;</td>
    <td class="content">
      <h1 style="color: #bb0004;">Offer Letter</h1>
      <p>Body content here...</p>
    </td>
  </tr>
</table>
""")

test_approach('appr2_border', """
.letter-box {
  border-left: 14px solid #bb0004;
  padding-left: 28px;
  padding-top: 20px;
  min-height: 950px;
}
""", """
<div class="letter-box">
  <h1 style="color: #bb0004;">Offer Letter</h1>
  <p>Body content with border-left...</p>
</div>
""")
