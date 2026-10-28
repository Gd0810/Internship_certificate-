import os
import io
import pymupdf as fitz
from PIL import Image, ImageDraw
from xhtml2pdf import pisa
import qrcode
import base64

# 1. Generate High-Res Circular Badge (seal.png) with concentric red rings and Redback logo
size = 400
badge = Image.new('RGBA', (size, size), (255, 255, 255, 0))
draw = ImageDraw.Draw(badge)

# Outer circle ring
draw.ellipse([6, 6, size-6, size-6], fill=(255, 255, 255, 255), outline=(187, 0, 4, 255), width=6)
# Inner circle ring
draw.ellipse([18, 18, size-18, size-18], fill=(255, 255, 255, 255), outline=(187, 0, 4, 255), width=3)

# Load redbackOG.png and center it
logo_path = r'c:\Users\redback\Downloads\credentia_internship_platform (1)\internproj\media\templates\certificate\default-cfe8f3a2\img\redbackOG.png'
logo = Image.open(logo_path).convert('RGBA')
target_w = 260
aspect = logo.height / logo.width
target_h = int(target_w * aspect)
logo_resized = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)

pos_x = (size - target_w) // 2
pos_y = (size - target_h) // 2
badge.paste(logo_resized, (pos_x, pos_y), logo_resized)

badge_out = r'c:\Users\redback\Downloads\credentia_internship_platform (1)\internproj\scratch\redback_seal.png'
badge.save(badge_out)

# 2. Generate a real test QR code data URI
qr = qrcode.QRCode(box_size=4, border=1)
qr.add_data("http://127.0.0.1:8000/verify/cert/RBS_INT_623037")
qr.make(fit=True)
qr_img = qr.make_image(fill_color="black", back_color="white")
qr_buf = io.BytesIO()
qr_img.save(qr_buf, format="PNG")
qr_b64 = base64.b64encode(qr_buf.getvalue()).decode("ascii")
qr_data_uri = f"data:image/png;base64,{qr_b64}"

sig_path = r'c:\Users\redback\Downloads\credentia_internship_platform (1)\internproj\media\templates\certificate\default-cfe8f3a2\img\sivapriya mam sign-01.png'.replace('\\', '/')
badge_uri = badge_out.replace('\\', '/')

