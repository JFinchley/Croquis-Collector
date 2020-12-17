# Croquis-Collector
Downloads all model poses from Croquis Cafe, a figure drawing reference site - https://modelindexdatabase.smugmug.com/browse.

This Python 3.7 script place all photos in the directory it is run in. If an image already exists it will skip downloading that image, designed to be run periodically. At time of writing - 17/12/20 - the Croquis Cafe photo collection is ~70 GB large, comprised of ~7000 jpgs. Script will reduce file size of jps by default till collection is ~2 GB.

Dependencies: requests, selenium, PIL, urllib.parse
