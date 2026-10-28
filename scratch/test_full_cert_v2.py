import io
import pymupdf as fitz
from PIL import Image, ImageDraw
from xhtml2pdf import pisa
import qrcode
import base64

# 1. Generate High-Res Circular Badge (seal.png) with zero margin so it touches strip seamlessly
size = 400
badge = Image.new('RGBA', (size, size), (255, 255, 255, 0))
draw = ImageDraw.Draw(badge)

# Outer circle ring right up to canvas boundary (0-margin)
draw.ellipse([1, 1, size-2, size-2], fill=(255, 255, 255, 255), outline=(187, 0, 4, 255), width=7)
# Inner circle ring
draw.ellipse([14, 14, size-15, size-15], fill=(255, 255, 255, 255), outline=(187, 0, 4, 255), width=3)

# Load redbackOG.png and center it
logo_path = r'c:\Users\redback\Downloads\credentia_internship_platform (1)\internproj\media\templates\certificate\default-cfe8f3a2\img\redbackOG.png'
logo = Image.open(logo_path).convert('RGBA')
target_w = 275
aspect = logo.height / logo.width
target_h = int(target_w * aspect)
logo_resized = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)

pos_x = (size - target_w) // 2
pos_y = (size - target_h) // 2
badge.paste(logo_resized, (pos_x, pos_y), logo_resized)

badge_out = r'c:\Users\redback\Downloads\credentia_internship_platform (1)\internproj\scratch\redback_seal_v2.png'
badge.save(badge_out)

# 2. QR code
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

