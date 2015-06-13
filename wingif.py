__author__ = 'paulbaker'

import sys
from os import path
import os

import requests
from lxml import html
import re


def load_page(page_url):
    print('Parsing ' + page_url)
    r = requests.get(page_url)
    tree = html.fromstring(r.text)
    image_links = tree.xpath('//a[contains(@href, ".webm")]/@href')
    image_links.extend(tree.xpath('//a[contains(@href, ".gif")]/@href'))
    image_links.extend(tree.xpath('//a[contains(@href, ".jpeg")]/@href'))
    image_links.extend(tree.xpath('//a[contains(@href, ".jpg")]/@href'))
    image_links.extend(tree.xpath('//a[contains(@href, ".png")]/@href'))
    return [i.replace(r'//', r'http://') for i in image_links]


def download_file(url):
    local_filename = url.split('/')[-1]
    if path.isfile(local_filename):
        print("Resuming " + url + " to " + local_filename)
        resume_header = {'Range': 'bytes=%d-' + str(path.getsize(local_filename))}
        r = requests.get(url, stream=True, headers=resume_header)
        write_mode = 'ab'
    else:
        print("Downloading " + url + " to " + local_filename)
        r = requests.get(url, stream=True)
        write_mode = 'wb'
    with open(local_filename, write_mode) as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()


def get_files(directory, file_types=r'(?:.*\.(?:jpe?g|png|webm|gif))'):
    files_list = os.listdir(directory)
    rgx = re.compile(file_types, re.I)
    files_list = list(filter(lambda filename: rgx.match(filename), files_list))
    return files_list


def generate_html(directory):
    html_file = directory + '/wingif.html'
    with open(html_file, 'w', encoding='UTF-8') as f:
        f.write('<html>\n')
        f.write('\t<body>\n')
        for image_path in get_files(current_dir):
            f.write('\t\t' + image_path.split('/')[-1] + '<br />')
            f.write('\t\t')
            if image_path.endswith('.webm'):
                f.write('<video muted controls loop width="500">')
                f.write('<source src="' + directory + '/' + image_path + '" type="video/mp4">')
                f.write('</video>')
            else:
                f.write('<img src="' + directory + '/' + image_path + '">')
            f.write('<br />\n')
        f.write('\t</body>\n')
        f.write('</html>')
    return html_file


if __name__ == '__main__':
    images = set()
    for arg in sys.argv[1:]:
        for link in load_page(arg):
            images.add(link)
    for image in images:
        download_file(image)
    current_dir = os.getcwd()
    os.system('google-chrome-stable --incognito ' + 'file:///' + generate_html(current_dir))
    # webbrowser.open()