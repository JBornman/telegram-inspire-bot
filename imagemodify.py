# Importing the PIL library
import textwrap
import os
from urllib.parse import quote_plus
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


def modifyimage(quote: str, source: str):
    """
    Takes a downloaded image and adds the quote and source to it.
    Deletes the original image and saves the edited image.

    Args:
        quote (str):
        source (str):
    """

    font = "fonts/FreeMono.ttf"
    shadowfont = "fonts/FreeMonoBold.ttf"
    quotesize = 100
    sourcesize = 80

    # Open the image
    img = Image.open('downloads/raw.jpg')

    # Text wrapping for our quote
    quote = textwrap.fill(text=quote, width=20)

    # Prep adding of 2D graphics
    I1 = ImageDraw.Draw(img)

    # Style quote shadow and add to image
    myshadow = ImageFont.truetype(shadowfont, quotesize)
    I1.multiline_text(position(I1, quote, myshadow),
                      quote,
                      font=myshadow,
                      fill=(255, 255, 255),
                      align='center')

    # Style quote text and add to image
    myfont = ImageFont.truetype(font, quotesize)
    I1.multiline_text(position(I1, quote, myfont),
                      quote,
                      font=myfont,
                      fill=(0, 0, 0),
                      align='center')

    # Style source shadow and add to image
    myshadow = ImageFont.truetype(shadowfont, sourcesize)
    I1.text(positionsource(I1, quote, source, myshadow, 0.1),
            source,
            font=myshadow,
            fill=(255, 255, 255))

    # Style source text and add to image
    myfont = ImageFont.truetype(font, sourcesize)
    I1.text(positionsource(I1, quote, source, myfont, 0.1),
            source,
            font=myfont,
            fill=(0, 0, 0))

    # Display and save the edited image and delete the original
    img.show()
    img.save("downloads/quote.jpg")
    os.remove("downloads/raw.jpg")


def position(draw: ImageDraw, text: str, font: ImageFont):
    """
    Determines positioning of the given text based on
    text size and placing on 1920x1080 image

    Args:
        draw (ImageDraw): ImageDraw used for text size calculation
        text (str): Content of the desired text
        font (ImageFont): Desired font

    Returns:
        x (int): numeric x value of text position
        y (int): numeric y value of text position
    """
    textsize = draw.textsize(text, font)
    screen_x = 1920
    screen_y = 1080
    x = screen_x / 2 - textsize[0] / 2
    y = screen_y / 2 - textsize[1] / 2
    return int(x), int(y)


def positionsource(draw: ImageDraw,
                   quote: str,
                   source: str,
                   font: ImageFont,
                   offset: float = 1.5):
    """
    Determines positioning of the given author of quote based on
    quote size, author size and placing on 1920x1080 image

    Args:
        draw (ImageDraw): ImageDraw used for text size calculation
        quote (str): Content of the desired quote
        source (str): Content of the desired author
        font (ImageFont): Desired font
        offset (float, optional): Offset value for x axis offset (right or left). Defaults to 1.5.

    Returns:
        author_x (int): numeric x value of author position
        author_y (int): numeric y value of author position
    """
    text_width, text_height = draw.textsize(quote, font)
    text_x, text_y = position(draw, quote, font)

    source_width = draw.textsize(source, font)
    source_x = (text_x + text_width) - int(
        (text_x + text_width) * offset) - source_width[0]
    source_y = (text_y + text_height) + 50
    return int(source_x), int(source_y)