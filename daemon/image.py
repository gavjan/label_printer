"""
Label image generation module.
Creates product label images with barcodes, prices, and product information.
"""

import textwrap
from PIL import Image, ImageFont, ImageDraw
from barcode import Code128
from barcode.writer import ImageWriter


def read_image(path, resize=None):
    """
    Load an image from disk and optionally resize it.
    
    Args:
        path: Path to the image file
        resize: Optional size to resize the image to (width/height in pixels)
    
    Returns:
        PIL Image object
    """
    try:
        img = Image.open(path)
        if resize:
            img = img.resize((resize, resize))
        if path.endswith('.png'):
            img = img.convert('RGBA')
        return img
    except FileNotFoundError:
        print(f'[ERROR] file: {path} not found')
        exit(1)


def draw_text(draw, text, x, y, size, center_x=False, center_y=False, rev_x=False, rev_y=False):
    """
    Draw text on an image with flexible positioning options.
    
    Args:
        draw: ImageDraw object to draw on
        text: Text string to render
        x, y: Base coordinates for text placement
        size: Font size in points
        center_x: Center text horizontally
        center_y: Center text vertically
        rev_x: Calculate x from right edge instead of left
        rev_y: Calculate y from bottom edge instead of top
    
    Returns:
        Tuple of (width, height) of the rendered text
    """
    font = ImageFont.truetype('assets/montserrat-bold.ttf', size)
    img_width, img_height = draw.im.size
    
    # Get text dimensions using textbbox (Pillow 10.0.0+)
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    # Apply positioning options
    if center_x:
        x += (img_width - width) // 2
    if center_y:
        y += (img_height - height) // 2
    if rev_x:
        x = img_width - width - x
    if rev_y:
        y = img_height - height - y
    
    draw.text((x, y), text, fill='black', font=font)
    return width, height
def make_jpg(prod, jpg_path):
    """
    Generate a product label image with barcode, price, and product details.
    
    Args:
        prod: Product dictionary containing title, prod_id, sale_price, size, link
        jpg_path: Output path for the generated label image
    """
    # Label dimensions
    ASPECT_RATIO = 1.45
    IMG_WIDTH = 580
    IMG_HEIGHT = int(IMG_WIDTH / ASPECT_RATIO)
    
    # Padding constants
    TOP_PAD = 20
    LEFT_PAD = 20
    RIGHT_PAD = 20
    TITLE_WRAP_WIDTH = 33
    
    # Create blank white canvas
    img = Image.new('RGB', (IMG_WIDTH, IMG_HEIGHT), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add logo in top-right corner
    logo = read_image('assets/logo.png', resize=60)
    img.paste(logo, (IMG_WIDTH - logo.width - RIGHT_PAD, TOP_PAD), mask=logo)
    
    # Generate and place barcode at bottom center
    barcode = Code128(str(prod['prod_id']), writer=ImageWriter())
    barcode_img = barcode.render(
        text='',
        writer_options={'module_height': 3, 'module_width': 0.57, 'quiet_zone': 1}
    )
    barcode_width, barcode_height = barcode_img.size
    barcode_height -= 10  # Adjust for better fit
    img.paste(barcode_img, ((IMG_WIDTH - barcode_width) // 2, IMG_HEIGHT - barcode_height))
    
    PROD_ID_SIZE = 40
    # Draw product ID below barcode
    _, id_height = draw_text(
        draw, str(prod['prod_id']), 0, barcode_height + (PROD_ID_SIZE//40)*2, PROD_ID_SIZE,
        center_x=True, rev_y=True
    )
    
    # Add currency symbol (AMD) next to price
    currency_symbol = read_image('assets/amd.png', resize=25)
    symbol_width, symbol_height = currency_symbol.size
    
    # Draw price with dynamic sizing based on length
    price = prod['sale_price']
    if len(price) <= 5:
        price_size = 165
    elif len(price) == 6:
        price_size = 138
    else:
        price_size = 115
    price_width, price_height = draw_text(
        draw, price, -symbol_width // 2, barcode_height + id_height + 30, price_size,
        center_x=True, rev_y=True
    )
    
    # Place currency symbol next to price
    symbol_x = (IMG_WIDTH + price_width - symbol_width) // 2
    symbol_y = IMG_HEIGHT - barcode_height - id_height - symbol_height - 25
    img.paste(currency_symbol, (symbol_x, symbol_y), mask=currency_symbol)
    
    # Draw product size if available
    size_height = 0
    if prod['size'].strip():
        _, size_height = draw_text(draw, f"Size: {prod['size']}", LEFT_PAD, TOP_PAD, 32)
    
    # Draw product title with text wrapping
    title_offset = 5
    wrapped_lines = textwrap.wrap(prod['title'], width=TITLE_WRAP_WIDTH)
    if not wrapped_lines:
        wrapped_lines = ['']
    
    for line in wrapped_lines:
        _, line_height = draw_text(
            draw, line, LEFT_PAD, TOP_PAD + size_height + title_offset, 24
        )
        title_offset += line_height
    
    # Save the generated label
    img.save(jpg_path)
    
    # Log printed product to CSV
    with open('written.csv', 'a') as f:
        f.write(f"{prod['prod_id']},{prod['title']},{prod['link']}\n")