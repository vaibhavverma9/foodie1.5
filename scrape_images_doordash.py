from bs4 import BeautifulSoup
import argparse as ap
import pandas as pd
import requests, os, pickle, json
from slimit import ast  # $ pip install slimit
from slimit.parser import Parser as JavascriptParser
from slimit.visitors import nodevisitor
from save_sentences_csv import items_in_sentence, optimize_list
from menu_from_db import extract_json, save_locally
from urllib.request import urlretrieve

#Logistics
script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
foodie_ids = []
items = []
filenames = []
matches = []
source_ids = []

def pull_doordash_html(doordash_code):
    url = 'https://www.doordash.com/store/' + doordash_code
    r = requests.get(url)
    encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(r.content, "lxml") # BeautifulSoup produces HTML of webpage
    return(soup)

def scrape_doordash_images(doordash_code, foodie_id):
    print("DoordashID:", doordash_code)
    if(doordash_code == ""):
        return False

    soup = pull_doordash_html(doordash_code)
   
    clean_soup = soup.find_all('script')[8].get_text().split("\"")[1]
    clean_soup = clean_soup.replace("\\u0022","\"").replace("\\u002D", "-")
    json_data = json.loads(clean_soup)
    path = script_dir + "/csvfiles/images/" + foodie_id + "-images-doordash/"    
    try: os.makedirs(path)
    except OSError: pass
    exceptions = ['a', 'an', 'of', 'the', 'is', 'with', 'or', 'and', 'to', 'from'] + foodie_id.split('-')
    json_menu = extract_json(foodie_id)
    menu_items = save_locally(json_menu, foodie_id)
    n = 0

    for category in json_data['current_menu']['menu_categories']:
        title = category['title']
        cat_items = category['items']
        for item in cat_items:
            image_name = item['name']
            image_url = item['image_url']
            if image_url == None:
                continue

            matched_items = items_in_sentence(image_name, menu_items, 2, foodie_id, exceptions)
            if(len(matched_items) == 0):
                continue

            optimized_items = optimize_list(matched_items, image_name.lower())
            print(optimized_items)
            for optimized_item in optimized_items:
                filename = foodie_id + "-" + str(n) + ".jpg"
                urlretrieve(image_url, path + filename)
                foodie_ids.append(foodie_id)
                items.append(optimized_item)
                filenames.append(filename)
                matches.append(image_name)
                source_ids.append(doordash_code)
                n += 1
    
    d = {'FoodieID' : foodie_ids, 'Item' : items, 'Filename' : filenames, 'Matches' : matches, 'DoordashID' : source_ids}
    df = pd.DataFrame(d)
    df.to_excel(path + foodie_id + ".xlsx", sheet_name='Sheet1', encoding="utf8", index=False)
            
if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-d', '--doordash_code', help='DoorDash Code', default='de-rice-asian-cuisine-chicago-7980')
    parser.add_argument('-f', '--foodie_id', help='Foodie Code', default="de-rice-asia-n-chicago")

    args = vars(parser.parse_args())
    doordash_code = args['doordash_code']
    foodie_id = args['foodie_id']
    scrape_doordash_images(doordash_code, foodie_id)
