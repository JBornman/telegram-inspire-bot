import requests
import os


def fetchimage(search: str):
    """
        Fetches a random image from wallhaven using the search term provided.
        This image is stored and renamed to raw.jpg

        Args:
            search (str): search term to retrieve background image from wallhaven
    """

    # Check for the existence of the downloads directory
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    #  Build the wallhaven image search image API request
    URL = "https://wallhaven.cc/api/v1/search"
    PARAMS = {
        'resolutions': '1920x1080',
        'ratios': '16x9',
        'q': search,
        'sorting': 'random',
        'seed': 'atxFqe'
    }

    # Send the wallhaven image search request
    r = requests.get(url=URL, params=PARAMS)
    filename = ''
    data = r.json()

    # TODO: if no results redo request with default search

    # TODO: Delete raw if it still exists

    #  Save result as raw.jpg
    for idx in range(1):
        img_data = requests.get(data['data'][idx]['path']).content
        with open('downloads' + '/' + data['data'][idx]['id'] + '.jpg',
                  'wb') as handler:
            handler.write(img_data)
            temp = handler.name
            filename = temp.replace('/', '\\')
            print(handler.name)
        os.rename(filename, 'downloads/raw.jpg')
