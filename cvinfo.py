import os
import requests
from bs4 import BeautifulSoup
from lxml import html
import re

# List of directory names to ignore
ignore_list = ['ignore_dir1', 'ignore_dir2']

def search_comicvine(series_name):
    print(f"Searching ComicVine for series: {series_name}")
    # Extract volume number if present, otherwise consider it as Volume 1
    match = re.search(r'V(\d+)', series_name)
    volume_number = match.group(1) if match else '1'
    print(f"Volume number: {volume_number}")
    search_query = series_name.replace(' ', '%20')
    
    # Function to perform the search on a specific page
    def perform_search(page):
        search_url = f"https://comicvine.gamespot.com/search/?q={search_query}&page={page}"
        print(f"Search URL: {search_url}")
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        tree = html.fromstring(str(soup))
        
        # List of paths to check for volume information
        paths = [
            f'/html/body/div[1]/div/div[2]/div/div/ul[1]/li[{i}]/a' for i in range(1, 16)
        ]
        
        # Check each path for volume information
        for path in paths:
            print(f"Checking path: {path}")
            results = tree.xpath(path)
            for result in results:
                url = result.xpath('./@href')[0]
                volume_info = result.xpath('.//p[2]/text()')
                volume_info = [info.strip() for info in volume_info]  # Strip extra spaces
                print(f"Found volume info: {volume_info}")
                if volume_info and f"Volume {volume_number}" in volume_info[0]:
                    print(f"Found URL: {url} for series: {series_name}")
                    return url, "Volume Search"
        return None, None
    
    # Perform the search on the first page
    url, search_type = perform_search(1)
    if url:
        return url, search_type
    
    # Perform the search on the second page if no match found on the first page
    url, search_type = perform_search(2)
    if url:
        return url, search_type
    
    # If no match found, search for "Volume YEAR"
    year_match = re.search(r'\((\d{4})\)', series_name)
    if year_match:
        year = year_match.group(1)
        print(f"Year found: {year}")
        
        # Perform the search for "Volume YEAR"
        search_url = f"https://comicvine.gamespot.com/search/?q={search_query}"
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        tree = html.fromstring(str(soup))
        
        # List of paths to check for volume information
        paths = [
            f'/html/body/div[1]/div/div[2]/div/div/ul[1]/li[{i}]/a' for i in range(1, 16)
        ]
        
        for path in paths:
            print(f"Checking path for year: {path}")
            results = tree.xpath(path)
            for result in results:
                url = result.xpath('./@href')[0]
                volume_info = result.xpath('.//p[1]/span/text()')
                volume_info = [info.strip() for info in volume_info]  # Strip extra spaces
                print(f"Found volume info: {volume_info}")
                if volume_info and re.match(rf"Volume\s+{year}", volume_info[0]):
                    print(f"Found URL: {url} for series: {series_name}")
                    return url, "Year Search"
    
    print(f"No URL found for series: {series_name}")
    return None, None

def create_cvinfo_file(directory, no_url_dirs, found_urls):
    series_name = os.path.basename(directory)
    print(f"Processing directory: {directory}")
    url, search_type = search_comicvine(series_name)
    if url:
        full_url = f"https://comicvine.gamespot.com{url}"
        cvinfo_path = os.path.join(directory, 'cvinfo')
        with open(cvinfo_path, 'w') as file:
            file.write(full_url)
        print(f"cvinfo file created with URL: {full_url}")
        found_urls.append((series_name, full_url, search_type))
    else:
        print(f"No URL found for series: {series_name}")
        no_url_dirs.append(series_name)

def process_immediate_subdirectories(root_directory):
    print(f"Processing root directory: {root_directory}")
    no_url_dirs = []
    found_urls = []
    for subdir in next(os.walk(root_directory))[1]:
        # Skip directories in the ignore list
        if subdir in ignore_list:
            print(f"Skipping directory: {subdir}")
            continue
        create_cvinfo_file(os.path.join(root_directory, subdir), no_url_dirs, found_urls)
    
    # Write the list of directories with no URL found to a .txt file
    no_url_file_path = os.path.join(root_directory, 'no_url_dirs.txt')
    with open(no_url_file_path, 'w') as file:
        for dir_name in no_url_dirs:
            file.write(f"{dir_name}\n")
    print(f"List of directories with no URL found written to: {no_url_file_path}")
    
    # Write the list of successfully found URLs to a .html file with two columns
    found_urls_file_path = os.path.join(root_directory, 'found_urls.html')
    with open(found_urls_file_path, 'w') as file:
        file.write("<html><body><table border='1'>\n")
        file.write("<tr><th>Volume Search</th><th>Year Search</th></tr>\n")
        volume_search_items = [f"<li>{dir_name}: <a href=\"{url}\">{url}</a></li>" for dir_name, url, search_type in found_urls if search_type == "Volume Search"]
        year_search_items = [f"<li>{dir_name}: <a href=\"{url}\">{url}</a></li>" for dir_name, url, search_type in found_urls if search_type == "Year Search"]
        max_length = max(len(volume_search_items), len(year_search_items))
        for i in range(max_length):
            file.write("<tr>")
            file.write(f"<td>{volume_search_items[i] if i < len(volume_search_items) else ''}</td>")
            file.write(f"<td>{year_search_items[i] if i < len(year_search_items) else ''}</td>")
            file.write("</tr>\n")
        file.write("</table></body></html>\n")
    print(f"List of successfully found URLs written to: {found_urls_file_path}")

# Get the directory in which the script resides
script_directory = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {script_directory}")

# Process only the immediate subdirectories in the script's directory
process_immediate_subdirectories(script_directory)
