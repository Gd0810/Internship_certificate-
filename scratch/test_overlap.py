import pymupdf as fitz
from xhtml2pdf import pisa
import io

badge_uri = r'c:\Users\redback\Downloads\credentia_internship_platform (1)\internproj\scratch\test_badge.png'.replace('\\', '/')

html = f"""<!doctype html>
<html>
<head>
<style>
  @page {{ size: A4 landscape; margin: 8mm; }}
  table {{ border-collapse: collapse; }}
</style>
</head>
<body>
  <table width='100%' style='border: 10px solid #151c27;'>
    <tr>
      <td style='border: 2px solid #bb0004; padding: 10px; background: #ffffff;'>
        <table width='100%'>
          <tr>
            <!-- Left Strip Column -->
            <td width='124' style='vertical-align: top; padding: 0;'>
              <table width='100%'>
                <tr>
                  <td style='text-align: center; padding: 0;'>
                    <table width='60' align='center'>
                      <tr>
                        <td style='background-color: #151c27; border-left: 2px solid #bb0004; border-right: 2px solid #bb0004; height: 135px;'>&nbsp;</td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td style='text-align: center; padding: 0;'>
                    <img src="{badge_uri}" width="116" height="116" style="width: 116px; height: 116px; display: block; margin: 0 auto;">
                  </td>
                </tr>
                <tr>
                  <td style='text-align: center; padding: 0;'>
                    <table width='60' align='center'>
                      <tr>
                        <td style='background-color: #151c27; border-left: 2px solid #bb0004; border-right: 2px solid #bb0004; height: 210px;'>&nbsp;</td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
            <!-- Right Content -->
            <td style='padding-left: 20px; vertical-align: top;'>
              <h1 style='text-align: center; margin-top: 40px;'>CERTIFICATE</h1>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
buf = io.BytesIO()
pisa.CreatePDF(html, dest=buf)
doc = fitz.open(stream=buf.getvalue(), filetype='pdf')
pix = doc[0].get_pixmap()
pix.save(r'c:\Users\redback\Downloads\credentia_internship_platform (1)\internproj\scratch\test_overlap_strip.png')
print('Saved test_overlap_strip.png, page count:', len(doc))
