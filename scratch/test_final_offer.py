import os, io, pymupdf
from xhtml2pdf import pisa

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Offer Letter &mdash; {{user_name}}</title>
<style>
  :root {
    --red: #bb0004;
    --dark-red: #8b0002;
    --black: #151c27;
    --text: #26313c;
    --muted: #5b6b78;
    --border: #e2e8f0;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  html, body {
    margin: 0;
    padding: 0;
    background: #e9edf1;
    font-family: Arial, Helvetica, sans-serif;
    color: #26313c;
  }

  .page-wrap {
    display: flex;
    justify-content: center;
    padding: 30px 16px;
  }

  .letter {
    width: 100%;
    max-width: 840px;
    background: #ffffff;
    box-shadow: 0 8px 30px rgba(21, 28, 39, 0.12);
    overflow: hidden;
    border-radius: 4px;
  }

  /* Two-column table layout: Left strip + Content */
  .letter-table {
    width: 100%;
    border-collapse: collapse;
    background: #ffffff;
  }

  .strip-red {
    width: 14px;
    background-color: #bb0004;
    padding: 0;
    margin: 0;
    vertical-align: top;
  }

  .strip-black {
    width: 5px;
    background-color: #151c27;
    padding: 0;
    margin: 0;
    vertical-align: top;
  }

  .content-cell {
    vertical-align: top;
    padding: 42px 52px 36px 46px;
    background: #ffffff;
  }

  .letterhead-table {
    width: 100%;
    margin-bottom: 24px;
    border-collapse: collapse;
  }

  .letterhead-table td {
    vertical-align: middle;
  }

  .logo-cell {
    width: 52px;
  }

  .logo-img {
    width: 46px;
    height: 46px;
    display: block;
  }

  .org-name {
    font-size: 20px;
    font-weight: bold;
    color: #151c27;
    line-height: 1.2;
    letter-spacing: 0.3px;
  }

  .org-sub {
    font-size: 11px;
    font-weight: 600;
    color: #64748b;
    letter-spacing: 1.2px;
    margin-top: 2px;
    text-transform: uppercase;
  }

  h1.title {
    font-size: 32px;
    color: #bb0004;
    margin: 0 0 22px;
    font-weight: bold;
    letter-spacing: 0.5px;
  }

  .meta-block {
    font-size: 13px;
    line-height: 1.65;
    margin-bottom: 18px;
    color: #475569;
  }

  .subject {
    font-weight: bold;
    margin-bottom: 18px;
    font-size: 13px;
    color: #151c27;
    padding: 8px 12px;
    background-color: #fef2f2;
    border-left: 3.5px solid #bb0004;
  }

  .salutation {
    margin-bottom: 14px;
    font-size: 13.5px;
    font-weight: bold;
    color: #151c27;
  }

  p.body-text {
    font-size: 13px;
    line-height: 1.65;
    margin: 0 0 14px;
    text-align: justify;
    color: #334155;
  }

  .highlight {
    font-weight: bold;
    color: #bb0004;
  }

  .closing {
    margin-top: 18px;
    font-size: 13px;
    color: #151c27;
  }

  .signature-block {
    margin-top: 8px;
  }

  .signature-block img.signature {
    height: 46px;
    display: block;
    margin-bottom: 4px;
  }

  .signature-name {
    font-size: 13.5px;
    font-weight: bold;
    color: #151c27;
  }

  .signature-role {
    font-size: 11.5px;
    color: #64748b;
  }

  .doc-footer-table {
    width: 100%;
    margin-top: 22px;
    padding-top: 14px;
    border-top: 1px solid #e2e8f0;
    border-collapse: collapse;
  }

  .doc-footer-table td {
    vertical-align: middle;
  }

  .footer-text {
    font-size: 11px;
    color: #64748b;
    letter-spacing: 0.2px;
  }

  .seal-img {
    width: 52px;
    height: 52px;
    display: block;
  }

  @media (max-width: 640px) {
    .content-cell { padding: 28px 20px 24px 20px; }
    h1.title { font-size: 26px; }
    .org-name { font-size: 17px; }
  }

  @media print {
    body { background: #ffffff !important; }
    .page-wrap { padding: 0 !important; }
    .letter { box-shadow: none !important; border-radius: 0 !important; max-width: 100% !important; }
  }
</style>
<style>
  @page {
    size: A4 portrait;
    margin: 6mm 8mm 6mm 8mm;
  }
</style>
</head>
<body>

  <div class="page-wrap">
    <div class="letter" id="letter">

      <table class="letter-table" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <!-- Left side decorative strip: Red and Black theme colors -->
          <td class="strip-red">&nbsp;</td>
          <td class="strip-black">&nbsp;</td>

          <!-- Main letter content -->
          <td class="content-cell">

            <!-- Letterhead -->
            <table class="letterhead-table">
              <tr>
                <td class="logo-cell">
                  <img class="logo-img" src="media/templates/offer_letter/default-seed/img/logo.png" alt="Logo">
                </td>
                <td style="padding-left: 14px;">
                  <div class="org-name">REDBACK IT SOLUTIONS</div>
                  <div class="org-sub">Official Internship Program</div>
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
              We are pleased to extend an offer of internship for the <span class="highlight">Full Stack Development</span> program at Redback IT Solutions. Following the review of your academic background and profile from <strong>Stanford University</strong>, we are confident in your technical aptitude and enthusiasm to contribute to our engineering initiatives.
            </p>

            <p class="body-text">
              During this internship, you will be engaged in practical project modules, code reviews, and industry-standard workflows designed to foster expertise in full-cycle software development.
            </p>

            <p class="body-text">
              We look forward to having you join our community and wish you a highly successful and productive internship journey.
            </p>

            <div class="closing">Sincerely,</div>
            <div class="signature-block">
              <img class="signature" src="media/templates/certificate/default-cfe8f3a2/img/sivapriya mam sign-01.png" alt="Signature">
              <div class="signature-name">Program Director</div>
              <div class="signature-role">Redback IT Solutions Private Limited</div>
            </div>

            <table class="doc-footer-table">
              <tr>
                <td class="footer-text">
                  Document ID: CRT-7264678C48 &nbsp;&bull;&nbsp; Verified Credential &nbsp;&bull;&nbsp; Redback Platform
                </td>
                <td style="text-align: right; width: 60px;">
                  <img class="seal-img" src="media/templates/offer_letter/default-seed/img/seal.png" alt="Official Seal">
                </td>
              </tr>
            </table>

          </td>
        </tr>
      </table>

    </div>
  </div>

</body>
</html>"""

out = io.BytesIO()
pisa.CreatePDF(html_template, dest=out)
doc = pymupdf.open(stream=out.getvalue(), filetype='pdf')
print(f"Pages: {len(doc)}")
pix = doc[0].get_pixmap(dpi=150)
pix.save("scratch/test_final_offer.png")
print("Saved scratch/test_final_offer.png")
