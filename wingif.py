__author__ = 'paulbaker'

import sys
from os import path

import requests
from lxml import html
import re


def load_page(page_url):
    print('Parsing ' + page_url)
    r = requests.get(page_url)
    tree = html.fromstring(r.text)
    image_links = tree.xpath('//a[contains(@href, ".webm")]/@href')
    image_links.extend(tree.xpath('//a[contains(@href, ".gif")]/@href'))
    image_links.extend(tree.xpath('//a[contains(@href, ".jpg")]/@href'))
    image_links.extend(tree.xpath('//a[contains(@href, ".png")]/@href'))
    return [i.replace(r'//', r'http://') for i in image_links]


def download_file(url):
    local_filename = url.split('/')[-1]
    print("Downloading " + url + " to " + local_filename)
    if path.isfile(local_filename):
        resume_header = {'Range': 'bytes=%d-' + str(path.getsize(local_filename))}
        r = requests.get(url, stream=True, headers=resume_header)
        write_mode = 'ab'
    else:
        r = requests.get(url, stream=True)
        write_mode = 'wb'
    with open(local_filename, write_mode) as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()


if __name__ == '__main__':
    images = []
    for arg in sys.argv[1:]:
        images.extend(load_page(arg))
    for image in images:
        download_file(image)