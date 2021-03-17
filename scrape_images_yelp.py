import argparse as ap
from bs4 import BeautifulSoup
from menu_from_db import extract_json, save_locally
from urllib.request import urlopen
import requests, json, time, random, os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from save_sentences_csv import items_in_sentence, optimize_list, read_items
import pandas as pd
from urllib.request import urlretrieve

def pull_yelp_images(restaurantTag, n):
    #Opening proper webpage
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    wiki = "https://www.yelp.com/biz_photos/" + restaurantTag + "?tab=food"
    driver.get(wiki)

    CLICK_PAUSE_TIME = .5
    output = []
    first_pic = driver.find_element_by_xpath("//a[@class='biz-shim js-lightbox-media-link js-analytics-click']")
    first_pic.click()
    time.sleep(CLICK_PAUSE_TIME * 5)

    #Cycle through all of the posts
    i = 0
    while i>=0 and i < n:
        full_pic = driver.find_element_by_xpath("//div[@class='media js-media-photo']")
        img = full_pic.find_element_by_xpath("img[@class='photo-box-img']")
        display_url = img.get_attribute("src")

        caption_frames = driver.find_elements_by_xpath("//div[@class='caption selected-photo-caption-text']")
        for caption_frame in caption_frames:
	        caption = caption_frame.text
	        output.append([caption, display_url])

        #Click the next
        try:
        	next_button = driver.find_element_by_xpath("//span[@class='icon icon--48-chevron-right icon--size-48 icon--inverse icon--fallback-inverted']")
        	next_button.click()
        	time.sleep(CLICK_PAUSE_TIME*2)
        	i += 1
       	except:
       		i = -1

    driver.close()
    return output	    	

def analyze_yelp_images(images_data, foodie_id, yelp_id):
    exceptions = ['a', 'an', 'of', 'the', 'is', 'with', 'or', 'and', 'to', 'from'] + foodie_id.split('-')

    script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))

    # menu_items = read_items(script_dir, foodie_id)
    json = extract_json(foodie_id)
    menu_items = save_locally(json, foodie_id)

    path = script_dir + "/csvfiles/images/" + foodie_id[:100] + yelp_id.replace('/', '-') + "-images-yelp/"
    try: os.makedirs(path)
    except OSError: pass  

    # initializing
    foodie_ids = []
    items = []
    filenames = []
    captions = []
    source_ids = []

    n = 100    

    for image_data in images_data:
        caption = image_data[0]
        link = image_data[1]

        # remove sentence if it does not contain a menu item
        items_in_given_sentence = items_in_sentence(caption, menu_items, 2, foodie_id, exceptions)
        print(items_in_given_sentence)
        if(len(items_in_given_sentence) == 0):
            continue

        # choose best item out of all matched items
        optimized_items = optimize_list(items_in_given_sentence, caption.lower())
        for item in optimized_items:
                         
            filename = foodie_id + "-" + str(n) + ".jpg"
            urlretrieve(link, path + filename)

            foodie_ids.append(foodie_id)
            items.append(item)
            filenames.append(filename)
            captions.append(caption)
            source_ids.append(yelp_id)
            n += 1
            print(n)
        
    d = {'FoodieID' : foodie_ids, 'Item' : items, 'Filename' : filenames, 'Captions' : captions, 'YelpID' : source_ids}
    df = pd.DataFrame(d)
    df.to_excel(path + foodie_id[:100] + yelp_id.replace('/','-') + ".xlsx", sheet_name='Sheet1', encoding="utf8", index=False)
    
    return n - 100

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-t', '--restaurant_tag', help='Restaurant tag', default='girl-and-the-goat-chicago')
	parser.add_argument('-n', '--number_of_images', help='Number of images', default='100')
	parser.add_argument('-f', '--foodie_id', help='FoodieID', default='girl--the-goat-chicago-807')

	args = vars(parser.parse_args())
	restaurant_tag = args['restaurant_tag']	
	number_of_images = int(args['number_of_images'])
	foodie_id = args['foodie_id']

	output = pull_yelp_images(restaurant_tag, number_of_images)
	n = analyze_yelp_images(output, foodie_id, restaurant_tag)
	print(n)
