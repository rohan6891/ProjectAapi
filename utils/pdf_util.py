from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import black
from reportlab.pdfbase.pdfmetrics import stringWidth
from textwrap import wrap

def create_title_page(pdf,case_no, title, description, nia_officer, cio, eo, eo_designation, created_at):
    # Page dimensions
    width, height = A4

    # Margins
    top_margin = 4 * cm
    left_margin = 3 * cm
    right_margin = 3 * cm
    bottom_margin = 3 * cm

    # Set fonts and colors
    pdf.setStrokeColor(black)
    pdf.setFillColor(black)

    # Header line
    pdf.setLineWidth(0.5)
    pdf.line(left_margin, height - top_margin + 1*cm, width - right_margin, height - top_margin + 1*cm)

    # Footer line
    pdf.line(left_margin, bottom_margin - 1*cm, width - right_margin, bottom_margin - 1*cm)

    # Title section
    pdf.setFont("Helvetica-Bold", 20)
    title_text = title
    title_width = stringWidth(title_text, "Helvetica-Bold", 20)
    pdf.drawString((width - title_width) / 2, height - top_margin, title_text)

    # Case Number
    pdf.setFont("Helvetica", 12)
    case_text = f"Case No.: {case_no}"
    case_width = stringWidth(case_text, "Helvetica", 12)
    pdf.drawString((width - case_width) / 2, height - top_margin - 1.2*cm, case_text)

    # Description
    pdf.setFont("Helvetica", 11)
    desc_x = left_margin
    desc_y = height - top_margin - 3*cm
    max_desc_width = width - left_margin - right_margin

    wrapped_description = wrap(description, width=70)  # Adjust the width as needed
    for line in wrapped_description:
        pdf.drawString(desc_x, desc_y, line)
        desc_y -= 14

    # Officer details
    info_y_start = desc_y - 1.5*cm
    line_height = 15

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left_margin, info_y_start, "Officers / Officials Involved:")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(left_margin, info_y_start - line_height, f"NIA Officer: {nia_officer}")
    pdf.drawString(left_margin, info_y_start - 2*line_height, f"CIO: {cio}")
    pdf.drawString(left_margin, info_y_start - 3*line_height, f"EO: {eo} ({eo_designation})")

    # Footer: Created date
    pdf.setFont("Helvetica", 10)
    date_text = f"Report Created On: {created_at}"
    pdf.drawString(left_margin, bottom_margin - 2*cm, date_text)

    # Footer: Confidential note
    pdf.setFont("Helvetica-Oblique", 8)
    footer_text = "Confidential - For Official Use Only"
    footer_width = stringWidth(footer_text, "Helvetica-Oblique", 8)
    pdf.drawString((width - footer_width) / 2, bottom_margin - 1.6*cm, footer_text)

    pdf.showPage()
    return pdf