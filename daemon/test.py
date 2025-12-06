"""
Test script for label generation.
Scrapes a sample product and generates a label image.
"""

from scraper import get_prod
from image import make_jpg

if __name__ == '__main__':
    url = "https://topsale.am/product/calvin-klein-mens-wallet-sets-minimalist-bifold-and-card-cases/30924/"
    prod = get_prod(url)
    make_jpg(prod, "label.jpg")