# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: 'printer.py'
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import subprocess
import time
from PIL import Image
from fpdf import FPDF
PDF_PATH = 'label.pdf'
BLANK_PDF = 'assets/blank.pdf'
def convert_jpg_to_pdf(input_jpg_path, output_pdf_path):
    image = Image.open(input_jpg_path)
    pdf = FPDF(unit='pt', format=image.size)
    pdf.add_page()
    pdf.image(input_jpg_path, 0, 0, image.size[0], image.size[1])
    pdf.output(output_pdf_path)
def print_jpg(jpg_path, trailing_blank=False):
    convert_jpg_to_pdf(jpg_path, PDF_PATH)
    print_pdf(PDF_PATH)
    if trailing_blank:
        time.sleep(0.75)
        print_pdf(BLANK_PDF)
def print_pdf(pdf_path='C:\\Users\\gevoc\\OneDrive\\Desktop\\file.pdf'):
    acro_path = 'C:\\Program Files\\Adobe\\Acrobat DC\\Acrobat\\Acrobat.exe'
    subprocess.Popen([acro_path, '/n', '/t', pdf_path, ''], shell=True)
if __name__ == '__main__':
    print_jpg('label.jpg')