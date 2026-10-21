import io, os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import xhtml2pdf.context as c
from xhtml2pdf import pisa
import pymupdf

font_reg = os.path.abspath('media/templates/offer_letter/default-c43d595d/fonts/Poppins-Regular.ttf')
font_bold = os.path.abspath('media/templates/offer_letter/default-c43d595d/fonts/Poppins-Bold.ttf')

pdfmetrics.registerFont(TTFont('Poppins', font_reg))
pdfmetrics.registerFont(TTFont('Poppins-Bold', font_bold))
c.addMapping('poppins', 0, 0, 'Poppins')
c.addMapping('poppins', 1, 0, 'Poppins-Bold')
c.addMapping('poppins', 0, 1, 'Poppins')
c.addMapping('poppins', 1, 1, 'Poppins-Bold')

orig_init = c.pisaContext.__init__
def custom_init(self, *args, **kwargs):
    orig_init(self, *args, **kwargs)
    self.fontList['poppins'] = 'Poppins'

c.pisaContext.__init__ = custom_init

def test_config(pad_top, pad_bottom, body_font, body_lh, terms_pad, terms_li_mb, accept_pad, label):
    sig_path = os.path.abspath('media/templates/offer_letter/default-c43d595d/img/signature.png').replace('\\', '/')
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @page {{
    size: A4 portrait;
    margin: 6mm 8mm 6mm 8mm;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  html, body {{
    margin: 0;
    padding: 0;
    background: #ffffff;
    font-family: 'Poppins', sans-serif;
    color: #1f2937;
    font-size: {body_font}px;
    line-height: {body_lh};
  }}

  .page-wrap {{
    width: 100%;
    margin: 0 auto;
    padding: 0;
  }}

  .letter {{
    width: 100%;
    background: #ffffff;
  }}

  .letter-table {{
    width: 100%;
    border-collapse: collapse;
  }}

  /* Left-side vertical strip: ONLY RED */
  .strip-red {{
    width: 18px;
    background-color: #bb0004;
    padding: 0;
    margin: 0;
    vertical-align: top;
  }}

  .content-cell {{
    vertical-align: top;
    padding: {pad_top}px 44px {pad_bottom}px 40px;
    background: #ffffff;
  }}

  /* Header */
  .header-block {{
    text-align: center;
    padding-bottom: 16px;
    margin-bottom: 20px;
    border-bottom: 2.5px solid #bb0004;
  }}

  .org-title {{
    font-size: 20px;
    font-weight: bold;
    color: #151c27;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 5px;
  }}

  .doc-title {{
    font-size: 14.5px;
    font-weight: bold;
    color: #bb0004;
    letter-spacing: 2.5px;
    text-transform: uppercase;
  }}

  /* Meta / Recipient */
  .meta-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 18px;
    font-size: {body_font}px;
    line-height: 1.6;
  }}

  .meta-table td {{
    vertical-align: top;
    padding: 3px 0;
  }}

  .subject-bar {{
    background-color: #fef2f2;
    border-left: 4.5px solid #bb0004;
    padding: 10px 16px;
    font-weight: bold;
    font-size: {body_font + 0.5}px;
    color: #151c27;
    margin: 18px 0 20px 0;
    letter-spacing: 0.2px;
  }}

  .salutation {{
    font-size: {body_font + 0.5}px;
    font-weight: bold;
    color: #151c27;
    margin-bottom: 14px;
  }}

  p.body-p {{
    font-size: {body_font}px;
    line-height: {body_lh};
    margin-bottom: 14px;
    color: #374151;
    text-align: justify;
  }}

  /* Terms and Conditions */
  .terms-section {{
    margin: 18px 0;
    padding: {terms_pad}px 18px;
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
  }}

  .terms-heading {{
    font-size: 12.5px;
    font-weight: bold;
    color: #bb0004;
    letter-spacing: 0.8px;
    margin-bottom: 10px;
    text-transform: uppercase;
  }}

  .terms-list {{
    margin: 0;
    padding-left: 20px;
    font-size: {body_font - 0.5}px;
    line-height: 1.55;
    color: #374151;
  }}

  .terms-list li {{
    margin-bottom: {terms_li_mb}px;
    text-align: justify;
  }}

  /* Closing & Signature */
  .sign-table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 16px;
  }}

  .sign-table td {{
    vertical-align: top;
  }}

  .sig-img {{
    height: 52px;
    display: block;
    margin: 5px 0 4px 0;
  }}

  .sig-name {{
    font-size: 13px;
    font-weight: bold;
    color: #151c27;
  }}

  .sig-company {{
    font-size: 12px;
    font-weight: bold;
    color: #151c27;
    margin-top: 2px;
  }}

  .sig-web {{
    font-size: 11.5px;
    color: #64748b;
    margin-top: 2px;
  }}

  .sig-web a {{
    color: #bb0004;
    text-decoration: none;
    font-weight: bold;
  }}

  /* Candidate Acceptance Box */
  .acceptance-box {{
    margin-top: 20px;
    padding: {accept_pad}px 18px;
    background-color: #f8fafc;
    border: 1.5px solid #cbd5e1;
    border-radius: 4px;
  }}

  .acceptance-title {{
    font-size: 12px;
    font-weight: bold;
    color: #151c27;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
    text-transform: uppercase;
  }}

  .acceptance-text {{
    font-size: 11.5px;
    color: #475569;
    font-style: italic;
    margin-bottom: 12px;
    line-height: 1.5;
  }}

  .acceptance-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
  }}

  .acceptance-table td {{
    padding-top: 4px;
  }}
