from reportlab.lib.pagesizes import A4

def create_title_page(pdf_report, title):
    """Creates a title page for the PDF report."""
    # Set the font and size
    pdf_report.setFont("Times-Roman", 36)
    text_width = pdf_report.stringWidth(title, "Times-Roman", 36)
    pdf_report.drawCentredString(A4[0] / 2, A4[1] / 2, title)
    underline_x_start = (A4[0] - text_width) / 2
    underline_y = A4[1] / 2 - 5
    pdf_report.setLineWidth(1)
    pdf_report.line(underline_x_start, underline_y, underline_x_start + text_width, underline_y)
    pdf_report.line(underline_x_start, underline_y - 3, underline_x_start + text_width, underline_y - 3)
    
    # Add a page break
    pdf_report.showPage()

def scale_image(img, max_width, max_height):
    """Scales the image to fit within the specified dimensions while maintaining the aspect ratio."""
    img_width, img_height = img.size
    aspect_ratio = img_height / img_width

    if img_width > max_width:
        img_width = max_width
        img_height = img_width * aspect_ratio

    if img_height > max_height:
        img_height = max_height
        img_width = img_height / aspect_ratio
    return img_width, img_height