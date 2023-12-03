import tempfile
import os
import io
import requests
from PIL import Image

def fetch_url(search: str):
    """
        Fetches the URL of a random image matching the search term.
        This should not be called directly

        Args:
            search (str): search term to retrieve background image from wallhaven

        Return:
            URL (str): URL to a random image matching the search term
    """

    resolution = f"{ os.getenv('CanvasWidth') }x{ os.getenv('CanvasHeight') }"

    url = "https://wallhaven.cc/api/v1/search"
    params = {
        'resolutions': resolution,
        'ratios': '16x9',
        'q': search,
        'sorting': 'random',
        'seed': 'atxFqe',
        'purity': '111'
    }

    r = requests.get(url=url, params=params, timeout=60)
    data = r.json()
    return data['data'][0]['path']



def get_random_image(search: str):
    """
        Fetches a random image from wallhaven using the search term provided.

        Args:
            search (str): search term to retrieve background image from wallhaven
        
        Returns:
            Image (PIL Image): The downloaded image
    """

    img_url = fetch_url(search)

    buffer = tempfile.SpooledTemporaryFile(max_size=1e9)
    r = requests.get(img_url, stream=True, timeout=60)

    if r.status_code == 200:
        for chunk in r.iter_content(chunk_size=1024):
            buffer.write(chunk)

        buffer.seek(0)
        img = Image.open( io.BytesIO( buffer.read() ) )
    buffer.close()

    return img
