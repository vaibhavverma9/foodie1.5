import argparse as ap
import os, pickle
import pandas as pd
import time
from datetime import date
import random
from menu_from_db import extract_json
from random import randint
from save_sentences_csv import run_match_sentences
from analyze_sentiment import run_sentiment_analyzer
from compile_to_json import compile_data
from scrape_reviews_infatuation import convert_to_ten_scale


user_ranges = {'General' : {'start' : 0, 'end' : 58}, 'DC' : {'start' : 101, 'end' : 130}}

dish_user_match = {}

# Reads info from file 
def read_info(restaurant_tag):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	fname = script_dir + "/output_info/" + restaurant_tag + ".txt"
	with open(fname, 'rb') as f:
		info = pickle.load(f)
	return info

def random_date():
	start_dt = date.today().replace(day=1, month=1).toordinal()
	end_dt = date.today().toordinal()
	return date.fromordinal(random.randint(start_dt, end_dt))

def create_comments(row, user_type):
	foodie_id = row['FoodieID']
	yelp_id = row['YelpID']
	# set file paths to data inputs
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	file_path = script_dir + "/csvfiles/sentences/labeled-rated/" + foodie_id + "-labeled-rated.xlsx"
	output_path = script_dir + "/csvfiles/sentences/comments/" + foodie_id + "-comments.xlsx"

	json = extract_json(foodie_id)

	df = pd.read_excel(file_path)

	info = json['Info']

	df = df.drop(columns=['Keywords'])
	df = max_3(df)

	# df = df.drop_duplicates(subset=['Item'], keep="first")

	df['Source'] = 'Yelp'
	# if yelp_id == '':
	# 	df['SourceRestaurantCode'] = get_yelp_id(json)
	# else:
	# 	df['SourceRestaurantCode'] = yelp_id
	df['FoodieID'] = foodie_id
	df['Month'] = ""
	df['Day'] = ""
	df['Year'] = ""
	start = user_ranges[user_type]['start']
	end = user_ranges[user_type]['end']

	# df.loc[i, 'SourceUserCode'] = "user-" + user_code
	user_code = randint(start, end) + 1000		
	random_day = random_date()
	# df.loc[i, 'Month'] = random_day.month
	# df.loc[i, 'Day'] = random_day.day
	# df.loc[i, 'Year'] = random_day.year

	for i, row in df.iterrows():
		print(row)
		if i % 5 == 0:
			user_code = randint(start, end) + 1000
			if(user_code == 1104):
				user_code = 1105
			random_day = random_date()
		if(row['Item'] in dish_user_match):
			while(user_code in dish_user_match[row['Item']]):
				user_code = randint(start, end) + 1000
			dish_user_match[row['Item']].append(user_code)
		else:
			dish_user_match[row['Item']] = []
			dish_user_match[row['Item']].append(user_code)
		df.loc[i, 'SourceUserCode'] = "user-" + str(user_code)
		df.loc[i, 'Month'] = random_day.month
		df.loc[i, 'Day'] = random_day.day
		df.loc[i, 'Year'] = random_day.year
		df.loc[i, 'Categories'], df.loc[i, 'Menu'], df.loc[i, 'Description'] = match_item(row['Item'], json)

	df = df[['Source', 'SourceUserCode', 'FoodieID', 'Month', 'Day', 'Year', 'Item', 'Sentence', 'Rating', 'Categories', 'Menu', 'Description']]



	df.to_excel(output_path, index=False)	
	return "Comments Extracted"

# changed to max 6
def max_3(df):
	frames = []
	unique_values = df.Item.unique()
	for unique_value in unique_values:
		rows = df['Item'] == unique_value
		df_t = df[rows].head(6)
		frames.append(df_t)
	result = pd.concat(frames).sort_values(by='Sentence').reset_index()
	return result

def get_yelp_id(json):
	if(json['Info'] != []):
		return json['Info'][0]['YelpID']
	else:
		return ''
	# return json['Info']['YelpID']

def match_item(item, json):
	category = ""
	menu = ""
	description = ""
	for row in json['Items']:
		if(row['Item'] == item):
			if(row['Categories'] == "NaN"):
				category = ""
			elif(isNaN(row['Categories']) == False):
				category = row['Categories']
			else:
				category = ""
			
			if(row['Menu'] == "NaN"):
				menu = ""
			elif(isNaN(row['Menu']) == False):
				menu = row['Menu']
			else:
				menu = ""

			if(row['Description'] == "NaN"):
				description = ""
			elif(isNaN(row['Description']) == False):
				description = row['Description']
			else:
				description = ""
	return category, menu, description

def isNaN(num):
    return num != num

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-f', '--foodie_id', help='FoodieID', default='girl-and-the-goat-chicago')

	args = vars(parser.parse_args())
	foodie_id = args['foodie_id']
