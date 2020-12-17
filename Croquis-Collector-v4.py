# version 4 for smugmug

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import requests
from urllib.parse import unquote
from PIL import Image

import time
import re
import os


def download(url, file_name):
    with open(file_name, "wb") as file:     # open in binary mode
        response = requests.get(url)        # get request
        file.write(response.content)        # write to file
        file.close()                        # close file


def safe_download(url, file_name):
    sleep_time = 30     # seconds between retry attempts
    retry_attempts = 20
    retry = True
    retry_count = 0
    while retry:        # allows for unstable internet connection when downloading
        try:
            download(url, file_name)
            retry = False
        except:
            time.sleep(sleep_time)
            retry_count += 1
            if retry_count >= retry_attempts:
                retry = False


# settings - tested with selenium using the geckodriver
geckoDriverPath = r'geckodriver.exe'
baseDir = os.getcwd()   # sub-folders will be created for each album
specificAlbums = []     # replace with list of strings of album names if desired, will analyse only those albums
recentAlbums = 0        # number of (most recently updated) albums to analyse, 0 for all, suggest 10 for weekly updates
reduceSize = True       # change to false to keep original images (WARNING, 2GB database size WITH default reduction)
reductionRatio = 0.66   # will reduce jps with width or height over 3000 by this factor, default = 0.66
quality = 60            # quality to save jps default = 60 (defaults optimise most images to ~350KB, ~2% of original)
# end of settings

baseDir = baseDir + os.path.sep
# set up selenium and login to database
driver = webdriver.Firefox(executable_path=geckoDriverPath, timeout=180)
baseUrl = "https://modelindexdatabase.smugmug.com/Croquis-Cafe-Model-Photo-Database/"
print("Navigating to", baseUrl)
driver.set_window_size(1080, 4000000)      # hugely long window forces site js script to load all images immediately
driver.get(baseUrl)
driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.TAB)
password = driver.find_element_by_name("password")
password.clear()
password.send_keys("ENTER")     # password for site
driver.find_element_by_class_name("sm-button-label").find_element_by_xpath("..").click()

# press END key until last link loads (which has the my-homepage-slideshow link)
pageLoaded = False
hrefLinks = []
print("Finding albums of images")
while not pageLoaded:   # in case window is resized, alternative method of getting to bottom of page
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # 30 second timeout
    driver.find_element_by_tag_name('body').send_keys(Keys.END)
    aTags = driver.find_elements_by_tag_name('a')
    for tag in aTags:
        href = tag.get_attribute('href')
        if href is not None and baseUrl in href and href not in hrefLinks:
            hrefLinks.append(href)
    if baseUrl + "My-Homepage-Slideshow" in hrefLinks:  # my-homepage-slideshow last album in database
        pageLoaded = True
    else:
        time.sleep(1)

# cycle through each album and collect the links to the photos
imgLinks = []
imgUrl = "https://photos.smugmug.com/Croquis-Cafe-Model-Photo-Database/"
for href in hrefLinks:
    if recentAlbums and hrefLinks.index(href) >= recentAlbums:     # will only search the first x albums in the database
        break
    elif specificAlbums:      # to only download the specified albums in the list
        skipAlbum = True
        for album in specificAlbums:
            if album in href:
                skipAlbum = False
                break
        if skipAlbum:
            continue
    if "My-Homepage-Slideshow" in href:     # no point downloading the teaser album
        continue
    print("\rAnalysing album " + str(hrefLinks.index(href) + 1) + " of " + str(len(hrefLinks)), end=" ")
    pageLoaded = False
    while not pageLoaded:   # to ensure driver.get retries on bad internet connections
        try:
            driver.get(href)
            pageLoaded = True
        except TimeoutException:
            pageLoaded = False    # doing nothing will make it try again as pageLoaded
    time.sleep(2)   # site javascript takes some time to initiate
    pageLoaded = False
    while not pageLoaded:   # in case window is resized, scroll down
        try:    # press end a few times to get to the end of page, if progess spinner visible, repeat
            for x in range(1, 10):
                time.sleep(0.1)
                driver.find_element_by_tag_name('body').send_keys(Keys.END)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sm-progress-spinner-visible")))
        except TimeoutException:    # page fully loaded - probably
            imgTags = driver.find_elements_by_tag_name('img')
            for tag in imgTags:
                src = tag.get_attribute("src")
                if src is not None and imgUrl in src and src not in imgLinks and \
                        "onate" not in src and "ledge" not in src:    # donate/pledge graphics excluded
                    imgLinks.append(src)
            pageLoaded = True
