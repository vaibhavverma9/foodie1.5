import argparse as ap
import requests, json, os , pickle
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from menu_from_db import extract_json, save_locally
from save_sentences_csv import items_in_sentence, optimize_list, read_items
import ast 
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd

def scrape_menu(caviar_id, foodie_id):
	#Open browser in incognito
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)

    wiki = "https://www.trycaviar.com/" + caviar_id
    print(wiki)
    driver.get(wiki)

    menu_items = {}
    menu_items['Food'] = []

    close_elements = driver.find_elements_by_xpath("//i[@class='icon-modal-close']")
    if(len(close_elements) > 0):
        close_element = close_elements[0]
        close_element.click()

    sections = driver.find_elements_by_xpath("//section[@class='merchant-menu-category']")
    for section in sections:
        print("----")
        category = section.find_element_by_xpath(".//h3[@class='merchant-menu-category_header']").text
        print(category)
        dishes = section.find_elements_by_xpath(".//a[@class='js-offer-link offer-tile_link']") + section.find_elements_by_xpath(".//a[@class='js-offer-link offer-tile_link offer-tile_link--unavailable']")
        for dish in dishes:
            item_name = dish.find_element_by_xpath(".//h4[@class='offer-tile_name']").text
            print(item_name)
            descriptions = dish.find_elements_by_xpath(".//p[@class='offer-tile_description']")
            if(len(descriptions) == 1):
                description = descriptions[0].text
            else:
                description = ''
            prices = dish.find_elements_by_xpath(".//span[@class='offer-tile_price offer-tile_price--unavailable']") + dish.find_elements_by_xpath(".//span[@class='offer-tile_price']")
            if(len(prices) > 0):
                price = prices[0].text
            else:
                price = ''

            menu_items['Food'].append([item_name, description, price, category, '', ''])

    return menu_items

# Save menu_items as a file using pickle library (not necessarily human readable)
def write_menu(menu_items, restaurant_tag):
    script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
    with open(script_dir + "/output_menu_items/foodie/" + restaurant_tag + ".txt", 'wb') as f:
        pickle.dump(menu_items, f)

def scrape_caviar_menu(caviar_id, foodie_id):
    menu_items = scrape_menu(caviar_id, foodie_id)
    write_menu(menu_items, foodie_id)

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-f', '--foodie_id', help="FoodieID", default="souvla-san-francisco-512")
    parser.add_argument('-c', '--caviar_id', help="CaviarID", default="san-francisco/souvla--hayes-632")

    args = vars(parser.parse_args())
    foodie_id = args['foodie_id']
    caviar_id = args['caviar_id']
    scrape_caviar_menu(caviar_id, foodie_id)
