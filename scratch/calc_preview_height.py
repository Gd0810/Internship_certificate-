import io

# Let's test the height sum with different spacing params
def calculate_height(body_font, line_h, p_mb, terms_li_mb, accept_mt):
    # Header: org (21px * 1.3 + 8) + doc (15px * 1.3) + padding 8 + mb 26
    h_header = (21 * 1.3 + 8) + (15 * 1.3) + 8 + 26
    # Meta: 2 rows * (13.5 * 1.8 + 10) + mb 24
    h_meta = 2 * (13.5 * 1.8 + 10) + 24
    # Subject: 14 * 1.4 + 24 + mb 46
    h_subj = (14 * 1.4) + 24 + 46
    # Salutation: 14 * 1.4 + 18
    h_salut = (14 * 1.4) + 18
    # Body 1: 3 lines * (body_font * line_h) + p_mb
    h_b1 = 3 * (body_font * line_h) + p_mb
    # Body 2: 3 lines * (body_font * line_h) + p_mb
    h_b2 = 3 * (body_font * line_h) + p_mb
    # Terms: heading (13.5 * 1.4 + 14) + 5 items * (2 lines * (13 * line_h) + terms_li_mb) + margin 50
    h_terms = (13.5 * 1.4 + 14) + 5 * (2 * 13 * line_h + terms_li_mb) + 50
    # Body 3: 3 lines * (body_font * line_h) + p_mb
    h_b3 = 3 * (body_font * line_h) + p_mb
    # Sign: sincerely (18) + img (58 + 14) + name (20) + comp (18) + web (18) + mt 26
    h_sign = 18 + 72 + 20 + 18 + 18 + 26
    # Accept: mt (accept_mt) + title (13 * 1.4 + 10) + text (2 * 12.5 * 1.7 + 18) + table (30)
    h_accept = accept_mt + (13 * 1.4 + 10) + (2 * 12.5 * 1.7 + 18) + 30
    # Padding
    h_pad = 50 + 48
    
    total = h_header + h_meta + h_subj + h_salut + h_b1 + h_b2 + h_terms + h_b3 + h_sign + h_accept + h_pad
    print(f"Params: font={body_font}, lh={line_h}, p_mb={p_mb}, terms_mb={terms_li_mb}, accept_mt={accept_mt} => Total Height: {total:.1f}px")
    return total

calculate_height(13.5, 1.85, 20, 12, 36)
calculate_height(13.5, 1.8, 18, 10, 32)
calculate_height(13.8, 1.85, 22, 14, 40)