html_content = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: A4 landscape;
    margin: 6mm;
  }}
  * {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }}
  body {{
    font-family: 'DejaVu Sans', Arial, sans-serif;
    background: #ffffff;
    color: #151c27;
    width: 100%;
  }}

  /* 3-Layer Luxury Border Framing */
  .frame-outer {{
    width: 100%;
    border: 8px solid #151c27;
    background: #ffffff;
    padding: 3px;
  }}
  .frame-mid {{
    width: 100%;
    border: 2px solid #bb0004;
    background: #ffffff;
    padding: 9px;
  }}
  .frame-inner {{
    width: 100%;
    border: 1px solid #151c27;
    background: #ffffff;
    border-collapse: collapse;
  }}

  /* Main Layout Table */
  .layout-table {{
    width: 100%;
    border-collapse: collapse;
  }}

  /* Left Strip Column: total width ~120px */
  .col-strip {{
    width: 124px;
    vertical-align: top;
    padding: 0;
    text-align: center;
  }}

  .strip-table {{
    width: 100%;
    border-collapse: collapse;
  }}
  .strip-band {{
    width: 60px;
    background-color: #151c27;
    border-left: 2px solid #bb0004;
    border-right: 2px solid #bb0004;
    margin: 0 auto;
  }}

  /* Right Content Column */
  .col-content {{
    vertical-align: top;
    padding: 10px 24px 14px 18px;
  }}

  /* Typography */
  .cert-title {{
    font-family: 'DejaVu Sans', Arial, sans-serif;
    font-size: 34px;
    font-weight: 800;
    color: #151c27;
    letter-spacing: 7px;
    text-transform: uppercase;
    text-align: center;
  }}

  .of-completion-table {{
    margin: 6px auto 0;
    border-collapse: collapse;
  }}
  .completion-line {{
    width: 60px;
    height: 1px;
    border-bottom: 1.5px solid #bb0004;
    vertical-align: middle;
  }}
  .completion-text {{
    padding: 0 14px;
    font-family: 'DejaVu Sans', Arial, sans-serif;
    font-size: 12px;
    font-weight: 700;
    color: #bb0004;
    letter-spacing: 3.5px;
    text-transform: uppercase;
    white-space: nowrap;
  }}

  .awarded-to {{
    text-align: center;
    font-family: 'DejaVu Serif', Georgia, serif;
    font-style: italic;
    font-size: 13.5px;
    color: #4b5563;
    margin-top: 14px;
    margin-bottom: 6px;
  }}

  .candidate-name {{
    text-align: center;
    font-family: 'DejaVu Serif', Georgia, serif;
    font-size: 30px;
    font-weight: 800;
    color: #151c27;
    text-transform: uppercase;
    letter-spacing: 1.5px;
  }}

  .name-divider {{
    width: 380px;
    height: 1px;
    border-bottom: 1px solid #d1d5db;
    margin: 5px auto 14px;
  }}

  .completion-desc {{
    text-align: center;
    font-family: 'DejaVu Serif', Georgia, serif;
    font-style: italic;
    font-size: 12.5px;
    color: #4b5563;
    margin-bottom: 6px;
  }}

  .track-name {{
    text-align: center;
    font-family: 'DejaVu Serif', Georgia, serif;
    font-size: 20px;
    font-weight: 800;
    color: #151c27;
    letter-spacing: 0.5px;
    margin-bottom: 5px;
  }}

  .sub-desc {{
    text-align: center;
    font-family: 'DejaVu Sans', Arial, sans-serif;
    font-size: 10px;
    font-weight: 600;
    color: #6b7280;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 22px;
  }}

  /* Footer 3 Columns */
  .footer-table {{
    width: 100%;
    border-collapse: collapse;
  }}
  .footer-col-left {{
    width: 32%;
    vertical-align: bottom;
    text-align: left;
    padding-left: 10px;
  }}
  .footer-col-center {{
    width: 34%;
    vertical-align: bottom;
    text-align: center;
  }}
  .footer-col-right {{
    width: 34%;
    vertical-align: bottom;
    text-align: right;
    padding-right: 10px;
  }}

  .footer-label {{
    font-family: 'DejaVu Sans', Arial, sans-serif;
    font-size: 9.5px;
    font-weight: 700;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 3px;
  }}
  .footer-val {{
    font-family: 'DejaVu Sans', Arial, sans-serif;
    font-size: 12.5px;
    font-weight: 700;
    color: #151c27;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  .sig-box {{
    border-left: 2.5px solid #bb0004;
    padding-left: 12px;
    display: inline-block;
    text-align: left;
  }}

  .verify-note {{
    text-align: center;
    font-family: 'DejaVu Sans', Arial, sans-serif;
    font-size: 8.5px;
    color: #9ca3af;
    margin-top: 14px;
    letter-spacing: 0.4px;
  }}
</style>
</head>
<body>

