import tempfile
import io
import requests
from PIL import Image

# Credit to Mathias Lykkegaard Lorenzen for sharing links to get the URL
# https://stackoverflow.com/questions/10639914/is-there-a-way-to-get-bings-photo-of-the-day

def get_image_url():
    """
        Returns the URL to the Bing Image of the day
        
        Returns:
            Image URL (str): URL ot the image of the day
    """

    url = "https://www.bing.com/HPImageArchive.aspx"
    params = {
        'format': "js",
        'idx': 0,
        'n': 1
    }

    r = requests.get(url=url, params=params, timeout=60)
    data = r.json()
    return f"https://bing.com/{data['images'][0]['url']}"



def get_image():
    """
        Fetches Bing's image of the day
        
        Returns:
            Image (PIL image): Bing's image of the day
    """

    img_url = get_image_url()

    buffer = tempfile.SpooledTemporaryFile(max_size=1e9)
    r = requests.get(img_url, stream=True, timeout=60)

    if r.status_code == 200:
        for chunk in r.iter_content(chunk_size=1024):
            buffer.write(chunk)

        buffer.seek(0)
        img = Image.open( io.BytesIO( buffer.read() ) )
    buffer.close()

    return img
