import bs4
import os
import requests
import re
import threading


def download(url, file_name):
    # open in binary mode
    with open(file_name, "wb") as file:
        # get request
        response = requests.get(url)
        # write to file
        file.write(response.content)
        # close file
        file.close()


# directories list contains URLs with links to multiple models, archiveslist contains URLs of a specific model
directorieslist = ["photo-archive.html"]    # starting page
archiveslist = []
weburl = "http://www.onairvideo.com/"   # the url containing model directories
print("Base website: " + weburl)

# create list of archive URLs by looping through all directories
for listitem in directorieslist:

    print("Downloading .../" + str(listitem))
    download(weburl + str(listitem), "tempfile.html")   # saves the file as tempfile before scraping
    tempfilehtml = open("tempfile.html")
    soup = bs4.BeautifulSoup(tempfilehtml, "html.parser")

    # make a list to save all links by scraping tempfile.html
    href = []
    for link in soup.find_all("a"):
        href.append(link.get("href"))

    # split up the links into the ones we care about (containing either 'croquis-cafe-photos' or 'cc-photo-archive_')
    directory = [s for s in href if "croquis-cafe-photos" in s]     # temporary list for comparison
    for item in directory:
        if item not in directorieslist:
            directorieslist.append(item)    # loops through temporary list and adds to directoireslist if unique

    archive = [s for s in href if "cc-photo-archive_" in s]     # temporary list for comparison
    for item in archive:
        if item not in archiveslist:
            archiveslist.append(item)       # loops through temporary list and adds to archiveslist if unique

    tempfilehtml.close()    # file clean up

# check if folder of same name exists, if not, add it and download images
for listitem in archiveslist:

    # string variables used in the prints and folder detection/creation
    modelname = listitem.replace("cc-photo-archive_", "").replace(".html", "").capitalize()
    modelprogress = str(archiveslist.index(listitem) + 1) + "/" + str(len(archiveslist))

    # skip downloading the model if a folder already exists for the model (i.e. they've been downloaded before)
    if os.path.isdir(os.getcwd() + "\\" + modelname):
        print("Skipping model " + modelprogress + " - existing directory '.../" + modelname + "/'")
        continue

    os.makedirs(os.getcwd() + "\\" + modelname)     # make subfolder in directory this script is located in

    print("Downloading model " + modelprogress + " (" + modelname + ") .../" + str(listitem))
    download(weburl + str(listitem), "tempfile.html")   # download the model directory page

    # the image URLs are kept in <script type="text/javascript"> part of the HTML, this sets up scraping
    tempfilehtml = open("tempfile.html")
    soup = bs4.BeautifulSoup(tempfilehtml, "html.parser")
    jsdata = soup.find("script", type="text/javascript").text
    pattern = r"//nebula.wsimg.com/\S+?&disposition=0&alloworigin=1"    # unsure how to do this without regex
    photoURLs = re.findall(pattern, jsdata)

    # set up threading so that multiple images can download at once
    threadlist = []
    i = 0
    for item in photoURLs:
        i = i + 1
        threadapp = threading.Thread(None, download, None, ("http:" + str(item), modelname + "\\" + str(i) + ".jpg"))
        threadlist.append(threadapp)

    print("Downloading model " + modelprogress + " (" + modelname + ") photos - " + str(len(photoURLs)) + " images")
    for x in threadlist:    # starts all the threads in threadlist
        x.start()

    for x in threadlist:    # waits for all the threads to finish
        x.join()

    tempfilehtml.close()    # file cleanup

os.remove("tempfile.html")

print("Croquis_Collector complete.")
