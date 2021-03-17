from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import argparse as ap
import os, json, requests, shutil
from menu_from_db import extract_json, save_locally
from save_sentences_csv import items_in_sentence, optimize_list, read_items
import pandas as pd
from urllib.request import urlretrieve


def run_postmates_image_scraper(postmates_code, foodie_id):
    #Opening proper webpage
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)

    wiki = "https://postmates.com/merchant/" + postmates_code
    driver.get(wiki)
    n = 0

    script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
    path = script_dir + "/csvfiles/images/" + foodie_id + "-images-postmates/"
    exceptions = ['a', 'an', 'of', 'the', 'is', 'with', 'or', 'and', 'to', 'from'] + foodie_id.split('-')
    
    
    # menu_items = read_items(script_dir, foodie_id)
    json = extract_json(foodie_id)
    menu_items = save_locally(json, foodie_id)

    foodie_ids = []
    items = []
    filenames = []
    matches = []

    elements = driver.find_elements_by_xpath("//div[@class='product-container css-2ko7m4 e1tw3vxs3']")
    for element in elements:
        item_name = element.find_element_by_xpath(".//h3[@class='product-name css-1yjxguc e1tw3vxs4']").get_attribute("innerText")
        
        matched_items = items_in_sentence(item_name, menu_items, 2, foodie_id, exceptions)
        if(len(matched_items) == 0):
            continue     

        imgs = element.find_elements_by_xpath(".//img[@class='css-1hyfx7x e1qfcze94']")
        for img in imgs:
            img_src = img.get_attribute("src")
            print(img_src)

            optimized_items = optimize_list(matched_items, item_name.lower())
            print(optimized_items)
            for item in optimized_items:

                if n == 0:
                    print("test")
                    try: os.makedirs(path)
                    except OSError: pass

                filename = foodie_id + "-" + str(n) + ".jpg"
                
                webp_finder = img_src.find('format=webp')
                print(webp_finder)
                img_src = img_src[:webp_finder]
                print(img_src)
                save_img_url(img_src, path + filename)
                
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

def save_img_url(img_url, location):
    r = requests.get(img_url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
    if r.status_code == 200:
        with open(location, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-s', '--postmates_code', help='Postmates Restaurant Code', default='aloha-poke-co-chicago-4')
    parser.add_argument('-f', '--foodie_id', help='Foodie ID', default='aloha-poke-chicago-131')

    args = vars(parser.parse_args())
    postmates_code = args['postmates_code']
    foodie_id = args['foodie_id']
    run_postmates_image_scraper(postmates_code, foodie_id)
