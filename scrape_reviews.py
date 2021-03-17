import ast, json, string, operator, re, os, time, pickle, requests
import argparse as ap
from bs4 import BeautifulSoup
from urllib.request import urlopen
from scrape_comments import read_user
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from scrape_reviews_yelp import scrape_yelp_data
from scrape_reviews_tripadvisor import scrape_tripadvisor_data
from scrape_reviews_googlereviews import scrape_googlereviews_data

def read_reviews(script_dir, foodie_id):
    with open(script_dir + "/output_reviews/" + foodie_id + ".txt", 'r') as f:
        output = json.load(f)
    return output

def save_reviews(script_dir, foodie_id, output):
    with open(script_dir + "/output_reviews/" + foodie_id + ".txt", 'wb') as f:
        pickle.dump(output, f)    

def run_scrape_reviews(foodie_id, yelp_id, query, n):
    script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
    output_tripadvisor = []
    output_yelp = []
    output_googlerviews = []
    output_search_links = []

    # print("TripAdvisor scraping reviews")
    # try:
    #     output_tripadvisor = scrape_tripadvisor_data(query, n)
    # except:
    #     pass

    # try:
    #     output_search_links = scrape_reviews_by_search(query)
    # except:
    #     pass

    print("Yelp scraping reviews")
    try:
        output_yelp = scrape_yelp_data(yelp_id, n)
    except:
        pass

    print("Google scraping reviews")
    try:
        output_googlerviews = scrape_googlereviews_data(query, n)
    except:
        pass

    output = output_tripadvisor + output_yelp + output_googlerviews 
    save_reviews(script_dir, foodie_id, output)
    print("Total Review Count:", len(output))
    print("TripAdvisor Review Count:", len(output_tripadvisor))
    print("Yelp Review Count:", len(output_yelp))
    print("Google Review Count:", len(output_googlerviews))
    
    return True

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-f', '--foodie_id', help='Foodie ID', default='girl--the-goat-chicago-807')
    parser.add_argument('-y', '--yelp_id', help='Yelp ID', default='girl-and-the-goat-chicago')
    parser.add_argument('-q', '--query', help='Search query on Google', default='Girl and the Goat Chicago')
    parser.add_argument('-n', '--n', help='Max Count', default='100')

    args = vars(parser.parse_args())
    foodie_id = args['foodie_id']
    yelp_id = args['yelp_id']
    query = args['query']
    n = int(args['n'])


    run_scrape_reviews(foodie_id, yelp_id, query, n)