import io, pymupdf
from xhtml2pdf import pisa

def test_layout(body_font_size, line_height, pad_top, spacing_terms, strip_height="100%"):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Internship Offer Letter &mdash; John Doe</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 8mm 10mm 8mm 10mm;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  html, body {{
    margin: 0;
    padding: 0;
    background: #e9edf1;
    font-family: 'DejaVu Sans', Arial, Helvetica, sans-serif;
    color: #1f2937;
    font-size: {body_font_size}px;
    line-height: {line_height};
  }}

  .page-wrap {{
    display: flex;
    justify-content: center;
    padding: 24px 16px;
  }}

  .letter {{
    width: 100%;
    max-width: 820px;
    min-height: 1140px;
    background: #ffffff;
    box-shadow: 0 8px 30px rgba(21, 28, 39, 0.12);
    overflow: hidden;
    border-radius: 4px;
  }}

  .letter-table {{
    width: 100%;
    border-collapse: collapse;
    background: #ffffff;
  }}

  /* Left-side vertical strip: ONLY RED */
  .strip-red {{
    width: 16px;
    background-color: #bb0004;
    padding: 0;
    margin: 0;
    vertical-align: top;
  }}

  .content-cell {{
    vertical-align: top;
    padding: {pad_top}px 48px 24px 44px;
    background: #ffffff;
  }}

  /* Header without images */
  .header-block {{
    text-align: center;
    padding-bottom: 14px;
    margin-bottom: 18px;
    border-bottom: 2px solid #bb0004;
  }}

  .org-title {{
    font-family: 'DejaVu Sans', Arial, Helvetica, sans-serif;
    font-size: 19px;
    font-weight: bold;
    color: #151c27;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 4px;
  }}

  .doc-title {{
    font-family: 'DejaVu Sans', Arial, Helvetica, sans-serif;
    font-size: 14px;
    font-weight: bold;
    color: #bb0004;
    letter-spacing: 2px;
    text-transform: uppercase;
  }}

  /* Meta / Recipient */
  .meta-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 16px;
    font-size: 12px;
    line-height: 1.6;
  }}

  .meta-table td {{
    vertical-align: top;
    padding: 2px 0;
  }}

  .subject-bar {{
    background-color: #fef2f2;
    border-left: 4px solid #bb0004;
    padding: 9px 14px;
    font-weight: bold;
    font-size: 13px;
    color: #151c27;
    margin: 16px 0 18px 0;
    letter-spacing: 0.2px;
  }}

  .salutation {{
    font-size: 13px;
    font-weight: bold;
    color: #151c27;
    margin-bottom: 12px;
  }}

  p.body-p {{
    font-size: 12px;
    line-height: 1.6;
    margin-bottom: 12px;
    color: #374151;
    text-align: justify;
  }}

  /* Terms and Conditions */
  .terms-section {{
    margin: 16px 0;
    padding: 12px 16px;
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
  }}

  .terms-heading {{
    font-family: 'DejaVu Sans', Arial, Helvetica, sans-serif;
    font-size: 12px;
    font-weight: bold;
    color: #bb0004;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
    text-transform: uppercase;
  }}

  .terms-list {{
    margin: 0;
    padding-left: 18px;
    font-size: 11px;
    line-height: 1.55;
    color: #374151;
  }}

  .terms-list li {{
    margin-bottom: {spacing_terms}px;
    text-align: justify;
  }}

  /* Closing & Signature */
  .sign-table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 14px;
  }}

  .sign-table td {{
    vertical-align: top;
  }}

  .sig-img {{
    height: 48px;
    display: block;
    margin: 4px 0 3px 0;
  }}

  .sig-name {{
    font-size: 12.5px;
    font-weight: bold;
    color: #151c27;
  }}

  .sig-company {{
    font-size: 11.5px;
    font-weight: bold;
    color: #151c27;
    margin-top: 2px;
  }}

  .sig-web {{
    font-size: 11px;
    color: #64748b;
    margin-top: 2px;
  }}

  .sig-web a {{
    color: #bb0004;
    text-decoration: none;
    font-weight: 600;
  }}

  /* Candidate Acceptance Box */
  .acceptance-box {{
    margin-top: 18px;
    padding: 12px 16px;
    background-color: #f8fafc;
    border: 1.5px solid #cbd5e1;
    border-radius: 4px;
  }}

  .acceptance-title {{
    font-family: 'DejaVu Sans', Arial, Helvetica, sans-serif;
    font-size: 11.5px;
    font-weight: bold;
    color: #151c27;
    letter-spacing: 0.8px;
    margin-bottom: 5px;
    text-transform: uppercase;
  }}

  .acceptance-text {{
    font-size: 11px;
    color: #475569;
    font-style: italic;
    margin-bottom: 10px;
    line-height: 1.5;
  }}

  .acceptance-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 11.5px;
  }}

  .acceptance-table td {{
    padding-top: 4px;
  }}

  @media print {{
    body {{ background: #ffffff !important; }}
    .page-wrap {{ padding: 0 !important; }}
    .letter {{ box-shadow: none !important; border-radius: 0 !important; max-width: 100% !important; }}
  }}
</style>
</head>
<body>

  <div class="page-wrap">
    <div class="letter" id="letter">

      <table class="letter-table" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <!-- Left side decorative strip: ONLY RED -->
          <td class="strip-red">&nbsp;</td>

          <!-- Main letter content -->
          <td class="content-cell">

            <!-- Header without images -->
            <div class="header-block">
              <div class="org-title">REDBACK IT SOLUTIONS PRIVATE LIMITED</div>
              <div class="doc-title">INTERNSHIP OFFER LETTER</div>
            </div>

            <!-- Meta Information Table -->
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

            <!-- Subject -->
            <div class="subject-bar">
              Subject: Offer of Internship &ndash; Full Stack Development
            </div>

            <!-- Salutation -->
            <div class="salutation">Dear John Doe,</div>

            <!-- Body Paragraphs -->
            <p class="body-p">
              We are pleased to offer you an opportunity to participate in the Internship Programme at <strong>Redback IT Solutions Private Limited</strong> in the domain of <strong>Full Stack Development</strong>.
            </p>

            <p class="body-p">
              This programme is designed to enhance your technical knowledge and practical skills through structured learning, hands-on assignments, project development, and guidance relevant to your selected domain.
            </p>

            <!-- Terms and Conditions -->
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

            <!-- Signature & Sign-off -->
            <table class="sign-table">
              <tr>
                <td>
                  <div style="font-size: 12px; margin-bottom: 2px;">Sincerely,</div>
                  <img class="sig-img" src="media/templates/offer_letter/default-c43d595d/img/signature.png" alt="Program Director Signature">
                  <div class="sig-name">Program Director</div>
                  <div class="sig-company">Redback IT Solutions Private Limited</div>
                  <div class="sig-web">Website: <a href="https://redback.in">https://redback.in</a></div>
                </td>
              </tr>
            </table>

            <!-- Candidate Acceptance -->
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
</html>"""

    out = io.BytesIO()
    pisa.CreatePDF(html, dest=out)
    doc = pymupdf.open(stream=out.getvalue(), filetype='pdf')
    print(f"Params: font={body_font_size}, pad={pad_top}, terms_sp={spacing_terms} => Pages: {len(doc)}")
    pix = doc[0].get_pixmap(dpi=150)
    pix.save(f"scratch/uncompressed_test_{body_font_size}_{pad_top}.png")
    return len(doc)

test_layout(12, 1.55, 36, 4)
test_layout(11.5, 1.5, 32, 3)