driver.quit()
print("\nSite analysis complete")

# format of each item [album, filename, https://link], string manipulation heavy to find each from link
downloadList = []
for link in imgLinks:
    # collected links end: /Bebe/i-PdrDcSr/0/f6739d1a/M/Bebe%209-M.jpg the /M/ -> /O/ and -M need to be removed
    pattern = r"-.{1,5}\.jpg$"      # from the last '-' to '.jpg' at the end of string
    downloadLink = re.sub(pattern, r".jpg", link)  # remove the -M from -M.jpg
    pattern = r"/[^0]{1,2}/[^/]*$"  # find the /M/ or /XL/ etc in the last '/.../' before end of string
    result = re.search(pattern, downloadLink)
    # replace the /L/ or /M/ etc with /O/ by splitting the /M/...jpg out and making the edit to that
    # smaller sizes available than /D/ or /O/ largest, /5K/, /4K/, /2XL/, /XL/
    downloadLink = re.sub(pattern, re.sub(r"/.*/", r"/O/", result.group(0)), downloadLink)
    # find filename from download link
    filename = unquote(downloadLink)
    pattern = r"[^/]*$"  # matches from chr after last '/' till end of string
    filename = re.search(pattern, filename)
    filename = filename.group(0)
    pattern = r"/Croquis-Cafe-Model-Photo-Database/[^/]*/"   # string before album name
    albumName = re.search(pattern, downloadLink)
    albumName = albumName.group(0)
    albumName = albumName.replace("/Croquis-Cafe-Model-Photo-Database/", "")
    albumName = albumName.replace("/", "")
    albumName = unquote(albumName)
    ident = os.path.join(albumName, filename)   # used below for finding duplicate named files in same album
    for item in downloadList:    # I'm bad at list comprehension
        if ident == item[3]:     # the use of duplicate file names in same album seems affect only the odd older album
            filename = filename.replace(".jpg", "a.jpg")  # first duplicate becomes filea.jpg, second fileaa.jpg etc
            ident = os.path.join(albumName, filename)
    downloadList.append([albumName, filename, downloadLink, ident])

# get list of existing jpgs in final folder so as not to redownload existing
existingJpgs = []
for root, dirs, files in os.walk(baseDir):
    for file in files:
        if file.endswith("_min.jpg") or file.endswith(".jpg"):
            # makes the format of each string album/filename.jpg to remove error of not downloading duplicate filenames
            existingJpgs.append(os.path.join(root.replace(baseDir, ""), file.replace("_min.jpg", ".jpg")))

# check if files already exist, don't download those that do, download and minimise others
for listItem in downloadList:
    filename = listItem[1]
    albumName = listItem[0]
    if os.path.join(albumName, filename) not in existingJpgs:  # check to ensure it doesn't already exist
        link = listItem[2]
        folderPath = baseDir + albumName + os.path.sep
        path = folderPath + filename
        if not os.path.exists(folderPath):      # folder may not exist, create it
            os.mkdir(folderPath)
        print("\rDownloading image " + str(downloadList.index(listItem) + 1) + " of " + str(len(downloadList)),
              "(" + albumName + ")\t\t\t", end=" ")
        safe_download(link, path)
        try:        # reduce image file size if specified
            img = Image.open(path)
            width, height = img.size
            if width > 3000 or height > 3000:   # image size
                width = int(round(width * reductionRatio))
                height = int(round(height * reductionRatio))
                img = img.resize((width, height), Image.ANTIALIAS)
            if os.stat(path).st_size > 350000 and reduceSize:  # file size larger than 350KB
                img.save(path.replace(".jpg", "_min.jpg"), optimize=reduceSize, quality=quality)
                os.remove(path)
            elif reduceSize:   # already below the min size and file optimisation required
                os.rename(path, path.replace(".jpg", "_min.jpg"))
        except:
            continue
