import os, io, pymupdf
from xhtml2pdf import pisa

html = """<!DOCTYPE html>
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
    --text: #1f2937;
    --muted: #4b5563;
    --border: #e5e7eb;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  html, body {
    margin: 0;
    padding: 0;
    background: #e9edf1;
    font-family: Arial, Helvetica, sans-serif;
    color: #1f2937;
    font-size: 11px;
    line-height: 1.45;
  }

  .page-wrap {
    display: flex;
    justify-content: center;
    padding: 24px 16px;
  }

  .letter {
    width: 100%;
    max-width: 820px;
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
    width: 12px;
    background-color: #bb0004;
    padding: 0;
    margin: 0;
    vertical-align: top;
  }

  .strip-black {
    width: 4px;
    background-color: #151c27;
    padding: 0;
    margin: 0;
    vertical-align: top;
  }

  .content-cell {
    vertical-align: top;
    padding: 28px 38px 24px 34px;
    background: #ffffff;
  }

  /* Header */
  .header-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1.5px solid #151c27;
  }

  .header-table td {
    vertical-align: middle;
  }

  .org-title {
    font-size: 15px;
    font-weight: bold;
    color: #151c27;
    letter-spacing: 0.8px;
  }

  .doc-title {
    font-size: 12px;
    font-weight: bold;
    color: #bb0004;
    letter-spacing: 1.2px;
    margin-top: 2px;
  }

  /* Meta / Recipient */
  .meta-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    font-size: 11px;
  }

  .meta-table td {
    vertical-align: top;
    padding: 1px 0;
  }

  .subject-bar {
    background-color: #fef2f2;
    border-left: 3.5px solid #bb0004;
    padding: 6px 10px;
    font-weight: bold;
    font-size: 11.5px;
    color: #151c27;
    margin: 10px 0 12px 0;
  }

  .salutation {
    font-size: 11.5px;
    font-weight: bold;
    color: #151c27;
    margin-bottom: 8px;
  }

  p.body-p {
    font-size: 10.5px;
    line-height: 1.45;
    margin-bottom: 8px;
    color: #374151;
    text-align: justify;
  }

  /* Terms and Conditions */
  .terms-section {
    margin: 10px 0 10px 0;
    padding: 8px 12px;
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
  }

  .terms-heading {
    font-size: 11px;
    font-weight: bold;
    color: #bb0004;
    letter-spacing: 0.5px;
    margin-bottom: 5px;
    text-transform: uppercase;
  }

  .terms-list {
    margin: 0;
    padding-left: 16px;
    font-size: 10px;
    line-height: 1.45;
    color: #374151;
  }

  .terms-list li {
    margin-bottom: 3px;
  }

  /* Closing & Signature */
  .sign-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 8px;
  }

  .sign-table td {
    vertical-align: top;
  }

  .sig-img {
    height: 38px;
    display: block;
    margin-bottom: 2px;
  }

  .sig-name {
    font-size: 11px;
    font-weight: bold;
    color: #151c27;
  }

  .sig-role {
    font-size: 10px;
    color: #4b5563;
  }

  .sig-company {
    font-size: 10.5px;
    font-weight: bold;
    color: #151c27;
  }

  .sig-web {
    font-size: 10px;
    color: #bb0004;
    text-decoration: none;
  }

  /* Candidate Acceptance Box */
  .acceptance-box {
    margin-top: 10px;
    padding: 8px 12px;
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
  }

  .acceptance-title {
    font-size: 10.5px;
    font-weight: bold;
    color: #151c27;
    letter-spacing: 0.5px;
    margin-bottom: 3px;
    text-transform: uppercase;
  }

  .acceptance-text {
    font-size: 10px;
    color: #475569;
    font-style: italic;
    margin-bottom: 6px;
  }

  .acceptance-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 10.5px;
  }

  .acceptance-table td {
    padding-top: 3px;
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

            <!-- Header -->
            <table class="header-table">
              <tr>
                <td style="width: 44px; vertical-align: middle;">
                  <img src="media/templates/offer_letter/default-c43d595d/img/logo.png" style="width: 38px; height: 38px; display: block;" alt="Redback Logo">
                </td>
                <td style="padding-left: 10px; vertical-align: middle;">
                  <div class="org-title">REDBACK IT SOLUTIONS PRIVATE LIMITED</div>
                  <div class="doc-title">INTERNSHIP OFFER LETTER</div>
                </td>
                <td style="text-align: right; width: 44px; vertical-align: middle;">
                  <img src="media/templates/offer_letter/default-c43d595d/img/seal.png" style="width: 38px; height: 38px; display: block;" alt="Seal">
                </td>
              </tr>
            </table>

            <!-- Meta Information Table -->
            <table class="meta-table">
              <tr>
                <td style="width: 55%;">
                  <strong>Offer ID:</strong> {{intern_id}}
                </td>
                <td style="text-align: right; width: 45%;">
                  <strong>Date:</strong> {{date}}
                </td>
              </tr>
              <tr>
                <td style="padding-top: 4px;">
                  <strong>To:</strong> {{user_name}}
                </td>
                <td style="text-align: right; padding-top: 4px;">
                  <strong>College / University:</strong> {{college_name}}
                </td>
              </tr>
            </table>

            <!-- Subject -->
            <div class="subject-bar">
              Subject: Offer of Internship &ndash; {{track_name}}
            </div>

            <!-- Salutation -->
            <div class="salutation">Dear {{user_name}},</div>

            <!-- Body Paragraphs -->
            <p class="body-p">
              We are pleased to offer you an opportunity to participate in the Internship Programme at <strong>Redback IT Solutions Private Limited</strong> in the domain of <strong>{{track_name}}</strong>.
            </p>

            <p class="body-p">
              This programme is designed to enhance your technical knowledge and practical skills through structured learning, hands-on assignments, project development, and guidance relevant to your selected domain.
            </p>

            <!-- Terms and Conditions -->
            <div class="terms-section">
              <div class="terms-heading">Terms and Conditions</div>
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
                  <div style="font-size: 11px; margin-bottom: 2px;">Sincerely,</div>
                  <img class="sig-img" src="media/templates/offer_letter/default-c43d595d/img/signature.png" alt="Program Director Signature">
                  <div class="sig-name">Program Director</div>
                  <div class="sig-company">Redback IT Solutions Private Limited</div>
                  <div class="sig-web">Website: <a href="https://redback.in" style="color: #bb0004; text-decoration: none;">https://redback.in</a></div>
                </td>
              </tr>
            </table>

            <!-- Candidate Acceptance -->
            <div class="acceptance-box">
              <div class="acceptance-title">Candidate Acceptance</div>
              <div class="acceptance-text">
                I acknowledge this offer and agree to comply with the applicable internship programme terms and conditions.
              </div>
              <table class="acceptance-table">
                <tr>
                  <td style="width: 55%;">
                    <strong>Student Name:</strong> {{user_name}}
                  </td>
                  <td style="text-align: right; width: 45%;">
                    <strong>Date:</strong> {{date}}
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

# Substitute sample tokens for testing
sample_rendered = html.replace("{{user_name}}", "John Doe") \
                      .replace("{{intern_id}}", "RB-INT-2026-0001") \
                      .replace("{{date}}", "21/10/2026") \
                      .replace("{{college_name}}", "Stanford University") \
                      .replace("{{track_name}}", "Full Stack Development")

out = io.BytesIO()
pisa.CreatePDF(sample_rendered, dest=out)
doc = pymupdf.open(stream=out.getvalue(), filetype='pdf')
print(f"Pages: {len(doc)}")
pix = doc[0].get_pixmap(dpi=150)
pix.save("scratch/test_user_content.png")
print("Saved scratch/test_user_content.png")
