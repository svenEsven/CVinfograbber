README.txt

ComicVine URL Finder Script
===========================

Description:
------------
This script searches for comic series URLs on the website "comicvine.gamespot.com" based on directory names. It considers volume numbers and years in the directory names, excludes certain directories, and creates an HTML list of successful matches.

Requirements:
-------------
- Python 3.x
- requests library
- BeautifulSoup library
- lxml library

You can install the required libraries using pip:

===============================================================================================================================================================================

Usage:
------
1. Place the script in the root directory containing the subdirectories you want to process.
2. Update the `ignore_list` variable in the script to include any directory names you want to exclude from the search.
3. Run the script.

The script will:
- Process each immediate subdirectory in the root directory.
- Search for the comic series on ComicVine based on the directory name.
- Extract the volume number and year from the directory name if present.
- Create a `cvinfo` file in each subdirectory with the found URL.
- Generate a `no_url_dirs.txt` file listing directories with no URL found.
- Generate a `found_urls.html` file listing successfully found URLs with hyperlinks.

Functions:
----------
1. `search_comicvine(series_name)`: Searches ComicVine for the given series name and returns the URL and search type (Volume Search or Year Search).
2. `create_cvinfo_file(directory, no_url_dirs, found_urls)`: Creates a `cvinfo` file with the found URL in the given directory.
3. `process_immediate_subdirectories(root_directory)`: Processes the immediate subdirectories in the root directory, creates `cvinfo` files, and generates `no_url_dirs.txt` and `found_urls.html`.

Files Generated:
----------------
1. `cvinfo`: A file created in each subdirectory containing the found URL.
2. `no_url_dirs.txt`: A file listing directories with no URL found.
3. `found_urls.html`: An HTML file listing successfully found URLs with hyperlinks.

Limitations:
------------
- as of now it only scans the first two pages of returned search results. this could easily be altered, but it keeps run time down and reduces false positives.
-it relies on the naming convention having a volume identifier in the directory as "V#"(no V# assumes the volume is Volume 1), as well as a year identifier in parentheses
          i.e. "The Flash V3 (2010)"
		This could certainly be modified to accomodate other naming conventions per use case.
- The script processes only the immediate subdirectories in the root directory.