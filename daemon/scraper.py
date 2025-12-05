# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: 'scraper.py'
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import HTTPError
from bs4 import BeautifulSoup as soup
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import os
import re
def file_exists(filename):
    return os.path.exists(filename)
def assert_folder(name):
    if not os.path.exists(name):
        os.makedirs(name)
def is_ascii(s):
    return all((ord(c) < 128 for c in s))
def svg_to_png(name):
    drawing = svg2rlg(name)
    try:
        renderPM.drawToFile(drawing, f'{name[:(-4)]}.png', fmt='PNG')
    except Exception:
        return False
    else:
        return True
def download_image(url, file_name, attempt=1):
    if not is_ascii(url):
        for x in url:
            # if not is_ascii(x):
            if False:
                url = url.replace(x, quote(x))
    url = url[:len("https://")] + quote(url[len("https://"):])

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:

        web_byte = urlopen(req).read()
        f = open(file_name, "wb")
        f.write(web_byte)
        f.close()
        return True
    except HTTPError as err:
        if err.code == 503 and attempt < 5:
            return download_image(url, file_name, attempt + 1)
        else:
            return False

def load_to_cache(link, name):
    assert_folder('.cache')
    if not file_exists(f'.cache/{name}'):
        download_image(link, f'.cache/{name}')
def download_tags(tag_links):
    del_len = len('topsale.am/img/')
    tags = []
    for link in tag_links:
        tag_name = re.search('topsale\\.am/img/.*', link).group()[del_len:]
        load_to_cache(link, tag_name)
        tags.append(tag_name)
    return tags
def load_page(url, attempt=1):
    if not is_ascii(url):
        for x in url:
            if not is_ascii(x):
                url = url.replace(x, quote(x))

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        web_byte = urlopen(req).read()
    except HTTPError as err:
        if err.code == 503:
            return load_page(url, attempt + 1) if attempt < 5 else soup("", "html.parser")
        return soup("", "html.parser")

    webpage = web_byte.decode('utf-8')
    page = soup(webpage, "html.parser")
    return page

def get_prod(link):
    def strip_price(p):
        return re.search('[0-9,]+', p).group()
    page_soup = load_page(link)
    prod_html = page_soup.find('div', {'class': 'details-block'})
    if not prod_html:
        return
    else:
        prod_html = prod_html.div.div.div
        title = prod_html.find('li', {'class': 'breadcrumb-item active'}).decode_contents()
        price_block = prod_html.find('span', {'class': 'old'})
        price = price_block.decode_contents() if price_block else '0'
        price = strip_price(price)
        sale_price = prod_html.find('span', {'class': 'regular'}).decode_contents()
        sale_price = strip_price(sale_price)
        brand_link = prod_html.find('div', {'class': 'product-brnd-logo'}).img['src']
        del_len = len('topsale.am/img/brands/')
        brand = re.search('topsale\\.am/img/brands/.*', brand_link).group()[del_len:]
        if brand == '0':
            brand = ''
        else:
            load_to_cache(brand_link, brand)
        if brand[(-4):] == '.svg':
            if not file_exists(f'.cache/{brand[:(-4)]}.png'):
                if svg_to_png(f'.cache/{brand}'):
                    brand = f'{brand[:(-4)]}.png'
                else:
                    brand = ''
            else:
                brand = f'{brand[:(-4)]}.png'
        size_select = prod_html.find('select', id='prodSizeChangeSel')
        size = ''
        if size_select:
            size_option = size_select.find('option')
            if size_option:
                size = size_option.text
        prod_id = prod_html.find('div', {'class': 'product-id'}).decode_contents()
        prod_id = int(re.search('\\d+', prod_id).group())
        tag_links = []
        labels = prod_html.find_all('span', {'class': 'customlabel'})
        if labels:
            for label in labels:
                tag_links.append(label.img['src'])
        off_tags = download_tags(tag_links)
        return {'title': title, 'price': price, 'sale_price': sale_price, 'prod_id': prod_id, 'size': size, 'brand': brand, 'off_tags': off_tags.copy(), 'link': link}
if __name__ == '__main__':
    print(get_prod('https://topsale.am/product/rebound-joy-sneakers/20713/'))
    print(get_prod('https://topsale.am/product/puma-womens-classic-x-barbie-no-doll-suede-/21264/'))
    print(get_prod('https://topsale.am/product/puma-womens-classic-x-barbie-no-doll-suede-/21190/'))
    print(get_prod('https://topsale.am/product/u.s.-polo-assn.-mens-us8641-analog-display-analog-quartz-black-watch/21483/'))