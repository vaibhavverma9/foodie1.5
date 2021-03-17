import ast, json, string, operator, re, os, time, pickle, requests
import argparse as ap
from bs4 import BeautifulSoup
from urllib.request import urlopen
from scrape_comments import read_user
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time, random

proxy_choices = ['us-wa.proxymesh.com:31280', 'nl.proxymesh.com:31280','sg.proxymesh.com:31280']

# Counts the total number of reviews for a restaurant
def count(yelp_id):
    url = "https://www.yelp.com/biz/" + yelp_id  + "?start=0" # URL of restaurant's yelp page    
    
    r = requests.get(url)
    if(r.status_code != 200):
        r = rotate_proxies(url)
    encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(r.content, from_encoding=encoding) # BeautifulSoup produces HTML of webpage
    print(soup)

    json_texts = soup.find_all("script", attrs={"type" : "application/ld+json"})
    for json_text in json_texts:
        jsn = json.loads(json_text.getText())
        if 'aggregateRating' in jsn:
            n_of_reviews = jsn['aggregateRating']['reviewCount']
            return n_of_reviews, yelp_id
    return 0, yelp_id

def rotate_proxies(url):
    print("rotating proxies")
    for proxy in proxy_choices:
        try:
            print(proxy)

            proxy = 'jameseats:jamestheeater@' + proxy

            proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy}         
            print(proxies)
            r = requests.get(url, proxies=proxies)
            print(r.status_code)
            if(r.status_code == 200):
                print("returning")
                return r
        except Exception as e: print(e)

    return ''

# Scraps review data
def scrap_data(yelp_id, reviewCount, n, nmax):
    output = []
    count = n

    while(n < reviewCount and n < nmax + count):
        url = "https://www.yelp.com/biz/" + yelp_id + "?start=" + str(n)
        r = requests.get(url)
        if(str(r.status_code) != '200'):
            r = rotate_proxies(url)

        encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
        soup = BeautifulSoup(r.content, from_encoding=encoding) # BeautifulSoup produces HTML of webpage

        json_texts = soup.find_all("script", attrs={"type" : "application/ld+json"})
        for json_text in json_texts:
            jsn = json.loads(json_text.getText())

            if('review' in jsn):
                reviews = jsn['review']
                for review in reviews:
                    output.append(review['description'])
        n += 20
        print(n)
    return output

def scrape_yelp_data(yelp_id, n):
	reviewCount, yelp_id = count(yelp_id)
	output = scrap_data(yelp_id, reviewCount, 0, n)
	return output

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-y', '--yelp_id', help='Yelp ID', default='girl-and-the-goat-chicago')
    parser.add_argument('-n', '--n', help='n', default='100')

    args = vars(parser.parse_args())
    yelp_id = args['yelp_id']
    n = int(args['n'])

    scrape_yelp_data(yelp_id, n)
