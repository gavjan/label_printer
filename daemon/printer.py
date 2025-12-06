"""
Printer module for converting and printing label images.
Converts JPG labels to PDF and sends them to the printer.
"""

import subprocess
import time
from PIL import Image
from fpdf import FPDF

PDF_PATH = 'label.pdf'
BLANK_PDF = 'assets/blank.pdf'


def convert_jpg_to_pdf(input_jpg_path, output_pdf_path):
    """
    Convert a JPG image to PDF format.
    
    Args:
        input_jpg_path: Path to input JPG file
        output_pdf_path: Path to output PDF file
    """
    image = Image.open(input_jpg_path)
    pdf = FPDF(unit='pt', format=image.size)
    pdf.add_page()
    pdf.image(input_jpg_path, 0, 0, image.size[0], image.size[1])
    pdf.output(output_pdf_path)


def print_jpg(jpg_path, trailing_blank=False):
    """
    Convert a JPG label to PDF and send to printer.
    
    Args:
        jpg_path: Path to the JPG label to print
        trailing_blank: If True, print a blank page after the label
    """
    convert_jpg_to_pdf(jpg_path, PDF_PATH)
    print_pdf(PDF_PATH)
    
    if trailing_blank:
        time.sleep(0.75)
        print_pdf(BLANK_PDF)


def print_pdf(pdf_path):
    """
    Send a PDF file to the printer using Adobe Acrobat.
    
    Args:
        pdf_path: Path to the PDF file to print
    """
    acro_path = 'C:\\Program Files\\Adobe\\Acrobat DC\\Acrobat\\Acrobat.exe'
    subprocess.Popen([acro_path, '/n', '/t', pdf_path, ''], shell=True)


if __name__ == '__main__':
    print_jpg('label.jpg')