</style>
</head>
<body>

  <div class="page-wrap">
    <div class="letter">
      <table class="letter-table" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td class="strip-red">&nbsp;</td>
          <td class="content-cell">
            <div class="header-block">
              <div class="org-title">REDBACK IT SOLUTIONS PRIVATE LIMITED</div>
              <div class="doc-title">INTERNSHIP OFFER LETTER</div>
            </div>

            <table class="meta-table">
              <tr>
                <td style="width: 55%;">
                  <strong>Offer ID:</strong> RB-INT-2026-0001
                </td>
                <td style="text-align: right; width: 45%;">
                  <strong>Date:</strong> 21/10/2026
                </td>
              </tr>
              <tr>
                <td style="padding-top: 4px;">
                  <strong>To:</strong> John Doe
                </td>
                <td style="text-align: right; padding-top: 4px;">
                  <strong>College / University:</strong> Stanford University
                </td>
              </tr>
            </table>

            <div class="subject-bar">
              Subject: Offer of Internship &ndash; Full Stack Web Development
            </div>

            <div class="salutation">Dear John Doe,</div>

            <p class="body-p">
              We are pleased to offer you an opportunity to participate in the Internship Programme at <strong>Redback IT Solutions Private Limited</strong> in the domain of <strong>Full Stack Web Development</strong>.
            </p>

            <p class="body-p">
              This programme is designed to enhance your technical knowledge and practical skills through structured learning, hands-on assignments, project development, and guidance relevant to your selected domain.
            </p>

            <div class="terms-section">
              <div class="terms-heading">TERMS AND CONDITIONS</div>
              <ol class="terms-list">
                <li>The intern is expected to complete assigned learning activities, practical tasks, and project submissions within the specified timelines.</li>
                <li>The intern must maintain professional conduct, submit original work, and follow programme guidelines.</li>
                <li>Confidential company information and internal project materials must not be disclosed without authorization.</li>
                <li>An internship completion certificate may be issued upon fulfilling the applicable programme requirements and evaluation criteria.</li>
                <li>Any applicable programme fees, stipend, or financial terms will be communicated separately and confirmed in writing.</li>
              </ol>
            </div>

            <p class="body-p">
              We welcome you to our internship programme and look forward to supporting your technical learning and professional development. Please confirm your acceptance through the official internship portal.
            </p>

            <table class="sign-table">
              <tr>
                <td>
                  <div style="font-size: 12.5px; margin-bottom: 2px;">Sincerely,</div>
                  <img class="sig-img" src="{sig_path}" alt="Signature">
                  <div class="sig-name">Program Director</div>
                  <div class="sig-company">Redback IT Solutions Private Limited</div>
                  <div class="sig-web">Website: <a href="https://redback.in">https://redback.in</a></div>
                </td>
              </tr>
            </table>

            <div class="acceptance-box">
              <div class="acceptance-title">CANDIDATE ACCEPTANCE</div>
              <div class="acceptance-text">
                I acknowledge this offer and agree to comply with the applicable internship programme terms and conditions.
              </div>
              <table class="acceptance-table">
                <tr>
                  <td style="width: 55%;">
                    <strong>Student Name:</strong> John Doe
                  </td>
                  <td style="text-align: right; width: 45%;">
                    <strong>Date:</strong> 21/10/2026
                  </td>
                </tr>
              </table>
            </div>

          </td>
        </tr>
      </table>
    </div>
  </div>

</body>
</html>
"""

    buf = io.BytesIO()
    pisa.CreatePDF(html, dest=buf)
    doc = pymupdf.open(stream=buf.getvalue(), filetype='pdf')
    num_p = len(doc)
    print(f"[{label}] pad_top={pad_top}, body_font={body_font}, terms_li_mb={terms_li_mb} => Pages: {num_p}")
    pix = doc[0].get_pixmap(dpi=150)
    out_img = f"scratch/test_spacing_{label}.png"
    pix.save(out_img)
    print(f"Saved {out_img}")
    return num_p

test_config(pad_top=36, pad_bottom=28, body_font=12.5, body_lh=1.6, terms_pad=12, terms_li_mb=5, accept_pad=12, label="c1")
test_config(pad_top=44, pad_bottom=34, body_font=13, body_lh=1.65, terms_pad=14, terms_li_mb=7, accept_pad=14, label="c2")
test_config(pad_top=48, pad_bottom=38, body_font=13.5, body_lh=1.68, terms_pad=15, terms_li_mb=8, accept_pad=15, label="c3")
