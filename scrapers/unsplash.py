import os
import io
import tempfile
import requests
from PIL import Image

def fetch_image_data(search: str):
    """
        Searches for a random image related to the provided search term

        Args:
            Search (str): search term to use when finding a random image
        
        Returns:
            Json (str): Object containing image & user properties
    """

    url = "https://api.unsplash.com/photos/random"
    params = {
        'query': search,
        'orientation': 'landscape',
        'count': 1,
        'client_id': os.getenv("UnsplashClientID")
    }

    r = requests.get(url=url, params=params, timeout=60)

    if r.status_code == 404:
        return None

    data = r.json()

    return data[0]



def download_image(url: str):
    """
        Downloads a pre-resized version of the photo at the provided url

        Args:
            url (str): The url of the image to download

        Args:
            Image (PIL image): The downloaded image
    """

    img_url = url + f"&w={os.getenv('CanvasWidth')}&h={os.getenv('CanvasHeight')}&fit=crop"

    buffer = tempfile.SpooledTemporaryFile(max_size=1e9)
    r = requests.get(img_url, stream=True, timeout=60)

    if r.status_code == 200:
        for chunk in r.iter_content(chunk_size=1024):
            buffer.write(chunk)

        buffer.seek(0)
        img = Image.open( io.BytesIO( buffer.read() ) )
    buffer.close()

    return img



def get_image(search: str) -> tuple:
    """
        This is the entry point methos that should be used to retrieve the image.
        Orchestrates the download of the image & returns the accompanying data.

        Args:
            Search (str): search term to use when getting the image
        
        Returns:
            Package (tuple): A tuple object containing:
                - [0] Artist name
                - [1] Link to artist's page
                - [2] Image
    """

    img_data = fetch_image_data(search)

    # If no results
    if img_data is None:
        raise IndexError

    img = download_image(img_data["urls"]["raw"])

    tupleobj = (img_data["user"]["name"], img_data["user"]["links"]["html"], img)
    return tupleobj
