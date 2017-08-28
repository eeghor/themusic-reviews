from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import sys
from datetime import datetime
import json
from selenium.webdriver.common.keys import Keys
from unidecode import unidecode
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
import requests
from bs4 import BeautifulSoup
from collections import defaultdict


now = datetime.now()
year, month, day = now.year, now.month, now.day

reviews = []

album_review_urls = set()

BASE_PAGE = "http://themusic.com.au/music/album-reviews"
WAIT_TIME = 60
driver = webdriver.Chrome('webdriver/chromedriver')

driver.get(BASE_PAGE)

# wait for the pagination bar
pagination_ul = WebDriverWait(driver, WAIT_TIME).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "pagination")))

last_page = int(pagination_ul.find_elements_by_xpath(".//li[@class='control']/a")[-1].get_attribute("href").split("=")[-1])
print("total available pages: {}".format(last_page))

def collect_headline_review_urls():
    # assuming we're on the right page
    this_page_urls = set()
    for a in driver.find_elements_by_xpath("//div[@id='albumReviewsHeadlines']/div[@class='row']/div[contains(@class, 'featureItem') or contains(@class, 'item')]/a"):
        this_page_urls.add(a.get_attribute("href"))
    #print("found {} album review links on this page".format(len(this_page_urls)))

    return this_page_urls

def collect_review_urls():
    # assuming we're on the right page
    this_page_urls = set()
    for a in driver.find_elements_by_xpath("//div[@id='albumReviewsList']/div[@class='row']/div[contains(@class, 'featureItem') or contains(@class, 'item')]/a"):
        this_page_urls.add(a.get_attribute("href"))
    #print("found {} album review links on this page".format(len(this_page_urls)))

    return this_page_urls


# print("on page 1, notmal reviews {}, featured {}".format(len(collect_review_urls()), len(collect_headline_review_urls())))

album_review_urls.update(collect_headline_review_urls())
album_review_urls.update(collect_review_urls())
print("reviews on the first page: {}".format(len(album_review_urls)))

last_page = 1
for i in range(2, last_page + 1):

    driver.get(BASE_PAGE + "/?page=" + str(i))

    print("now on {}".format(driver.current_url))

    # wait unitl that pagination bar is visible
    WebDriverWait(driver, WAIT_TIME).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "pagination")))

    album_review_urls.update(collect_review_urls())

    if (i%10 == 0) or (i == last_page):
        print("links collected so far: {}".format(len(album_review_urls)))


driver.quit()

for rl in album_review_urls:


    print(rl)
    GOT_PAGE = False

    while not GOT_PAGE:

        try:
            soup = BeautifulSoup(requests.get(rl, timeout=30).content, "lxml")
            GOT_PAGE = True
        except:
            print("requests couldn\'t get a page, retrying...")
            time.sleep(3)

    this_review = defaultdict()

    try:
        this_review["review_artist"] = unidecode(soup.find("h1", itemprop = 'itemReviewed'))
        print(this_review["review_artist"])
    except:
        this_review["review_artist"] = None