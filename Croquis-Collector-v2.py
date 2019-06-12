# version 2.0 for new website design

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
indicesList = ["/model-index-1"]  # starting page
jsURLs = []  # contains script.js urls scrapped from source html
jsonURLs = []   # contains relevant json urls that were within jsURLs

# create list of archive URLs by looping through all indices
for listItem in indicesList:
    print("Downloading http://www.onairvideo.com" + str(listItem))
    download("http://www.onairvideo.com" + str(listItem), "tempfile.html")  # saves file for scraping
    tempFileHTML = open("tempfile.html")
    soup = bs4.BeautifulSoup(tempFileHTML, "html.parser")

    # make a list to save all links by scraping tempfile.html
    href = []
    for link in soup.find_all("a"):
        href.append(link.get("href"))

    # record the links which are indexes and contain links to models
    for item in href:
        if item is not None:
            if "model-index-pg" in item:
                if item not in indicesList:
                    if "#" not in item:  # loops through temporary list and adds to directoireslist if unique
                        indicesList.append(item)

    # make a list of each model link by json data from source html
    dataJS = str(soup)  # using re to scrap JSON data (held in script.js files)
    pattern = r"//img1.wsimg.com/blobby/go/e447419f-7200-4240-9090-26bc61d6e2b2/gpub/\S+?/script.js"
    jsURLs = re.findall(pattern, dataJS)     # jsURLs used as temporary storage
    jsURLs = list(set(jsURLs))    # remove duplicates
    for item in jsURLs:
        if item is not None:
            if item not in jsonURLs:
                jsonURLs.append(item)

    tempFileHTML.close()  # file clean up

print("Downloading and interpreting " + str(len(jsonURLs)) + " JSON files to find model and photo information.")

# cycle through the found script.js s and get the gallery JSON files to analyse
modelList = []  # format [[modelName1, [modelURL1, modelURLn]], [modelNamen, [modelURL1, modelURLn]]]
for listItem in jsonURLs:
    download("http:" + str(listItem), "tempfile.json")
    with open("tempfile.json") as tempFileJSON:
        data = tempFileJSON.read()
        if "Gallery4" in data:  # all the gallery JSON files have Gallery4 in them
            data = data[data.find("})({") + 3:data.rfind("}") + 1]  # strips javascript from JSON
            data = data.replace("\u002F", "/")  # cleans JSON by removing backslash characters
            data = data.replace("/:/", "")  # removes the useless /:/ from the (photo) urls
            dataStore = json.loads(data)
            modelName = dataStore["title"]
            photoURLs = []
            for item in dataStore["paginatedImages"]:
                for element in item:  # the JSON stores urls in a ["paginatedImages"][i]["url"] format
                    photoURLs.append(element["url"])  # with i being an integer
            photoURLs = list(set(photoURLs))    # remove duplicates
            modelList.append([modelName, photoURLs])    # add to modelList
        tempFileJSON.close()

print("Found " + str(len(modelList)) + " models and " +
      str(str(modelList).count(",") + 1 - len(modelList)) + " photos.")

# cycle through model name downloading photos for folders that do not already exist
for listItem in modelList:
    modelName = listItem[0]
    photoURLs = listItem[1]
    if os.path.isdir(modelName):
        if len(os.listdir(modelName)) >= len(photoURLs):
            print("Skipping model " + str(modelName) + ". Existing images in folder.")
            continue  # skip this listItem, model folder exists with correct number of images
    else:
        os.mkdir(modelName)
    for item in photoURLs:
        print("Downloading model " + str(modelName) + ", image " + str(photoURLs.index(item) + 1) +
              " of " + str(len(photoURLs)))
        download("http:" + str(item),
                 str(os.getcwd()) + "\\" + str(modelName) + "\\" + str(photoURLs.index(item) + 1) + ".jpg")

# Clean up tempfiles
os.remove("tempfile.html")
os.remove("tempfile.json")

print("Croquis-Collector-v2 complete.")
