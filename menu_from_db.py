import requests, json, os
import pandas as pd
import numpy as np
import argparse as ap
from scrape_menu_items import write_menu

url = "https://thefoodieapi.com/api/GetRestaurantByFoodieID"

def extract_json(foodie_id):
	params = {'FoodieID' : foodie_id}
	headers = {'Content-Type' : "application/x-www-form-urlencoded",
		'Authorization' : "o83tKj7ebbA3"}
	response = requests.post(url, data=params, headers=headers)
	print(response.text)
	return json.loads(response.text)

def generate_verify(json, foodie_id):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	file_path = script_dir + "/csvfiles/verify/" + foodie_id + "-items.xlsx"	
	writer = pd.ExcelWriter(file_path, engine='xlsxwriter')

	# save to info sheet
	df = pd.DataFrame(json['Items'])
	df = df.replace(np.nan, '', regex=True)
	df = df.replace('NaN', '', regex=True)
	df = df.replace('0', '', regex=True)
	df = df[['Item', 'Description', 'Price', 'Categories', 'Menu']]
	df = df.sort_values(by=['Menu', 'Categories'])
	df.to_excel(writer, index=False, sheet_name='Items')

	writer.close()

def save_locally(json, foodie_id):
	menu_items = {}
	menu_items['Food'] = []
	for item in json['Items']:
		item['Categories'] = item['Categories'].replace('NaN', '')
		item['Menu'] = item['Menu'].replace('NaN', '')
		menu_items['Food'].append([item['Item'], item['Description'], item['Price'], item['Categories'], item['Menu'], ''])
	if(len(json['Items']) > 0):
		write_menu(menu_items, foodie_id)
	return menu_items

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-f', '--foodie_id', help='Foodie ID', default="el-castillito-san-francisco-134")
	args = vars(parser.parse_args())
	foodie_id = args['foodie_id']

	json = extract_json(foodie_id)
	save_locally(json, foodie_id)

