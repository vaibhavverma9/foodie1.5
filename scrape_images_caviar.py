import argparse as ap
import requests, json, os 
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from menu_from_db import extract_json, save_locally
from save_sentences_csv import items_in_sentence, optimize_list, read_items
import ast 
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd

def run_caviar_image_scraper(caviar_id, foodie_id):
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
    script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
    path = script_dir + "/csvfiles/images/" + foodie_id + "-images-caviar/"
    exceptions = ['a', 'an', 'of', 'the', 'is', 'with', 'or', 'and', 'to', 'from'] + foodie_id.split('-')

    # menu_items = read_items(script_dir, foodie_id)
    json = extract_json(foodie_id)
    if(json['Items'] == []):
        return 'Could not pull images from database. Potential FoodieID mismatch.'
    menu_items = save_locally(json, foodie_id)

    foodie_ids = []
    source_ids = []
    items = []
    filenames = []
    matches = []
    n = 0

    #Click on reviews
    dishes = driver.find_elements_by_xpath("//a[@class='js-offer-link offer-tile_link']")
    dishes = dishes + driver.find_elements_by_xpath("//a[@class='js-offer-link offer-tile_link offer-tile_link--unavailable']")
    dish_links = []
    for dish in dishes:
        dish_link = dish.get_attribute("href")
        dish_links.append(dish_link)

    for dish_link in dish_links:
        driver.get(dish_link)
        item_name = driver.find_element_by_xpath("//h1[@class='item_name']").text
        item_img_srcset = driver.find_elements_by_xpath("//img[@class='item_image']")
        if(item_img_srcset == []):
            continue

        print(item_name)
        print(item_img_srcset)

        item_img_srcset = item_img_srcset[0].get_attribute("srcset").split()
        img_src = item_img_srcset[len(item_img_srcset) - 2]
        
        matched_items = items_in_sentence(item_name, menu_items, 2, foodie_id, exceptions)
        if(len(matched_items) == 0):
            continue     

        optimized_items = optimize_list(matched_items, item_name.lower())
        for item in optimized_items:
            if n == 0:
                try: os.makedirs(path)
                except OSError: pass

            filename = foodie_id + "-" + str(n) + ".jpg"
            urlretrieve(img_src, path + filename)

            foodie_ids.append(foodie_id)
            items.append(item)
            filenames.append(filename)

            matches.append(item_name)
            n += 1
            print(n)

    driver.close()
    if n > 0:
        d = {'FoodieID' : foodie_ids, 'Item' : items, 'Filename' : filenames, 'Matches' : matches}
        df = pd.DataFrame(d)
        df.to_excel(path + foodie_id + ".xlsx", sheet_name='Sheet1', encoding="utf8", index=False)
        return 'Added Caviar Imgs'
    else:
        return 'No Caviar Imgs Scraped'

def pull_content(caviar_id, foodie_id):
    wiki = "https://www.trycaviar.com/" + caviar_id
    # print(wiki)
    r = requests.get(wiki)
    encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(r.content, from_encoding=encoding) # BeautifulSoup produces HTML of webpage
    # print(soup)

	# foodie_ids = []
	# items = []
	# filenames = []
	# matches = []

	# exceptions = ['a', 'an', 'of', 'the', 'is', 'with', 'or', 'and', 'to', 'from'] + foodie_id.split('-')
	# json = extract_json(foodie_id)
	# menu_items = save_locally(json, foodie_id)
	# script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	# path = script_dir + "/csvfiles/images/" + foodie_id[:100] + "-images-caviar/"
	# try: os.makedirs(path)
	# except OSError: pass

	# for container in soup.find_all("div", attrs={"data-react-class" : "OfferTilesContainer"}):
	# 	# print(ast.literal_eval(str(container.get('data-react-props'))))

	# 	for dish in container.get('data-react-props'):
	# 		image_name = dish['name']
	# 		image_url = dish['imageSet'][0]['hidpi']

	# 		matched_items = items_in_sentence(image_name, menu_items, 2, foodie_id, exceptions)
	# 		if(len(matched_items) == 0):
	# 			continue

	# 		optimized_items = optimize_list(matched_items, image_name.lower())
	# 		for item in optimized_items:
	# 			filename = foodie_id + "-" + str(n) + ".jpg"
	# 			urlretrieve(link, path + filename)

	# 			foodie_ids.append(foodie_id)
	# 			items.append(item)
	# 			filenames.append(filename)
	# 			matches.append(image_name)
	# 			n += 1

	# 	d = {'FoodieID' : foomanchi-new-york-221die_ids, 'Item' : items, 'Filename' : filenames, 'Matches' : matches}
	# 	df = pd.DataFrame(d)
	# 	df.to_excel(path + foodie_id[:100] + ".xlsx", sheet_name='Sheet1', encoding="utf8", index=False)

	# return n 

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-f', '--foodie_id', help="FoodieID", default="souvla-san-francisco-512")
    parser.add_argument('-c', '--caviar_id', help="CaviarID", default="san-francisco/souvla--hayes-632")

    args = vars(parser.parse_args())
    foodie_id = args['foodie_id']
    caviar_id = args['caviar_id']
    run_caviar_image_scraper(caviar_id, foodie_id)
