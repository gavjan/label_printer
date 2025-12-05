# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: 'image.py'
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import textwrap
from PIL import Image, ImageFont, ImageDraw
from barcode import Code128
from barcode.writer import ImageWriter
def read_image(path, resize=None):
    try:
        opened_img = Image.open(path)
        if resize:
            opened_img = opened_img.resize((resize, resize))
        if path[(-4):] == '.png':
            opened_img = opened_img.convert('RGBA')
        return opened_img
    except FileNotFoundError:
        print('[ERROR] file:', path, 'not found')
        exit(1)
def draw_text(draw, text, x, y, size, center_x=False, center_y=False, rev_x=False, rev_y=False):
    font = ImageFont.truetype('assets/montserrat-bold.ttf', size)
    img_width, img_height = draw.im.size
    width, height = draw.textsize(text, font=font)
    if center_x:
        x += (img_width - width) // 2
    if center_y:
        y += (img_height - height) // 2
    if rev_x:
        x = img_width - width - x
    if rev_y:
        y = img_height - height - y
    draw.text((x, y), text, fill='black', font=font)
    return (width, height)
def make_jpg(prod, jpg_path):
    aspect_ratio = 1.45
    img_width = 580
    img_height = int(img_width / aspect_ratio)
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    top_pad = 20
    left_pad = 20
    right_pad = 20
    wrap = 33
    logo = read_image('assets/logo.png', resize=60)
    img.paste(im=logo, box=(img_width - logo.width - right_pad, top_pad), mask=logo)
    code128 = Code128(str(prod['prod_id']), writer=ImageWriter())
    code_img = code128.render(text='', writer_options={'module_height': 4, 'module_width': 0.57, 'quiet_zone': 1})
    code_width, code_height = code_img.size
    code_height -= 15
    img.paste(code_img, ((img_width - code_width) // 2, img_height - code_height - 5))
    _, id_height = draw_text(draw, str(prod['prod_id']), 0, code_height, 18, center_x=True, rev_y=True)
    amd = read_image('assets/amd.png', resize=25)
    amd_width, amd_height = amd.size
    p = prod['sale_price']
    p_size = 165 if len(p) <= 5 else 138 if len(p) == 6 else 115
    price_width, price_height = draw_text(draw, p, -amd_width // 2, code_height + id_height + 3, p_size, center_x=True, rev_y=True)
    img.paste(im=amd, box=((img_width + price_width - amd_width) // 2, img_height - code_height - id_height - amd_height - 15), mask=amd)
    size_height = 0
    if prod['size'].strip()!= '':
        _, size_height = draw_text(draw, f"Size: {prod['size']}", left_pad, top_pad, 32)
    sum_height = 5
    wrapped = textwrap.wrap(prod['title'], width=wrap)
    if not wrapped:
        wrapped.append('')
    for line in wrapped:
        _, title_height = draw_text(draw, line, left_pad, top_pad + size_height + sum_height, 24)
        sum_height += title_height
    img.save(jpg_path)
    with open('written.csv', 'a') as f:
        f.write(f"{prod['prod_id']},{prod['title']} , {prod['link']}\n")