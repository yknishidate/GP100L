
import requests
import os

filename = "bunny.obj"
url = "https://graphics.stanford.edu/~mdfisher/Data/Meshes/bunny.obj"
url_data = requests.get(url).content

with open(filename, mode='wb') as f:
    f.write(url_data)
