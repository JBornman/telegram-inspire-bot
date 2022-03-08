# Importing the PIL library
import textwrap
import os
from urllib.parse import quote_plus
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

def ModifyImage(quote,source):
    # Open the image
    img = Image.open('downloads/raw.jpg')

    quote = textwrap.fill(text=quote,width=20)

    # Prep adding of 2D graphics
    I1 = ImageDraw.Draw(img)

    # Custom font for shadow
    myShadow = ImageFont.truetype('fonts/FreeMonoBold.ttf',100)

    # Add Text to an image
    I1.multiline_text((400, 250), quote, font=myShadow, fill =(255, 255, 255), align='center')

    # Custom font style and font size
    myFont = ImageFont.truetype('fonts/FreeMono.ttf', 100)

    # Add Text to an image
    I1.multiline_text((400, 250), quote, font=myFont, fill =(0, 0, 0), align='center')

    # # ==================

    # Prep adding of 2D graphics
    I1 = ImageDraw.Draw(img)

    # Custom font for shadow
    myShadow = ImageFont.truetype('fonts/FreeMonoBold.ttf',90)

    # Add Text to an image
    I1.text((810, 810), source, font=myShadow, fill =(255, 255, 255))

    # Custom font style and font size
    myFont = ImageFont.truetype('fonts/FreeMono.ttf', 90)

    # Add Text to an image
    I1.text((810, 810), source, font=myFont, fill =(0, 0, 0))

    # Display edited image
    img.show()
    
    # Save the edited image
    img.save("downloads/quote.jpg")
    
    # Delete original
    os.remove("downloads/raw.jpg")