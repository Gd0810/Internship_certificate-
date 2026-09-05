import os
import sys
import django

sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from certificates.pdf import html_to_pdf_bytes
import fitz

test_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Internship Offer Letter — {{user_name}}</title>
<style>
  @page {
    size: A4 portrait;
    margin: 12mm 16mm 12mm 16mm;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: Arial, Helvetica, sans-serif;
    color: #222222;
    background: #ffffff;
    font-size: 13px;
    line-height: 1.5;
  }
  .sheet {
    width: 100%;
  }
  .header-table {
    width: 100%;
    border-bottom: 2px solid #0056b3;
    padding-bottom: 12px;
    margin-bottom: 20px;
  }
  .org-title {
    font-size: 22px;
    font-weight: bold;
    color: #0056b3;
  }
  .doc-type {
    font-size: 11px;
    font-weight: bold;
    color: #666666;
    letter-spacing: 1.5px;
    margin-top: 3px;
  }
  .meta-table {
    width: 100%;
    margin-bottom: 20px;
  }
  .meta-label {
    font-size: 12px;
    color: #555555;
  }
  .subject-bar {
    background-color: #f0f4f8;
    border-left: 4px solid #0056b3;
    padding: 10px 14px;
    font-weight: bold;
    font-size: 14px;
    color: #003366;
    margin-bottom: 20px;
  }
  .salutation {
    font-size: 14px;
    font-weight: bold;
    margin-bottom: 14px;
    color: #111111;
  }
  p.body-p {
    margin-bottom: 14px;
    color: #333333;
    text-align: justify;
  }
  .details-box {
    width: 100%;
    border: 1px solid #dcdcdc;
    background-color: #fafafa;
    margin: 18px 0;
    border-collapse: collapse;
  }
  .details-box td {
    padding: 9px 14px;
    border-bottom: 1px solid #eeeeee;
    font-size: 12.5px;
  }
  .details-box tr:last-child td {
    border-bottom: none;
  }
  .label-cell {
    width: 140px;
    font-weight: bold;
    color: #004085;
  }
  .value-cell {
    color: #222222;
  }
  .closing {
    margin-top: 24px;
    margin-bottom: 10px;
    font-size: 13px;
  }
  .sig-table {
    width: 100%;
    margin-top: 10px;
    margin-bottom: 20px;
  }
  .sig-img {
    height: 48px;
    margin-bottom: 4px;
  }
  .sig-name {
    font-weight: bold;
    font-size: 13px;
    color: #003366;
  }
  .sig-title {
    font-size: 11.5px;
    color: #666666;
  }
  .footer-table {
    width: 100%;
    border-top: 1px solid #dddddd;
    padding-top: 10px;
    margin-top: 20px;
  }
  .footer-text {
    font-size: 10.5px;
    color: #777777;
  }
</style>
</head>
<body>
<div class="sheet">
  <table class="header-table">
    <tr>
      <td style="width: 60px;">
        <img src="media/templates/certificate/default-seed/img/logo.png" style="width: 48px; height: 48px;" alt="Logo">
      </td>
      <td style="vertical-align: middle;">
        <div class="org-title">CREDENTIA INTERNSHIP PLATFORM</div>
        <div class="doc-type">OFFICIAL INTERNSHIP OFFER LETTER</div>
      </td>
    </tr>
  </table>

  <table class="meta-table">
    <tr>
      <td class="meta-label"><strong>Date:</strong> 05 September 2026</td>
      <td style="text-align: right;" class="meta-label"><strong>Intern ID:</strong> RBS/INT/987456</td>
    </tr>
  </table>

  <div class="subject-bar">
    SUBJECT: OFFER OF INTERNSHIP FOR WEB DEVELOPMENT TRACK
  </div>

  <div class="salutation">Dear Giri Dharan,</div>

  <p class="body-p">
    We are pleased to extend an offer of internship for the <strong>Web Development</strong> program at Credentia. Following our review of your profile and academic record from <strong>Anna University</strong>, we are confident that your background and skills make you an excellent candidate for our internship program.
  </p>

  <table class="details-box">
    <tr>
      <td class="label-cell">Candidate Name:</td>
      <td class="value-cell">Giri Dharan</td>
    </tr>
    <tr>
      <td class="label-cell">Intern ID:</td>
      <td class="value-cell">RBS/INT/987456</td>
    </tr>
    <tr>
      <td class="label-cell">Internship Track:</td>
      <td class="value-cell">Web Development</td>
    </tr>
    <tr>
      <td class="label-cell">Institution:</td>
      <td class="value-cell">Anna University</td>
    </tr>
    <tr>
      <td class="label-cell">Start Date:</td>
      <td class="value-cell">05 September 2026</td>
    </tr>
    <tr>
      <td class="label-cell">Status:</td>
      <td class="value-cell"><strong style="color: #28a745;">Confirmed &amp; Active</strong></td>
    </tr>
  </table>

  <p class="body-p">
    During this program, you will gain hands-on practical experience through real-world projects and technical modules designed to build industry-ready expertise. Upon successful completion of all required tasks and performance evaluations, you will be awarded an official, verifiable Certificate of Completion.
  </p>

  <p class="body-p">
    We welcome you to Credentia and wish you a highly rewarding and successful internship experience.
  </p>

  <div class="closing">Sincerely,</div>

  <table class="sig-table">
    <tr>
      <td style="width: 60%;">
        <img class="sig-img" src="media/templates/certificate/default-seed/img/signature.png" alt="Signature"><br>
        <div class="sig-name">Program Director</div>
        <div class="sig-title">Credentia Internship Platform</div>
      </td>
      <td style="width: 40%; text-align: right; vertical-align: bottom;">
        <img src="media/templates/certificate/default-seed/img/seal.png" style="width: 54px; height: 54px;" alt="Seal">
      </td>
    </tr>
  </table>

  <table class="footer-table">
    <tr>
      <td class="footer-text">
        This is an official computer-generated document issued by Credentia Internship Platform.<br>
        Verification ID: RBS/INT/987456 | Authenticity can be verified at credentia.org/verify
      </td>
    </tr>
  </table>
</div>
</body>
</html>
"""

os.makedirs("scratch", exist_ok=True)
pdf = html_to_pdf_bytes(test_html, base_url="http://127.0.0.1:8000")
with open("scratch/test_layout.pdf", "wb") as f:
    f.write(pdf)

doc = fitz.open("scratch/test_layout.pdf")
print("Page count:", len(doc))
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=150)
    pix.save(f"scratch/layout_page_{i+1}.png")
    print(f"Saved scratch/layout_page_{i+1}.png")
