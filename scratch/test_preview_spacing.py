import io, os

with open('media/templates/offer_letter/default-c43d595d/index.html') as f:
    html = f.read()

# Replace template variables
html = html.replace('{{user_name}}', 'John Doe')
html = html.replace('{{intern_id}}', 'RBS/INT/623037')
html = html.replace('{{date}}', '08 September 2026')
html = html.replace('{{college_name}}', 'Stanford University')
html = html.replace('{{track_name}}', 'Full Stack Development')

# Let's inspect the current HTML
print("Loaded index.html, size:", len(html))
