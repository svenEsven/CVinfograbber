import os
import requests
from bs4 import BeautifulSoup
from lxml import html
import re

IGNORE_LIST = ['ignore_dir1', 'ignore_dir2']
SEARCH_URL_TEMPLATE = "https://comicvine.gamespot.com/search/?q={query}&page={page}"
VOLUME_PATHS = [f'/html/body/div[1]/div/div[2]/div/div/ul[1]/li[{i}]/a' for i in range(1, 16)]

def search_comicvine(series_name):
    volume_number = re.search(r'V(\d+)', series_name)
    volume_number = volume_number.group(1) if volume_number else '1'
    search_query = series_name.replace(' ', '%20')

    def perform_search(page):
        response = requests.get(SEARCH_URL_TEMPLATE.format(query=search_query, page=page))
        tree = html.fromstring(response.text)
        for path in VOLUME_PATHS:
            results = tree.xpath(path)
            for result in results:
                url = result.xpath('./@href')[0]
                volume_info = [info.strip() for info in result.xpath('.//p[2]/text()')]
                if volume_info and f"Volume {volume_number}" in volume_info[0]:
                    return url, "Volume Search"
        return None, None

    url, search_type = perform_search(1)
    if not url:
        url, search_type = perform_search(2)
    if not url:
        year_match = re.search(r'\((\d{4})\)', series_name)
        if year_match:
            year = year_match.group(1)
            response = requests.get(SEARCH_URL_TEMPLATE.format(query=search_query, page=1))
            tree = html.fromstring(response.text)
            for path in VOLUME_PATHS:
                results = tree.xpath(path)
                for result in results:
                    url = result.xpath('./@href')[0]
                    volume_info = [info.strip() for info in result.xpath('.//p[1]/span/text()')]
                    if volume_info and re.match(rf"Volume\s+{year}", volume_info[0]):
                        return url, "Year Search"
    return url, search_type

def create_cvinfo_file(directory, no_url_dirs, found_urls):
    series_name = os.path.basename(directory)
    url, search_type = search_comicvine(series_name)
    if url:
        full_url = f"https://comicvine.gamespot.com{url}"
        with open(os.path.join(directory, 'cvinfo'), 'w') as file:
            file.write(full_url)
        found_urls.append((series_name, full_url, search_type))
    else:
        no_url_dirs.append(series_name)

def process_immediate_subdirectories(root_directory):
    no_url_dirs = []
    found_urls = []
    for subdir in next(os.walk(root_directory))[1]:
        if subdir not in IGNORE_LIST:
            create_cvinfo_file(os.path.join(root_directory, subdir), no_url_dirs, found_urls)

    with open(os.path.join(root_directory, 'no_url_dirs.txt'), 'w') as file:
        file.write("\n".join(no_url_dirs))

    with open(os.path.join(root_directory, 'found_urls.html'), 'w') as file:
        file.write("<html><body><table border='1'>\n<tr><th>Volume Search</th><th>Year Search</th></tr>\n")
        volume_search_items = [f"<li>{dir_name}: <a href=\"{url}\">{url}</a></li>" for dir_name, url, search_type in found_urls if search_type == "Volume Search"]
        year_search_items = [f"<li>{dir_name}: <a href=\"{url}\">{url}</a></li>" for dir_name, url, search_type in found_urls if search_type == "Year Search"]
        max_length = max(len(volume_search_items), len(year_search_items))
        for i in range(max_length):
            file.write("<tr>")
            file.write(f"<td>{volume_search_items[i] if i < len(volume_search_items) else ''}</td>")
            file.write(f"<td>{year_search_items[i] if i < len(year_search_items) else ''}</td>")
            file.write("</tr>\n")
        file.write("</table></body></html>\n")

script_directory = os.path.dirname(os.path.abspath(__file__))
process_immediate_subdirectories(script_directory)
