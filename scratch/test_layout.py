import fitz, io, os
from xhtml2pdf import pisa

html = '''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page { size: A4 landscape; margin: 8mm; }
  * { margin:0; padding:0; }
  body {
    font-family: 'DejaVu Sans', Arial, sans-serif;
    background: #faf8f5;
    color: #2f2f2f;
    width: 100%;
  }
  .sheet { width: 100%; padding: 18px; background: #faf8f5; }
  .frame-table { width: 100%; border-collapse: collapse; }
  .frame-cell { border: 3px solid #535353; padding: 24px 45px 18px; text-align: center; background: #ffffff; }
  .footer-table { width: 100%; margin-top: 25px; }
  .footer-table td { vertical-align: bottom; text-align: center; }
</style>
</head>
<body>
<div class="sheet">
<table class="frame-table"><tr><td class="frame-cell">
  <div style="height: 380px;">Content above footer</div>

  <table class="footer-table" style="width: 100%;">
    <tr>
      <!-- Column 1: QR Code block -->
      <td style="width: 25%; text-align: center; vertical-align: bottom; padding: 0 10px;">
        <div style="font-size: 11px; font-weight: bold; color: #151c27; margin-bottom: 6px; text-align: center;">
          CRET NO : CRT-7264678C48
        </div>
        <div style="text-align: center;">
          <img src="media/templates/certificate/default-cfe8f3a2/img/redbackOG.png" width="72" height="72" style="border: 1px solid #c8c2b5; padding: 3px; background: #ffffff;">
        </div>
        <div style="font-size: 10px; color: #8a8a86; margin-top: 4px; text-align: center;">
          Scan to Verify
        </div>
      </td>

      <!-- Column 2: Spacer -->
      <td style="width: 5%;"></td>

      <!-- Column 3: Program Director Signature -->
      <td style="width: 36%; text-align: center; vertical-align: bottom; padding: 0 25px;">
        <div style="text-align: center; padding-bottom: 4px;">
          <img src="media/templates/certificate/default-cfe8f3a2/img/sivapriya mam sign-01.png" style="height: 60px;">
        </div>
        <div style="border-top: 1px solid #535353; padding-top: 5px; font-size: 11px; color: #8a8a86; text-align: center;">
          Program Director
        </div>
      </td>

      <!-- Column 4: Spacer -->
      <td style="width: 5%;"></td>

      <!-- Column 5: Date of Issued -->
      <td style="width: 29%; text-align: center; vertical-align: bottom; padding: 0 25px;">
        <div style="font-size: 13.5px; font-weight: 600; padding-bottom: 8px; text-align: center;">
          08 September 2026
        </div>
        <div style="border-top: 1px solid #535353; padding-top: 5px; font-size: 11px; color: #8a8a86; text-align: center;">
          Date of Issued
        </div>
      </td>
    </tr>
  </table>

  <div style="font-size: 10.5px; color: #8a8a86; margin-top: 18px;">
    Intern ID: RBS/INT/623037 &nbsp;&middot;&nbsp; Verify at https://redback.org/verify &nbsp;&middot;&nbsp; Scan QR to Verify
  </div>

</td></tr></table>
</div>
</body>
</html>
'''

out = io.BytesIO()
pisa.CreatePDF(html, dest=out)
doc = fitz.open(stream=out.getvalue(), filetype='pdf')
pix = doc[0].get_pixmap(dpi=150)
os.makedirs('scratch', exist_ok=True)
pix.save('scratch/test_layout_v4.png')
print('Saved scratch/test_layout_v4.png')
