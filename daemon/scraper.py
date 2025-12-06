"""
Web scraper for extracting product information from topsale.am.
Scrapes product details including title, price, images, and specifications.
"""

from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import os
import re


def file_exists(filename):
    """Check if a file exists."""
    return os.path.exists(filename)


def assert_folder(name):
    """Create a folder if it doesn't exist."""
    if not os.path.exists(name):
        os.makedirs(name)


def is_ascii(s):
    """Check if a string contains only ASCII characters."""
    return all(ord(c) < 128 for c in s)


def svg_to_png(name):
    """
    Convert an SVG file to PNG format.
    
    Args:
        name: Path to the SVG file
    
    Returns:
        True if conversion succeeded, False otherwise
    """
    drawing = svg2rlg(name)
    try:
        renderPM.drawToFile(drawing, f'{name[:-4]}.png', fmt='PNG')
        return True
    except Exception:
        return False


def download_image(url, file_name, attempt=1):
    """
    Download an image from a URL.
    
    Args:
        url: URL of the image to download
        file_name: Local path to save the image
        attempt: Current retry attempt number
    
    Returns:
        True if download succeeded, False otherwise
    """
    # URL encode non-ASCII characters
    if not is_ascii(url):
        url = url[:len("https://")] + quote(url[len("https://"):])
    
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        web_byte = urlopen(req).read()
        with open(file_name, "wb") as f:
            f.write(web_byte)
        return True
    except HTTPError as err:
        # Retry on 503 errors up to 5 times
        if err.code == 503 and attempt < 5:
            return download_image(url, file_name, attempt + 1)
        return False


def load_to_cache(link, name):
    """
    Download an image to the .cache directory if not already cached.
    
    Args:
        link: URL of the image
        name: Filename to save in cache
    """
    assert_folder('.cache')
    if not file_exists(f'.cache/{name}'):
        download_image(link, f'.cache/{name}')


def download_tags(tag_links):
    """
    Download product tag images and return their cached filenames.
    
    Args:
        tag_links: List of tag image URLs
    
    Returns:
        List of cached tag filenames
    """
    del_len = len('topsale.am/img/')
    tags = []
    for link in tag_links:
        match = re.search(r'topsale\.am/img/.*', link)
        if match:
            tag_name = match.group()[del_len:]
            load_to_cache(link, tag_name)
            tags.append(tag_name)
    return tags


def load_page(url, attempt=1):
    """
    Load and parse a webpage.
    
    Args:
        url: URL of the page to load
        attempt: Current retry attempt number
    
    Returns:
        BeautifulSoup object containing the parsed HTML
    """
    # URL encode non-ASCII characters
    if not is_ascii(url):
        for x in url:
            if not is_ascii(x):
                url = url.replace(x, quote(x))
    
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        web_byte = urlopen(req).read()
    except HTTPError as err:
        # Retry on 503 errors up to 5 times
        if err.code == 503 and attempt < 5:
            return load_page(url, attempt + 1)
        return BeautifulSoup("", "html.parser")
    
    webpage = web_byte.decode('utf-8')
    return BeautifulSoup(webpage, "html.parser")


def get_prod(link):
    """
    Scrape product information from a topsale.am product page.
    
    Args:
        link: URL of the product page
    
    Returns:
        Dictionary containing product information:
            - title: Product name
            - price: Original price
            - sale_price: Current sale price
            - prod_id: Product ID number
            - size: Product size (if available)
            - brand: Brand logo filename in cache
            - off_tags: List of promotional tag filenames
            - link: Product URL
    """
    def strip_price(price_str):
        """Extract numeric price from HTML string."""
        match = re.search(r'[0-9,]+', price_str)
        return match.group() if match else '0'
    
    page_soup = load_page(link)
    prod_html = page_soup.find('div', {'class': 'details-block'})
    
    if not prod_html:
        return None
    
    prod_html = prod_html.div.div.div
    
    # Extract product title
    title = prod_html.find('li', {'class': 'breadcrumb-item active'}).decode_contents()
    
    # Extract prices
    price_block = prod_html.find('span', {'class': 'old'})
    price = strip_price(price_block.decode_contents()) if price_block else '0'
    
    sale_price_block = prod_html.find('span', {'class': 'regular'})
    sale_price = strip_price(sale_price_block.decode_contents())
    
    # Extract and cache brand logo
    brand_logo_tag = prod_html.find('div', {'class': 'product-brnd-logo'})
    brand = ''
    if brand_logo_tag and brand_logo_tag.img:
        brand_link = brand_logo_tag.img['src']
        match = re.search(r'topsale\.am/img/brands/.*', brand_link)
        if match:
            del_len = len('topsale.am/img/brands/')
            brand = match.group()[del_len:]
            
            if brand != '0':
                load_to_cache(brand_link, brand)
                
                # Convert SVG to PNG if needed
                if brand.endswith('.svg'):
                    png_name = f'{brand[:-4]}.png'
                    if not file_exists(f'.cache/{png_name}'):
                        if svg_to_png(f'.cache/{brand}'):
                            brand = png_name
                        else:
                            brand = ''
                    else:
                        brand = png_name
            else:
                brand = ''
    
    # Extract product size
    size = ''
    size_select = prod_html.find('select', id='prodSizeChangeSel')
    if size_select:
        size_option = size_select.find('option')
        if size_option:
            size = size_option.text
    
    # Extract product ID
    prod_id_div = prod_html.find('div', {'class': 'product-id'})
    prod_id_match = re.search(r'\d+', prod_id_div.decode_contents())
    prod_id = int(prod_id_match.group()) if prod_id_match else 0
    
    # Extract promotional tags
    tag_links = []
    labels = prod_html.find_all('span', {'class': 'customlabel'})
    for label in labels:
        if label.img:
            tag_links.append(label.img['src'])
    
    off_tags = download_tags(tag_links)
    
    return {
        'title': title,
        'price': price,
        'sale_price': sale_price,
        'prod_id': prod_id,
        'size': size,
        'brand': brand,
        'off_tags': off_tags.copy(),
        'link': link
    }


if __name__ == '__main__':
    # Test with sample products
    print(get_prod('https://topsale.am/product/rebound-joy-sneakers/20713/'))
    print(get_prod('https://topsale.am/product/puma-womens-classic-x-barbie-no-doll-suede-/21264/'))
    print(get_prod('https://topsale.am/product/puma-womens-classic-x-barbie-no-doll-suede-/21190/'))
    print(get_prod('https://topsale.am/product/u.s.-polo-assn.-mens-us8641-analog-display-analog-quartz-black-watch/21483/'))