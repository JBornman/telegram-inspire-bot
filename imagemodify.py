# Importing the PIL library
import textwrap
import os
from urllib.parse import quote_plus
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

def modifyimage(quote: str,source: str):
    """
    Takes a downloaded image and adds the quote and source to it.
    Deletes the original image and saves the edited image.

    Args:
        quote (str):
        source (str):
    """
    
    # Open the image
    img = Image.open('downloads/raw.jpg')

    # Text wrapping for our quote
    quote = textwrap.fill(text=quote,width=20)

    # Prep adding of 2D graphics
    I1 = ImageDraw.Draw(img)

    # Style quote shadow and add to image
    myshadow = ImageFont.truetype('fonts/FreeMonoBold.ttf',100)
    I1.multiline_text((400, 250), quote, font=myshadow, fill =(255, 255, 255), align='center')

    # Style quote text and add to image
    myfont = ImageFont.truetype('fonts/FreeMono.ttf', 100)
    I1.multiline_text((400, 250), quote, font=myfont, fill =(0, 0, 0), align='center')

    # Style source shadow and add to image
    myshadow = ImageFont.truetype('fonts/FreeMonoBold.ttf',90)
    I1.text((810, 810), source, font=myshadow, fill =(255, 255, 255))

    # Style source text and add to image
    myfont = ImageFont.truetype('fonts/FreeMono.ttf', 90)
    I1.text((810, 810), source, font=myfont, fill =(0, 0, 0))

    # Display and save the edited image and delete the original
    img.show()
    img.save("downloads/quote.jpg")
    os.remove("downloads/raw.jpg")