html = f"""<!doctype html>
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
  }}
  body {{
    font-family: 'DejaVu Sans', Arial, sans-serif;
    background: #ffffff;
    color: #151c27;
    width: 100%;
  }}

  /* Outer 3-Layer Frame */
  .frame-outer {{
    width: 100%;
    border: 10px solid #151c27;
    background: #ffffff;
  }}
  .frame-mid {{
    border: 2.5px solid #bb0004;
    padding: 8px;
    background: #ffffff;
  }}
  .frame-inner {{
    border: 1px solid #151c27;
    background: #ffffff;
  }}

  /* Content Styling */
  .cert-heading {{
    font-family: 'DejaVu Sans', Arial, sans-serif;
    font-size: 32px;
    font-weight: 800;
    color: #151c27;
    letter-spacing: 7px;
    text-transform: uppercase;
    text-align: center;
    margin-top: 2px;
  }}

  .awarded-title {{
    text-align: center;
    font-family: 'DejaVu Serif', Georgia, serif;
    font-style: italic;
    font-size: 13px;
    color: #4b5563;
    margin-top: 14px;
    margin-bottom: 6px;
  }}

  .recipient-name {{
    text-align: center;
    font-family: 'DejaVu Serif', Georgia, serif;
    font-size: 28px;
    font-weight: 800;
    color: #151c27;
    text-transform: uppercase;
    letter-spacing: 1.5px;
  }}

  .for-completing {{
    text-align: center;
    font-family: 'DejaVu Serif', Georgia, serif;
    font-style: italic;
    font-size: 12px;
    color: #4b5563;
    margin-top: 14px;
    margin-bottom: 6px;
  }}

  .prog-title {{
    text-align: center;
    font-family: 'DejaVu Serif', Georgia, serif;
    font-size: 19px;
    font-weight: 800;
    color: #151c27;
    letter-spacing: 0.5px;
    margin-bottom: 5px;
  }}

  .prog-desc {{
    text-align: center;
    font-family: 'DejaVu Sans', Arial, sans-serif;
    font-size: 9.5px;
    font-weight: 600;
    color: #6b7280;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 24px;
  }}

  .footer-meta-title {{
    font-family: 'DejaVu Sans', Arial, sans-serif;
    font-size: 9px;
    font-weight: 700;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 4px;
  }}

  .footer-meta-val {{
    font-family: 'DejaVu Sans', Arial, sans-serif;
    font-size: 12px;
    font-weight: 700;
    color: #151c27;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  .bottom-disclaimer {{
    text-align: center;
    font-family: 'DejaVu Sans', Arial, sans-serif;
    font-size: 8.5px;
    color: #9ca3af;
    margin-top: 14px;
    letter-spacing: 0.3px;
  }}
</style>
</head>
<body>

<table class="frame-outer" width="100%" cellspacing="0" cellpadding="0">
  <tr>
    <td class="frame-mid">
      <table class="frame-inner" width="100%" cellspacing="0" cellpadding="0">
        <tr>
          <!-- Left Column: Vertical Strip & Circular Badge -->
          <td width="124" style="vertical-align: top; padding: 0;">
            <table width="100%" cellspacing="0" cellpadding="0">
              <tr>
                <td style="text-align: center; padding: 0;">
                  <table width="62" align="center" cellspacing="0" cellpadding="0">
                    <tr>
                      <td style="background-color: #151c27; border-left: 2px solid #bb0004; border-right: 2px solid #bb0004; height: 135px; line-height: 1px; font-size: 1px;">&nbsp;</td>
                    </tr>
                  </table>
                </td>
              </tr>
              <tr>
                <td style="text-align: center; padding: 0;">
                  <img src="{badge_uri}" width="118" height="118" alt="Redback Seal" style="width: 118px; height: 118px; display: block; margin: 0 auto;">
                </td>
              </tr>
              <tr>
                <td style="text-align: center; padding: 0;">
                  <table width="62" align="center" cellspacing="0" cellpadding="0">
                    <tr>
                      <td style="background-color: #151c27; border-left: 2px solid #bb0004; border-right: 2px solid #bb0004; height: 260px; line-height: 1px; font-size: 1px;">&nbsp;</td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>

          <!-- Right Column: Certificate Main Content -->
          <td style="vertical-align: top; padding: 12px 24px 14px 18px;">

            <!-- Header Row: Spacer on Left, QR Code on Right -->
            <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 2px;">
              <tr>
                <td style="vertical-align: top; text-align: left;">
                  &nbsp;
                </td>
                <td style="vertical-align: top; text-align: right; width: 85px;">
                  <img src="{qr_data_uri}" width="66" height="66" alt="QR Code" style="width: 66px; height: 66px; border: 1px solid #e5e7eb; padding: 2px; background: #ffffff; display: block; margin-left: auto;">
                  <div style="font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 7.5px; font-weight: 700; color: #151c27; margin-top: 3px; letter-spacing: 0.5px; text-align: center;">RBS/INT/623037</div>
                </td>
              </tr>
            </table>

            <!-- Certificate Title -->
            <div class="cert-heading">CERTIFICATE</div>
            
            <!-- OF COMPLETION with tight centered left/right accent rules -->
            <table width="290" align="center" cellspacing="0" cellpadding="0" style="margin: 6px auto 0;">
              <tr>
                <td width="55" style="border-bottom: 1.5px solid #bb0004; height: 1px; font-size: 1px; line-height: 1px;">&nbsp;</td>
                <td style="text-align: center; padding: 0 12px; font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 11.5px; font-weight: 700; color: #bb0004; letter-spacing: 3px; text-transform: uppercase; white-space: nowrap;">
                  OF COMPLETION
                </td>
                <td width="55" style="border-bottom: 1.5px solid #bb0004; height: 1px; font-size: 1px; line-height: 1px;">&nbsp;</td>
              </tr>
            </table>

            <!-- Recipient Award Line -->
            <div class="awarded-title">awarded to</div>
            <div class="recipient-name">Santhosh Kumar R</div>
            
            <!-- Centered Name Underline Table -->
            <table width="360" align="center" cellspacing="0" cellpadding="0" style="margin: 6px auto 0;">
              <tr>
                <td style="border-bottom: 1px solid #d1d5db; height: 1px; font-size: 1px; line-height: 1px;">&nbsp;</td>
              </tr>
            </table>

            <!-- Program Info -->
            <div class="for-completing">for successfully completing the</div>
            <div class="prog-title">Python Full Stack Development</div>
            <div class="prog-desc">A COMPREHENSIVE INTERNSHIP PROGRAMME AT REDBACK IT SOLUTIONS PRIVATE LIMITED</div>

            <!-- Footer Meta Row: Date | Intern ID | Signature Box -->
            <table width="100%" cellspacing="0" cellpadding="0" style="margin-top: 10px;">
              <tr>
                <!-- Left: Date of Issue -->
                <td width="33%" style="vertical-align: bottom; text-align: left; padding-left: 8px;">
                  <div class="footer-meta-title">DATE OF ISSUE</div>
                  <div class="footer-meta-val">15 OCTOBER 2026</div>
                </td>

                <!-- Center: Intern ID -->
                <td width="34%" style="vertical-align: bottom; text-align: center;">
                  <div class="footer-meta-title">INTERN ID</div>
                  <div class="footer-meta-val">RBS/INT/623037</div>
                </td>

                <!-- Right: Signature Box (replacing inGrad) -->
                <td width="33%" style="vertical-align: bottom; text-align: right; padding-right: 8px;">
                  <table align="right" cellspacing="0" cellpadding="0" style="border-left: 2.5px solid #bb0004; padding-left: 10px;">
                    <tr>
                      <td style="text-align: left;">
                        <img src="{sig_path}" alt="Signature" style="height: 42px; width: auto; max-width: 140px; display: block; margin-bottom: 2px;">
                        <div style="font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 9px; font-weight: 800; color: #151c27; text-transform: uppercase; letter-spacing: 0.5px;">AUTHORIZED SIGNATORY</div>
                        <div style="font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 8px; color: #6b7280; font-weight: 600;">Program Director &middot; Redback</div>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>

            <!-- Bottom Verification Disclaimer -->
            <div class="bottom-disclaimer">
              Scan the QR code or visit http://127.0.0.1:8000/verify/cert/ and enter the Intern ID to verify authenticity.
            </div>

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
pisa_status = pisa.CreatePDF(html, dest=buf)
print("pisa err:", pisa_status.err)
pdf_bytes = buf.getvalue()

doc = fitz.open(stream=pdf_bytes, filetype="pdf")
print("Total pages in PDF:", len(doc))
pix = doc[0].get_pixmap(dpi=150)
out_png = r'c:\Users\redback\Downloads\credentia_internship_platform (1)\internproj\scratch\full_cert_v2.png'
pix.save(out_png)
print("Saved full_cert_v2.png, size:", pix.width, "x", pix.height)
