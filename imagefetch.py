import requests 
import os

def FetchImage(search):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    URL = "https://wallhaven.cc/api/v1/search"
    PARAMS = {'resolutions':'1920x1080',
            'ratios': '16x9',
            'q':search,
            'sorting':'random',
            'seed':'atxFqe'} 

    r = requests.get(url = URL, params = PARAMS) 
    filename = ''
    data = r.json() 

    for idx in range(1):
        img_data = requests.get(data['data'][idx]['path']).content
        with open('downloads'+'/'+data['data'][idx]['id']+'.jpg', 'wb') as handler:
            handler.write(img_data)
            temp = handler.name
            filename = temp.replace('/','\\')
            print (handler.name)
        os.rename(filename, 'downloads/raw.jpg')