<div class="frame-outer">
  <div class="frame-mid">
    <div class="frame-inner">

      <table class="layout-table">
        <tr>
          <!-- Left Vertical Strip with Circular Redback Seal -->
          <td class="col-strip">
            <table class="strip-table">
              <tr>
                <td style="padding: 0; text-align: center; vertical-align: top;">
                  <!-- Upper vertical strip connecting to top border -->
                  <div class="strip-band" style="height: 175px;"></div>
                </td>
              </tr>
              <tr>
                <td style="padding: 0; text-align: center; vertical-align: middle;">
                  <!-- Circular Redback Seal Badge -->
                  <div style="width: 118px; margin: 0 auto; text-align: center;">
                    <img src="{badge_uri}" width="118" height="118" alt="Redback Seal" style="width: 118px; height: 118px; display: block; margin: 0 auto;">
                  </div>
                </td>
              </tr>
              <tr>
                <td style="padding: 0; text-align: center; vertical-align: top;">
                  <!-- Lower vertical strip connecting to bottom border -->
                  <div class="strip-band" style="height: 255px;"></div>
                </td>
              </tr>
            </table>
          </td>

          <!-- Right Content Area -->
          <td class="col-content">
            <!-- Top QR Section -->
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 2px;">
              <tr>
                <td style="vertical-align: top; text-align: left;">
                  <!-- Optional subtle tag -->
                </td>
                <td style="vertical-align: top; text-align: right; width: 90px;">
                  <img src="{qr_data_uri}" width="68" height="68" alt="Verification QR Code" style="width: 68px; height: 68px; border: 1px solid #e5e7eb; padding: 2px; background: #ffffff; display: block; margin-left: auto;">
                  <div style="font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 8px; font-weight: 700; color: #151c27; margin-top: 3px; letter-spacing: 0.5px; text-align: center;">RBS/INT/623037</div>
                </td>
              </tr>
            </table>

            <!-- Title & Subtitle -->
            <div class="cert-title">CERTIFICATE</div>
            <table class="of-completion-table">
              <tr>
                <td class="completion-line"></td>
                <td class="completion-text">OF COMPLETION</td>
                <td class="completion-line"></td>
              </tr>
            </table>

            <!-- Recipient -->
            <div class="awarded-to">awarded to</div>
            <div class="candidate-name">Santhosh Kumar R</div>
            <div class="name-divider"></div>

            <!-- Program Info -->
            <div class="completion-desc">for successfully completing the</div>
            <div class="track-name">Python Full Stack Development</div>
            <div class="sub-desc">AN INTENSIVE INTERNSHIP PROGRAMME AT REDBACK IT SOLUTIONS PRIVATE LIMITED</div>

            <!-- Footer: Date, Intern ID, Signature -->
            <table class="footer-table">
              <tr>
                <td class="footer-col-left">
                  <div class="footer-label">DATE OF ISSUE</div>
                  <div class="footer-val">15 OCTOBER 2026</div>
                </td>

                <td class="footer-col-center">
                  <div class="footer-label">INTERN ID</div>
                  <div class="footer-val">RBS/INT/623037</div>
                </td>

                <td class="footer-col-right">
                  <div class="sig-box">
                    <img src="{sig_path}" alt="Signature" style="height: 44px; width: auto; max-width: 140px; display: block;">
                    <div style="font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 9px; font-weight: 800; color: #151c27; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 3px;">DIGITALLY VERIFIED</div>
                    <div style="font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 8.5px; color: #6b7280; font-weight: 600;">Authorized Signatory &middot; Redback</div>
                  </div>
                </td>
              </tr>
            </table>

            <!-- Bottom Verification Note -->
            <div class="verify-note">
              Scan the QR code or visit http://127.0.0.1:8000/verify/cert/ to verify authenticity.
            </div>

          </td>
        </tr>
      </table>

    </div>
  </div>
</div>

</body>
</html>
"""

pdf_buf = io.BytesIO()
pisa_status = pisa.CreatePDF(html_content, dest=pdf_buf)
print("pisa err:", pisa_status.err)

pdf_bytes = pdf_buf.getvalue()
doc = fitz.open(stream=pdf_bytes, filetype="pdf")
print("Page count:", len(doc))
pix = doc[0].get_pixmap(dpi=150)
out_png = r'c:\Users\redback\Downloads\credentia_internship_platform (1)\internproj\scratch\test_cert_preview.png'
pix.save(out_png)
print("Rendered PNG saved to:", out_png, "Size:", pix.width, "x", pix.height)
