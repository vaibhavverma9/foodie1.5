import argparse as ap
import requests, os, json, pickle
import csv
from requests.auth import AuthBase
import json
import sys
import pandas as pd
from menu_from_db import extract_json, save_locally
from save_sentences_csv import items_in_sentence, optimize_list, read_items
import ast 
from urllib.request import urlretrieve

# For URL, hideMenuItems must be false 
def pull_json(url, authorization):
	headers = {
     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
     'Accept': 'application/json',
     'Authorization' : authorization 
     # 'Referer' : 'https://www.grubhub.com/restaurant/little-star-pizza---mission-district-400-valencia-st-san-francisco/549152?orderMethod=delivery&locationMode=DELIVERY&facetSet=umamiV2&pageSize=20&hideHateos=true&searchMetrics=true&queryText=sushi&latitude=37.77492904&longitude=-122.41941834&fieldSet=cuisine&sortSetId=umamiV2&sponsoredSize=3&countOmittingTimes=true',
     # 'Origin' : 'https://www.grubhub.com', 
     # 'If-Modified-Since' : '0', 
     # 'Cache-Control' : 'max-age=0'
	}

	response = requests.get(url, headers = headers)
	print(response)
	try:
		return response.json()
	except:
		return {} 

def pull_menu_items(response_json):
	menu_items = {}
	menu_items['Food'] = []

	print(response_json)
	categories = response_json['restaurant']['menu_category_list']
	for category in categories:
		category_name = category['name']
		dishes = category['menu_item_list']
		for dish in dishes:
			item_name = dish['name']
			description = dish['description']
			price = float(dish['price']['amount']) / 100
			menu_items['Food'].append([item_name, price, description, category_name, ''])
	print(menu_items)
	return menu_items

def pull_images(response_json, foodie_id):
	menu_items = {}
	menu_items['Food'] = []

	#Logistics
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	path = script_dir + "/csvfiles/images/" + foodie_id + "-images-grubhub/"
	exceptions = ['a', 'an', 'of', 'the', 'is', 'with', 'or', 'and', 'to', 'from'] + foodie_id.split('-')

	# menu_items = read_items(script_dir, foodie_id)
	json_t = extract_json(foodie_id)
	if(json_t['Items'] == []):
		return 'Could not pull images from database. Potential FoodieID mismatch.'
	menu_items = save_locally(json_t, foodie_id)
	
	foodie_ids = []
	source_ids = []
	items = []
	filenames = []
	matches = []
	n = 0


	print(response_json)
	categories = response_json['restaurant']['menu_category_list']
	for category in categories:
		dishes = category['menu_item_list']
		for dish in dishes:
			item_name = dish['name']
			if 'media_image' in dish:
				img_url = dish['media_image']['base_url'] + dish['media_image']['public_id'] + '.' + dish['media_image']['format']
				print(img_url)
				matched_items = items_in_sentence(item_name, menu_items, 2, foodie_id, exceptions)
				if(len(matched_items) == 0):
					continue     

				optimized_items = optimize_list(matched_items, item_name.lower())
				for item in optimized_items:
					if n == 0:
						try: os.makedirs(path)
						except OSError: pass

					filename = foodie_id + "-" + str(n) + ".jpg"
					urlretrieve(img_url, path + filename)

					foodie_ids.append(foodie_id)
					items.append(item)
					filenames.append(filename)

					matches.append(item_name)
					n += 1
					print(n)

	if n > 0:
		d = {'FoodieID' : foodie_ids, 'Item' : items, 'Filename' : filenames, 'Matches' : matches}
		df = pd.DataFrame(d)
		df.to_excel(path + foodie_id + ".xlsx", sheet_name='Sheet1', encoding="utf8", index=False)

	return 'Added GrubHub Imgs'

# Save menu_items as a file using pickle library (not necessarily human readable)
def write_menu(menu_items, restaurant_tag):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	with open(script_dir + "/output_menu_items/foodie/" + restaurant_tag + ".txt", 'wb') as f:
		pickle.dump(menu_items, f)

def strip_store_id(grubhub_id):
	id_arr = grubhub_id.split('/')
	store_id = id_arr[len(id_arr) - 1]
	return store_id

def scrape_grubhub_menu(url, authorization, foodie_id):
	response_json = pull_json(url, authorization)
	if(response_json == {}):
		return "GrubHub URL or Authorization Incorrect"
	try:
		menu_items = pull_menu_items(response_json)
		write_menu(menu_items, foodie_id)
		return "Menu from GrubHub Pulled"
	except:
		return "GrubHub URL or Authorization Incorrect"

def scrape_grubhub_images(url, authorization, foodie_id):
	response_json = pull_json(url, authorization)
	if(response_json == {}):
		print("GrubHub URL or Authorization Incorrect")
		return "GrubHub URL or Authorization Incorrect"
	try:
		print("Pulling Images")
		return pull_images(response_json, foodie_id)
	except:
		return "GrubHub URL or Authorization Incorrect"


if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-u', '--request_url', help='Request URL', default='https://api-gtm.grubhub.com/restaurants/549152?hideChoiceCategories=true&version=4&orderType=standard&hideUnavailableMenuItems=true&hideMenuItems=false&showMenuItemCoupons=true&includePromos=true&location=POINT(-122.41941834%2037.77492904)&locationMode=delivery')
	parser.add_argument('-f', '--foodie_id', help='Foodie ID', default='little-star-pizza-san-francisco-403')
	parser.add_argument('-a', '--authorization', help='Authorization', default='Bearer d738ccb5-56fa-4618-849a-0862aac27a60')

	args = vars(parser.parse_args())
	request_url = args['request_url']
	foodie_id = args['foodie_id']
	authorization = args['authorization']

	scrape_grubhub_images(request_url, authorization, foodie_id)
	