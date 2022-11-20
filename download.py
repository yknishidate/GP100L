
import requests


def download(url, filename):
    url_data = requests.get(url).content
    with open(filename, mode='wb') as f:
        f.write(url_data)


if __name__ == "__main__":

    url = "https://graphics.stanford.edu/~mdfisher/Data/Meshes/bunny.obj"
    download(url, "bunny.obj")

    url = "https://raw.githubusercontent.com/triplepointfive/ogldev/master/Content/box.obj"
    download(url, "box.obj")
