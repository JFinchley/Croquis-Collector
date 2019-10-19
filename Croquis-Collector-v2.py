# version 2.3 for new website design

import json
import os
import re

import bs4
import requests


def download(url, file_name):
    with open(file_name, "wb") as file:     # open in binary mode
        response = requests.get(url)        # get request
        file.write(response.content)        # write to file
        file.close()                        # close file


print("Croquis-Collector-v2 started.")
# directories list contains URLs of model indices
indicesList = ["/model-index-directory"]  # starting page
jsURLs = []  # contains script.js urls scrapped from source html
jsonURLs = []   # contains relevant json urls that were within jsURLs
baseDir = ""

# create list of archive URLs by looping through all indices
for listItem in indicesList:
    print("\rInterrogating http://www.onairvideo.com" + str(listItem), end="", flush=True)
    tempFileHTML = requests.get("http://www.onairvideo.com" + str(listItem))  # saves file for scraping
    soup = bs4.BeautifulSoup(tempFileHTML.content, "html.parser")
    href = []   # make a list to save all links by scraping soup
    for link in soup.find_all("a"):
        href.append(link.get("href"))
    href = list(set(href))  # remove duplicates
    for item in href:   # record the unique links which are indexes and contain links to models
        if item is not None and "model-index" in item:
            if item.find("#", 0) != -1:
                item = item[0:item.find("#",0)]
            if item not in indicesList:
                indicesList.append(item)
    dataJS = str(soup)  # using re to scrap JSON data (held in script.js files) to find links to models
    pattern = r"//img1.wsimg.com/blobby/go/e447419f-7200-4240-9090-26bc61d6e2b2/gpub/\S+?/script.js"
    jsURLs = list(set(re.findall(pattern, dataJS)))     # jsURLs used for jsonURLs on this page
    for item in jsURLs:
        if item is not None and item not in jsonURLs:
            jsonURLs.append(item)   # jsonURLs holds json urls across all indexes
print("\rInterrogated all site directories.")   # else the json print will overwrite the downloads

# cycle through the found script.js s and get the gallery JSON files to analyse
photoURLs = []  # for all
for listItem in jsonURLs:
    print("\rInterrogating file " + str(jsonURLs.index(listItem) + 1) + " of " + str(len(jsonURLs)) +
          " JSON files to find model and photo information.", flush=True, end="")
    data = str(requests.get("http:" + str(listItem)).content)
    if "galleryImages" in data:  # all the gallery JSON files have galleryImages in them
        data = data[data.find("})({") + 3:data.rfind("}") + 1]  # strips javascript from JSON
        data = data.replace(r"\\u002F", "/")  # cleans JSON by removing backslash characters
        data = data.replace("\\", "")   # there are the occasional random backslash in names
        dataStore = json.loads(data)
        for item in dataStore["galleryImages"][0]:  # json format ["galleryImages"][0][]["image"]["image"]
            photoURLs.append(item["image"]["image"].rsplit("/", 1)[1])
photoURLs = list(set(photoURLs))    # remove duplicates
photoURLs.sort()

print("\n" + str(len(photoURLs)) + " photos found, ", end="")
totalCount = len(photoURLs)

# cycle through and remove images that already exist
for listItem in photoURLs[:]:
    if os.path.isfile(baseDir + listItem):
        photoURLs.remove(listItem)

print("skipped " + str(totalCount - len(photoURLs)) + " existing images in folder.")

# download images that have not been downloaded previously
for listItem in photoURLs:
    print("\rDownloading image " + str(photoURLs.index(listItem) + 1) + " of " + str(len(photoURLs)) + ": " + listItem,
          end="", flush=True)
    download("https://img1.wsimg.com/isteam/ip/e447419f-7200-4240-9090-26bc61d6e2b2/" + str(listItem),
             baseDir + listItem)

print("\nCroquis-Collector-v2 complete.")
