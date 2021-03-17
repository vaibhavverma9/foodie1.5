import argparse as ap
import requests, json, os 
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from menu_from_db import extract_json, save_locally
from save_sentences_csv import items_in_sentence, optimize_list
import ast, pickle
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd

def pull_items(caviar_id, foodie_id):
	#Open browser in incognito
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)

    wiki = "https://www.trycaviar.com/" + caviar_id
    driver.get(wiki)

    #Logistics
    output = []

    #Click on reviews
    containers = driver.find_elements_by_xpath("//div[@class='merchant-menu-category']")
    for container in containers:
    	category = container.find_element_by_xpath("//h3[@class='merchant-menu-category_header']").get_attribute("innerText").title()
    	category_details = container.find_element_by_xpath("//div[@data-react-class='OfferTilesContainer']")
    	detail_json = json.loads(category_details.get_attribute('data-react-props'))
    	for dish in detail_json['offers']:
    		name = dish['name']
    		price = dish['price']
    		description = dish['description']
    		output.append([name, description, price, category, ""])
    print(output)
    return output

def write_menu(menu_items, foodie_id):
    script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
    foodie_id = foodie_id.replace('/', '-')
    foodie_id = foodie_id.replace(',', '')
    print("Saving menu items at " + script_dir + "/output_menu_items/foodie/" + foodie_id + ".txt")
    with open(script_dir + "/output_menu_items/foodie/" + foodie_id + ".txt", 'wb') as f:
        pickle.dump(menu_items, f)

def scrape_caviar_menus(caviar_id, foodie_id):
    output = {}
    output['Food'] = pull_items(caviar_id, foodie_id)
    write_menu(output, foodie_id)
    return True

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-f', '--foodie_id', help="FoodieID", default="souvla-san-francisco-512")
    parser.add_argument('-c', '--caviar_id', help="CaviarID", default="san-francisco/souvla--hayes-632")

    args = vars(parser.parse_args())
    foodie_id = args['foodie_id']
    caviar_id = args['caviar_id']
    run_caviar_menu_scraper(caviar_id, foodie_id)
