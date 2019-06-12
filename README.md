# Croquis-Collector
Downloads all model poses from Croquis Cafe, a figure drawing reference site - https://onairvideo.com/model-index-1.

This Python 3.7 script will create a subdirectory per model in the directory it is run in and fills the folder with the model's pose photos. If a folder with the model's name already exists it will skip that model. At time of writing - 12/06/19 - the Croquis Cafe photo collection is 861 MB large, comprised of 2939 jpgs of 49 models.

Requires requests and beautifulsoup4 modules.
