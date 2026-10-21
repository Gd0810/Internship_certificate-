import io, pymupdf
from xhtml2pdf import pisa

def test_render(filename, strip_html, strip_css):
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: A4 portrait;
    margin: 8mm 10mm 8mm 10mm;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: Arial, Helvetica, sans-serif;
    color: #26313c;
    background: #ffffff;
    font-size: 13.5px;
    line-height: 1.6;
  }}
  .letter-table {{
    width: 100%;
    border-collapse: collapse;
  }}
  {strip_css}
  .content {{
    padding: 36px 44px 30px 40px;
    vertical-align: top;
  }}
  .org-name {{
    font-size: 19px;
    font-weight: bold;
    color: #151c27;
    margin-bottom: 24px;
  }}
  h1.title {{
    font-size: 32px;
    font-weight: bold;
    color: #bb0004;
    margin: 0 0 24px;
    letter-spacing: 0.5px;
  }}
  .meta-block {{
    font-size: 13px;
    line-height: 1.6;
    margin-bottom: 20px;
    color: #475569;
  }}
  .subject {{
    font-size: 13.5px;
    font-weight: bold;
    color: #151c27;
    margin-bottom: 18px;
    padding: 8px 12px;
    background-color: #fef2f2;
    border-left: 3px solid #bb0004;
  }}
  .salutation {{
    font-size: 13.5px;
    font-weight: bold;
    margin-bottom: 14px;
    color: #151c27;
  }}
  p.body-text {{
    font-size: 13px;
    line-height: 1.65;
    margin: 0 0 16px;
    text-align: justify;
    color: #334155;
  }}
  .highlight {{
    font-weight: bold;
    color: #bb0004;
  }}
  .signature-block {{
    margin-top: 24px;
  }}
  .sig-name {{
    font-size: 14px;
    font-weight: bold;
    color: #151c27;
  }}
  .sig-role {{
    font-size: 12px;
    color: #64748b;
  }}
  .doc-footer {{
    margin-top: 28px;
    padding-top: 14px;
    border-top: 1px solid #e2e8f0;
    font-size: 11px;
    color: #64748b;
  }}
</style>
</head>
<body>
  <table class="letter-table" cellpadding="0" cellspacing="0">
    <tr>
      {strip_html}
      <td class="content">
        <table style="width: 100%; margin-bottom: 18px;">
          <tr>
            <td style="width: 50px; vertical-align: middle;">
              <img src="media/templates/offer_letter/default-seed/img/logo.png" style="width: 44px; height: 44px;" alt="Logo">
            </td>
            <td style="vertical-align: middle; padding-left: 14px;">
              <div class="org-name" style="margin-bottom: 0;">REDBACK IT SOLUTIONS</div>
              <div style="font-size: 11px; color: #64748b; font-weight: 600; letter-spacing: 1px;">OFFICIAL INTERNSHIP PROGRAM</div>
            </td>
          </tr>
        </table>

        <h1 class="title">Offer Letter</h1>

        <div class="meta-block">
          <strong>Date:</strong> 08 September 2026<br>
          <strong>Intern ID:</strong> RBS/INT/623037<br>
          <strong>Institution:</strong> Stanford University
        </div>

        <div class="subject">
          SUBJECT: OFFER OF INTERNSHIP &mdash; Full Stack Development
        </div>

        <div class="salutation">Dear John Doe,</div>

        <p class="body-text">
          We are pleased to extend an offer of internship for the <span class="highlight">Full Stack Development</span> program at Redback IT Solutions. Following the review of your academic background and profile from <strong>Stanford University</strong>, we are confident in your capabilities and enthusiasm to contribute to our technical initiatives.
        </p>

        <p class="body-text">
          During this internship, you will be engaged in practical project modules, code reviews, and industry-standard development workflows designed to build end-to-end expertise in modern software engineering.
        </p>

        <p class="body-text">
          We look forward to having you as part of our learning community and wish you a highly successful and productive internship journey.
        </p>

        <div style="margin-top: 18px; font-size: 13px;">Sincerely,</div>
        <div class="signature-block">
          <img src="media/templates/certificate/default-cfe8f3a2/img/sivapriya mam sign-01.png" style="height: 48px;" alt="Signature">
          <div class="sig-name">Program Director</div>
          <div class="sig-role">Redback IT Solutions Private Limited</div>
        </div>

        <table style="width: 100%; margin-top: 24px; padding-top: 12px; border-top: 1px solid #e2e8f0;">
          <tr>
            <td style="font-size: 11px; color: #64748b; vertical-align: middle;">
              Document ID: CRT-7264678C48 &nbsp;&bull;&nbsp; Verified Credential
            </td>
            <td style="text-align: right; width: 60px; vertical-align: middle;">
              <img src="media/templates/offer_letter/default-seed/img/seal.png" style="width: 50px; height: 50px;" alt="Seal">
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    out = io.BytesIO()
    pisa.CreatePDF(html, dest=out)
    doc = pymupdf.open(stream=out.getvalue(), filetype='pdf')
    print(f"{filename}: pages={len(doc)}")
    pix = doc[0].get_pixmap(dpi=150)
    pix.save(f"scratch/{filename}.png")

test_render(
    "strip_v1",
    """<td class="strip-red" style="width: 12px; background-color: #bb0004; padding: 0;">&nbsp;</td>
       <td class="strip-black" style="width: 5px; background-color: #151c27; padding: 0;">&nbsp;</td>""",
    ""
)

test_render(
    "strip_v2",
    """<td class="strip-composite" style="width: 16px; background-color: #bb0004; border-right: 4px solid #151c27; padding: 0;">&nbsp;</td>""",
    ""
)
