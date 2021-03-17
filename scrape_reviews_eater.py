import ast, json, string, operator, re, os, time, pickle, requests
import argparse as ap
from bs4 import BeautifulSoup
from urllib.request import urlopen
from scrape_comments import read_user
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


#Get text from an individual Eater article url
#Helper function for scrape_eater_data
def scrape_eater_article(article_url):
    r = requests.get(article_url)
    encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(r.content, "lxml")
    texts = soup.find('div', attrs={'class' : 'c-entry-content'}).find_all('p')
    output_text = ""
    for text in texts:
        output_text = output_text + " " + text.get_text()
    return(output_text)

#Get text
def scrape_eater_data(restaurant_tag):
    #Open browser in incognito
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("http://www.google.com")

    #Locate TripAdvisor webpage
    #First google search
    elem = driver.find_element_by_name("q")
    elem.clear()
    search_string = "Eater " + restaurant_tag.replace("-"," ")
    elem.send_keys(search_string)
    elem.send_keys(Keys.RETURN)

    #Now click the proper web link
    elem1 = driver.find_element_by_xpath("//h3[@class='LC20lb']")
    parent = elem1.find_element_by_xpath("..")
    google_url = parent.get_attribute("href")

    #Running through Eater search results
    i = 0
    #article_links = []
    article_texts = []
    #print("Max 32 Results per Page")
    while(True):
        i +=1
        print("Page: " + str(i))
        suffix = "/" + str(i)
        url = google_url + suffix
        print(url)
        r = requests.get(url)
        encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
        soup = BeautifulSoup(r.content, "lxml")
        links = soup.findAll('a', attrs = {'data-analytics-link' : 'article'})
        num_links = len(links)
        if(num_links < 1):
            print("break")
            break
        k = 0
        for link in links:
            k += 1
            print(str(k) + " of " + str(num_links))
            #article_links.append(str(link['href']))
            article_texts.append(scrape_eater_article(link['href']))

    driver.close()
    return(article_texts)

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-s', '--search_query', help='Search Query', default='girl-and-the-goat-chicago')

    args = vars(parser.parse_args())
    search_query = args['search_query']
    print(scrape_eater_data(search_query))
