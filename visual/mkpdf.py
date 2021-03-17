import pdfkit

html_path = "girl_and_goat_demo.html"
output_path = "test.pdf"

with open(html_path, 'rb') as fp:
    html_string = str(fp.read())
    pdfkit.from_string(html_string, output_path)
