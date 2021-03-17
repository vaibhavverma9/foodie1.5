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

def scrape_googlereviews_data(search_query, max_count):
    max_count = max_count * 2

    #Open browser in incognito
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("http://www.google.com")

    #First google search
    elem = driver.find_element_by_name("q")
    elem.clear()
    search_string = "Google Reviews " + search_query.replace("-"," ")
    elem.send_keys(search_string)
    elem.send_keys(Keys.RETURN)

    #Click on reviews
    reviewbutton = driver.find_element_by_xpath("//span[@jsl='$t t-h6pVaOIWfNg;$x 0;']")
    reviewbutton.get_attribute('data-ved')
    reviewbutton.click()
    time.sleep(CLICK_PAUSE_TIME*6)

    #Scroll down review window to load all reviews
    #   Finding a focusable element so that we can scroll
    try:
        focusable = driver.find_element_by_xpath("//button[@jsaction='r.GnCZFN8m9d0']")
    except:
        print("Too Fast")
        time.sleep(CLICK_PAUSE_TIME*8)
        focusable = driver.find_element_by_xpath("//button[@jsaction='r.GnCZFN8m9d0']")

    scrolls = int(np.ceil(max_count/10)+1)
    for i in range(0,scrolls):          #Collects the first 200 (10 per loop)
        focusable.send_keys(Keys.END)
        time.sleep(CLICK_PAUSE_TIME)

    #Expand all of the reviews
    #Note that the last several reviews may not be expanded
    #Because expanding the reviews actually loads a few more reviews 
    expand_buttons = driver.find_elements_by_xpath("//a[@class='fl review-more-link']")
    for button in expand_buttons:
        try:
            button.click()
        except:
            print("button already printed?")

    #Extract all review elements
    reviews = driver.find_elements_by_xpath("//span[@jsl='$t t-uvHqeLvCkgA;$x 0;']")

    #Extract text from reviews
    output = []
    for review in reviews:
        if(review.text != ''):
            output.append(review.text)

    #Close the driver
    driver.close()

    #Return our texts
    print(len(output)) 
    return output

def scrape_google_description(search_query):
    #Open browser in incognito
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("http://www.google.com")

    #First google search
    elem = driver.find_element_by_name("q")
    elem.clear()
    search_string = search_query.replace("-"," ")
    elem.send_keys(search_string)
    elem.send_keys(Keys.RETURN)

    try:
        description_span = driver.find_element_by_xpath("//span[@class='Yy0acb']")
        print(description_span)
        description = description_span.text
        print(description)
    except: 
        description = ''

    #Close the driver
    driver.close()

    #Return our texts
    return description

def scrape_google_hours_spent(search_query):
    #Open browser in incognito
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("http://www.google.com")

    #First google search
    elem = driver.find_element_by_name("q")
    elem.clear()
    search_string = search_query.replace("-"," ")
    elem.send_keys(search_string)
    elem.send_keys(Keys.RETURN)

    hours_div = driver.find_element_by_xpath("//div[@class='UYKlhc']")
    print(hours_div)
    hours = hours_div.find_element_by_xpath(".//b").text
    print(hours)

    #Close the driver
    driver.close()

    #Return our texts
    return hours

if __name__ == '__main__':
    scrape_google_description('Girl and the Goat Chicago')
    # parser = ap.ArgumentParser()
    # parser.add_argument('-s', '--search_query', help='Search Query', default='girl-and-the-goat-chicago')
    # parser.add_argument('-n', '--n', help='Max Count', default='200')

    # args = vars(parser.parse_args())
    # search_query = args['search_query']
    # n = int(args['n'])
    # scrape_googlereviews_data(search_query, n)
    