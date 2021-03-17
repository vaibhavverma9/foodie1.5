import ast, json, string, operator, re, os, time, pickle, requests
import argparse as ap
from bs4 import BeautifulSoup
from urllib.request import urlopen
from scrape_comments import read_user
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import numpy as np

CLICK_PAUSE_TIME = .5

def scrape_restaurants():
    wiki = "https://www.yelp.com/search?find_desc=Restaurants&find_loc=East%20Village%2C%20Manhattan%2C%20NY&sortby=review_count"

    #Open browser in incognito
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(wiki)
    
    time.sleep(CLICK_PAUSE_TIME*6)

    restaurant_cells = driver.find_elements_by_xpath("//div[@class=' container__09f24__21w3G hoverable__09f24__2nTf3 margin-t3__09f24__5bM2Z margin-b3__09f24__1DQ9x padding-t3__09f24__-R_5x padding-r3__09f24__1pBFG padding-b3__09f24__1vW6j padding-l3__09f24__1yCJf border--top__09f24__1H_WE border--right__09f24__28idl border--bottom__09f24__2FjZW border--left__09f24__33iol border-color--default__09f24__R1nRO']")
    for restaurant_cell in restaurant_cells:
        name = restaurant_cell.find_element_by_xpath("//a[@class=' link__09f24__1MGLa link-color--inherit__09f24__3Cplm link-size--inherit__09f24__3Javq']")
        href = name.get_attribute('href')
        print(href)

if __name__ == '__main__':
    scrape_restaurants()