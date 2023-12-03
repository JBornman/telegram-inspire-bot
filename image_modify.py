import os
from PIL import Image, ImageDraw, ImageFont



MasterFont = os.getenv('Font')
QuoteFontSize = int( os.getenv('QuoteFontSize') )
QuoteMasterFontSize = int( os.getenv('QuoteMasterFontSize') )
DateFontSize = int( os.getenv('DateFontSize') )
CW, CH = ( int( os.getenv('CanvasWidth') ), int( os.getenv('CanvasHeight') ) ) # Canvas Width, Canvas Height

Q_font = ImageFont.truetype(MasterFont, QuoteFontSize)
QM_font = ImageFont.truetype(MasterFont, QuoteMasterFontSize)
D_font = ImageFont.truetype(MasterFont, DateFontSize)

TextColour = (0, 0, 0, 255)
OutlineColour = (255, 255, 255, 255)
OutlineThickness = int( os.getenv('OutlineThickness') )



def centre_align_text(txt_list):
    """
    pads the lines of text of a quote image so that they are centre aligned on the image

    Args:
        list (str[]): list of wrapped quote text (to make sure not all text is a single line that runs off the image)

    Returns:
        list (str[]): list of padded wrapped quote text that correctly alignt the text to the centre of the image
    """

    maxlinelength = 0
    newlist = []

    # Get longest of all the lines
    for line in txt_list:
        if len(line) > maxlinelength:
            maxlinelength = len(line)

    # Add padding to lines
    for line in txt_list:
        padding_chars = round( (maxlinelength - len(line) ) / 2 )
        pads = "  " * padding_chars
        newlist.append(pads + line)

    return newlist



# Much thanks to Chris Collett for this method - https://stackoverflow.com/questions/8257147/wrap-text-in-pil
def wrap_text(text: str, font: ImageFont.ImageFont, line_length: int):
    """
    Splits a single line of text into equal length strings in a multi-line list

    Args:
        text (str): The quote text that will need to be split over multiple line
        font (ImageFont): The font parameters that will be used when generating the final image. Used to calculate size of the text
        line_length (int): How many pixels wide the text should span before being split to a new line

    Returns:
        list (str[]): list of wrapped quote text
    """

    lines = ['']
    for word in text.split():
        line = f'{lines[-1]} {word}'.strip()
        if font.getlength(line) <= line_length:
            lines[-1] = line
        else:
            lines.append(word)

    formatted_list = centre_align_text(lines)
    return '\n'.join(formatted_list)



# Credit to Sastanin & Kannan Suresh for the math that ensures text is always centred
# https://stackoverflow.com/questions/1970807/center-middle-align-text-with-pil
def draw_text_layer(image: Image, quote: str, author: str, date: str = None):
    """
    Draws the quote, quote master & potential date text onto the background image

    Args:
        image (PIL Image): The background to be used
        quote (str): The quote text
        author (str): The name of the person who said the quote
        date (str): The date when the quote was said

    Returns:
        image (PIL Image): The created quote image
    """

    output = image.convert("RGBA").resize( (CW, CH) )
    draw = ImageDraw.Draw(output)

    # Draw the quote Text
    wrapped_quote = wrap_text(quote, Q_font, 1500)
    _, _, tw, th = draw.textbbox(xy=(10, 10), text=wrapped_quote, font=Q_font)
    draw.text( ( (CW - tw) / 2, (CH - th) / 3), text=wrapped_quote, font=Q_font, fill=TextColour, stroke_width=OutlineThickness, stroke_fill=OutlineColour)

    # Draw the quote Master's Name
    _, _, tw, th = draw.textbbox(xy=(10, 10), text=author, font=QM_font)
    draw.text( xy=( (CW - tw) / 2, CH - ( (CH - th) / 4) ), text=author, font=QM_font, fill=TextColour, stroke_width=OutlineThickness, stroke_fill=OutlineColour )

    # Draw the quote date
    if date is not None:
        _, _, tw, th = draw.textbbox(xy=(10, 10), text=date, font=D_font)
        draw.text( xy=( (CW - tw) / 2, CH - ( (CH - th) / 4) + 75 ), text=date, font=D_font, fill=TextColour, stroke_width=OutlineThickness, stroke_fill=OutlineColour )

    return output
