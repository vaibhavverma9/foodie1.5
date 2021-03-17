# -*- coding: utf-8 -*-
import argparse as ap
import os, pickle, requests, traceback, re, operator, sys, math, shutil
import pandas as pd
from bs4 import BeautifulSoup
from scrape_menu_ubereats import scrape_ubereats_menus
from scrape_menu_singleplatform import scrape_singleplatform_menus
from scrape_menu_items import scrape_yelp_menus
from scrape_menu_postmates import scrape_postmates_menus
from scrape_menu_allmenus import scrape_allmenus_menus	
from scrape_reviews import run_scrape_reviews
from scrape_reviews_googlereviews import scrape_google_hours_spent, scrape_google_description
from scrape_info import run_scrape_info, find_coordinates, foursquare_info, scrap_data, gather_categories
from save_items_pickle import run_save_items_pickle
from save_items_csv import run_save_items_csv, read_items
from save_sentences_csv import run_match_sentences
from analyze_sentiment import run_sentiment_analyzer
from compile_to_final import generate_final, read_info
from pathlib import Path
from doordash import scrape_doordash_menu, scrape_doordash_images
from grubhub import scrape_grubhub_menu, scrape_grubhub_images
from generate_analytics_pdf import run_generate_analytics_pdf
from compile_to_json import add_to_database
from scrape_instagram import run_ig_img_scraper, usernames_for_automated_dms
from scrape_images_caviar import run_caviar_image_scraper
from menu_from_db import generate_verify, extract_json, save_locally
from fcs import create_comments
from scrape_images_postmates import run_postmates_image_scraper
from bing_api import web_search
from scrape_menu_caviar2 import scrape_caviar_menu
from get_foursquare_id import get_id
import json
from scrape_reviews_yelp import rotate_proxies
from convert_woflow import run_woflow_conversion
from scrape_images_yelp import pull_yelp_images, analyze_yelp_images
from scrape_reviews_infatuation import scrape_infatuation_reviews, create_output


google_api_key = "AIzaSyCcdD3A2gcadAxVEt7q_BUlAEl-gW_qgiE"

def read_input(f_suffix):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	file_path = script_dir + "/csvfiles/input/" + f_suffix + ".xlsx"
	df = pd.read_excel(file_path)
	return df

def save_output(df, f_suffix):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	file_path = script_dir + "/csvfiles/input/" + f_suffix + ".xlsx"
	writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
	print("Saving details at " + file_path)
	df.to_excel(writer, index=False)
	writer.close()

def read_row(row):
	name = str(row['Name']).replace("&", "").strip()
	address = str(row['Address']).strip()
	city = str(row['City']).strip()
	state = str(row['State']).strip()
	zipcode = str(row['Zipcode']).strip()
	yelpId = str(row['YelpID']).strip()
	return name, address, city, state, zipcode, yelpId

def create_foodie_id(row):
	name, address, city, state, zipcode, yelpId = read_row(row)

	if(isNaN(yelpId)):
		foodie_id = name + '-' + city
		foodie_id = foodie_id.lower().replace(" ", "-")
		symbols = ["&", ",", "+", ".", "'", "’", '/']
		for symbol in symbols: 
			foodie_id = foodie_id.replace(symbol, '')
		return foodie_id
	else:
		return yelpId

def scrape_data(url):
	print("Scraping URL:", url)
	r = requests.get(url)

	if(str(r.status_code) != '200'):
		r = rotate_proxies(url)

	encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
	soup = BeautifulSoup(r.content, "lxml") 
	return soup

def scrape_menu(row):
	foodie_id = row['FoodieID']
	if(isNaN(row['YelpID'])):
		try:
			ids = gather_ids('Yelp', sources['Yelp'], row)
			for source_id in ids:
				if(source_id == ""):
					continue
				if(verify_yelp_menus(source_id)):
					if(scrape_yelp_menus(source_id, foodie_id)):
						row['YelpID'] = source_id
						sources[source]['id'] = source_id
						return source, source_id
		except:
			pass
	else:
		if(scrape_yelp_menus(row['YelpID'], row['FoodieID'])):
			sources['Yelp']['id'] = row['YelpID']
			return "Yelp", row['YelpID']

	return False, ""

def message(source, is_source, data_type, source_id):
	if is_source:
		print("Yes!", source, "has", data_type, "for", source_id)
	else:
		print("Sorry!", source, "does not have", data_type, "for", source_id)

def scrape_reviews(row, n):
	foodie_id = row['FoodieID']
	if(isNaN(row['YelpID'])):
		row['YelpID'] = gather_id('Yelp', sources['Yelp'], row)
	run_scrape_reviews(foodie_id, row["YelpID"], row['Name'] + ' ' + row['City'], n) 
	return row

def scrape_info(row, f_suffix, neighborhood):
	print("printing info")
	foodie_id = row['FoodieID']
	foursquare_id = row['FoursquareID']

	if(isNaN(row['YelpID'])):
		row['YelpID'] = gather_id('Yelp', sources['Yelp'], row)
		sources['Yelp']['id'] = row['YelpID']
		if(isNaN(row['YelpID'])):
			row['Status'] = "Manually add YelpID"			
			return row 

	if(run_scrape_info(row['YelpID'], foodie_id, foursquare_id, str(row['Address']), '', f_suffix, row)):
		return row

	return row

def match_analyze_compile(row):
	foodie_id = row['FoodieID']
	review_count = run_match_sentences(foodie_id, 4, 1)
	run_sentiment_analyzer(0, foodie_id, '')
	generate_final(foodie_id)
	# if review_count < 80 and 'Menu Available' in row['Status']:
	# 	return "More Reviews"
	# try:
	# 	info = read_info(foodie_id)
	# except:
	# 	pass
	# if(info['Latitude'] != "" and info['Longitude'] != "" and info['FoursquareID'] != ""):
		# return "Ready to Import"
	return "Ready to Sanity Check:" + str(review_count)

def add_to_mturk_csv(row, f_suffix):
	foodie_id = row['FoodieID']
	website_url = get_website_link(row)

	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	file_path = script_dir + "/csvfiles/mturk/mturk-" + f_suffix + ".csv"
	my_file = Path(file_path)
	if my_file.is_file():
		df = pd.read_csv(file_path)
		d1 = {'website_url' : [website_url], 'notes' : [""]}
		df2 = pd.DataFrame(d1)
		df = df.append(df2)		
	else:
		d1 = {'website_url' : [website_url], 'notes' : [""]}
		df = pd.DataFrame(d1)
	df.to_csv(file_path, index=False)

def upwork_create_menu_request(row, f_suffix):
	# print("adding to upwork csv as create request")
	foodie_id = row['FoodieID']
	website_url = get_website_link(row)
	name, address, city, state, zipcode, yelpId = read_row(row)
	menu_filename = foodie_id + "-items.xlsx"

	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	abbr = abbreviate_suffix(f_suffix)
	dir_path = script_dir + "/csvfiles/upwork/" + abbr

	try: os.makedirs(dir_path)
	except OSError: pass

	file_path = dir_path + "/create-" + f_suffix + ".xlsx"
	my_file = Path(file_path)

	if my_file.is_file():
		df = pd.read_excel(file_path)
		d1 = {'Name of Your Excel File' : [menu_filename], 'Restaurant Website' : [website_url], 'Restaurant Name' : [name], 'Address' : [address], 'City' : [city], 'State' : [state], 'Zipcode' : [zipcode], 'Menu Source' : [""], 'Additional Notes' : [""]}
		df2 = pd.DataFrame(d1)
		df = df.append(df2)	
		df = df.drop_duplicates(subset=['Restaurant Name', 'Address'], keep="first")
	else:
		d1 = {'Name of Your Excel File' : [menu_filename], 'Restaurant Website' : [website_url], 'Restaurant Name' : [name], 'Address' : [address], 'City' : [city], 'State' : [state], 'Zipcode' : [zipcode], 'Menu Source' : [""], 'Additional Notes' : [""]}
		df = pd.DataFrame(d1)
	df.to_excel(file_path, index=False)

def upwork_verify_menu_request(row, f_suffix):
	# print("adding to upwork csv as verify request")
	foodie_id = row['FoodieID']
	website_url = get_website_link(row)
	name, address, city, state, zipcode, yelpId = read_row(row)
	print(foodie_id)
	menu_filename = foodie_id + "-items.xlsx"

	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	abbr = abbreviate_suffix(f_suffix)
	dir_path = script_dir + "/csvfiles/upwork/" + abbr
	try: os.makedirs(dir_path)
	except OSError: pass

	verify_path = dir_path + "/verify-" + f_suffix
	try: os.makedirs(verify_path)
	except OSError: pass

	file_path = verify_path + "/0-verify-" + f_suffix + ".xlsx"
	my_file = Path(file_path)

	if my_file.is_file():
		df = pd.read_excel(file_path)
		d1 = {'Name of Your Excel File' : [menu_filename], 'Restaurant Website' : [website_url], 'Restaurant Name' : [name], 'Address' : [address], 'City' : [city], 'State' : [state], 'Zipcode' : [zipcode], 'Menu Source' : [""], 'Additional Notes' : [""]}
		df2 = pd.DataFrame(d1)
		df = df.append(df2)		
	else:
		d1 = {'Name of Your Excel File' : [menu_filename], 'Restaurant Website' : [website_url], 'Restaurant Name' : [name], 'Address' : [address], 'City' : [city], 'State' : [state], 'Zipcode' : [zipcode], 'Menu Source' : [""], 'Additional Notes' : [""]}
		df = pd.DataFrame(d1)
	df.to_excel(file_path, index=False)

	items = read_items(script_dir, foodie_id)
	food_items = []
	for key in items:
		for item in items[key]:
			food_items.append(item)

	s = pd.DataFrame(food_items, index=None, columns=['Item', 'Description', 'Price', 'Categories', 'Menu']) 
	s.to_excel(verify_path + "/" + foodie_id + "-items.xlsx", sheet_name='Sheet1', encoding="utf8", index=False)

def zip_upwork_verify_menus(f_suffix):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	abbr = abbreviate_suffix(f_suffix)
	dir_path = script_dir + "/csvfiles/upwork/" + abbr

	for root, dirs, files in os.walk(dir_path):
		if f_suffix in root:
			print(root[root.find('verify'):], len(files) - 1)
			shutil.make_archive(root, 'zip', root)
		for file in files:
			if "create" in file and f_suffix in file:
				file_path = dir_path + "/" + file
				df = pd.read_excel(file_path)
				print(file, df.shape[0])

def abbreviate_suffix(f_suffix):
	index = max(f_suffix.find('-'), 0)
	return f_suffix[:index]

def isNaN(num):
    return num != num

def roundup(x):
    return int(math.ceil(max(x, 1) / 10.0)) * 10

def generate_google_api_key(name, address, city, state, zipcode):
	lat, lng = find_coordinates(name, address, city, state, zipcode)
	wiki = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + name + "&inputtype=textquery" + "&location=" + str(lat) +","+str(lng)+ "&address=" + address + ", " + city + ", " + state +  "&key=" + google_api_key + "&fields=place_id"
	response = requests.get(wiki)
	output = json.loads(response.text)
	name = name.replace("&", "and")
	if('status' in output):
		if(output['status'] == "ZERO_RESULTS" or output['status'] == "INVALID_REQUEST" or output['status'] == 'REQUEST_DENIED'):
			return "", "No GooglePlIDs"
		else:
			return output['candidates'][0]['place_id'], "Found GooglePlID"

def scrape(row, i, f_suffix):
	print("scrape function")
	foodie_id = row['FoodieID']
	if "Menu Available" in row['Status']:
		run_save_items_pickle(foodie_id, foodie_id)
		run_save_items_csv(foodie_id)

		row = scrape_info(row, f_suffix, row['Neighborhood'])
		if("Manually add YelpID" not in row['Status']):
			row = scrape_reviews(row, 0)
	elif "Scrape Menu" in row['Status']:
		source, source_id = scrape_menu(row)
		if source == False:
			row['Status'] = 'Menu Unavailable'
		else:
			run_save_items_csv(foodie_id)
			run_save_items_pickle(foodie_id, foodie_id)
			run_save_items_csv(foodie_id)
			row['Status'] = 'Scraped Menu'
	elif "More Reviews" in row['Status']:
		run_save_items_pickle(foodie_id, foodie_id)
		run_save_items_csv(foodie_id)
		row = scrape_info(row, f_suffix)
		if("Manually add YelpID" not in row['Status']):
			row = scrape_reviews(row, 500)
	elif "New Request" in row['Status']:
		row = scrape_info(row, f_suffix)
		source, source_id = scrape_menu(row)
		if source == False:
			print("source: False")
			upwork_create_menu_request(row, f_suffix)
			row['Status'] = "Menu Unavailable"
			return row
		else:
			print("source: True")
			run_save_items_csv(foodie_id)
			run_save_items_pickle(foodie_id, foodie_id)
			row['Status'] = 'Menu Available'
			return row
	elif row['Status'] == "Menu Unavailable":
		upwork_create_menu_request(row, f_suffix)
		return row
	else:
		return row
	return row

# Gather ID using BeautifulSoup for restaurant codes with a distinct end symbol
def gather_id(source, detail, row):
	print("----")
	print(source, detail)
	name, address, city, state, zipcode, yelpId = read_row(row)
	variations = ["\\", "", "/", " \\", "//"]
	if(detail['id'] == ""):
		for variation in variations:
			wiki = "https://www.google.com/search?q=" + name + " " + address + " " + city + " " + state + " " + source + variation
			soup = scrape_data(wiki)
			keyword = detail['keyword']
			n_ids = detail['n_ids']

			links = soup.find_all('a')
			for link in links:
				text = link.get('href')
				if keyword in text:
					return clean_text(text, keyword, n_ids, city)
				if source in text:
					print(text)
			if(len(links) > 10):
				break

	else:
		return detail['id']
	return ""

# Gather multiple IDs using BeautifulSoup for restaurant codes with a distinct end symbol
def gather_ids(source, detail, row):
	name, address, city, state, zipcode, yelpId = read_row(row)
	
	wiki = "https://www.google.com/search?q=" + name + " " + city + " " + state + " " + address + " " + zipcode + " " + source
	soup = scrape_data(wiki)
	keyword = detail['keyword']
	n_ids = detail['n_ids']

	links = soup.find_all('a')
	output = []

	for link in links:
		text = link.get('href')
		if keyword in text:
			output.append(clean_text(text, keyword, n_ids, city))

	return set(output)

def all_occurrences(text, keyword):
	index = 0
	indexes = [0]
	while True:
		index = text.find(keyword, index)
		if index == -1:
			return indexes
		indexes.append(index)
		text = text[index + len(keyword):]

def clean_text(text, keyword, n_ids, city):
	text = text[text.index(keyword) + len(keyword):]
	if '&' in text:
		text = text[:text.index('&')]
	if '+' in text:
		text = text[:text.index('+')]

	city = city.lower().replace(' ', '-')
	occurrences = all_occurrences(text, city)
	end_index = occurrences[max(len(occurrences) - 1, 0)] + len(city)
	while('%' in text[end_index:]):
		text = text[:end_index] + text[end_index:text.index('%')]
	
	char = '/'
	occurences = []
	for pos, c in enumerate(text):
		if char == c:
			occurences.append(pos)

	if len(occurences) > n_ids - 1:
		text = text[:occurences[n_ids - 1]]

	return text

# Gather website link using BeautifulSoup
def get_website_link(row):
	name, address, city, state, zipcode, yelpId = read_row(row)
	query = name + " " + city + " " + state + " " + zipcode
	words_in_name = re.split(' ', name.lower())

	links = web_search(query, '10')

	count = {}
	for link in links:
		if 'http' in link:
			link = link[link.index('http'):]
			if '.com' in link:
				link = link[:link.index('.com') + 4]
				for word in words_in_name:
					if word in link:
						if link in count:
							count[link] += 1
						else:
							count[link] = 1
	if count == {}:
		return ""
	else:
		return max(count.items(), key=operator.itemgetter(1))[0]

def verify_yelp_menus(yelp_id):
	wiki = "https://www.yelp.com/menu/" + yelp_id
	soup = scrape_data(wiki)
	title = soup.find('title').get_text()
	if 'Menu' in title:
		return True
	return False

def initialize_sources():
	for source in sources:
		sources[source]['id'] = ''
	return sources

delivery_foodie_ids = []
delivery_links = []
delivery_addresses = []
del_sources = []
def get_delivery_links(row):
	ubereats_id = gather_id('UberEats', delivery_sources['UberEats'], row)
	if(ubereats_id):
		delivery_foodie_ids.append(row['FoodieID'])
		delivery_links.append(delivery_sources['UberEats']['keyword'] + ubereats_id)
		delivery_addresses.append(row['Address'])
		del_sources.append('Uber Eats')

	doordash_id = gather_id('DoorDash', delivery_sources['DoorDash'], row)
	if(doordash_id):
		delivery_foodie_ids.append(row['FoodieID'])
		delivery_links.append(delivery_sources['DoorDash']['keyword'] + doordash_id)
		delivery_addresses.append(row['Address'])
		del_sources.append('Doordash')		

	grubhub_id = gather_id('GrubHub', delivery_sources['GrubHub'], row)
	if(grubhub_id):
		delivery_foodie_ids.append(row['FoodieID'])
		delivery_links.append(delivery_sources['GrubHub']['keyword'] + grubhub_id)
		delivery_addresses.append(row['Address'])
		del_sources.append('GrubHub')	

	postmates_id = gather_id('PostMates', delivery_sources['PostMates'], row)
	if(postmates_id):
		delivery_foodie_ids.append(row['FoodieID'])
		delivery_addresses.append(row['Address'])
		delivery_links.append(delivery_sources['PostMates']['keyword'] + postmates_id)
		del_sources.append('Postmates')

	caviar_id = gather_id('Caviar', delivery_sources['Caviar'], row)
	if(caviar_id != ''):
		delivery_foodie_ids.append(row['FoodieID'])
		delivery_links.append(delivery_sources['Caviar']['keyword'] + caviar_id)
		delivery_addresses.append(row['Address'])
		del_sources.append('Caviar')

	seamless_id = gather_id('Seamless', delivery_sources['Seamless'], row)
	if(seamless_id != ''):
		delivery_foodie_ids.append(row['FoodieID'])
		delivery_links.append(delivery_sources['Seamless']['keyword'] + seamless_id)
		delivery_addresses.append(row['Address'])
		del_sources.append('Seamless')

	deliverycom_id = gather_id('delivery.com', delivery_sources['delivery.com'], row)
	if(deliverycom_id != ''):
		delivery_foodie_ids.append(row['FoodieID'])
		delivery_links.append(delivery_sources['delivery.com']['keyword'] + deliverycom_id)
		delivery_addresses.append(row['Address'])
		del_sources.append('delivery.com')		

def get_delivery_backups(links):
	if(len(links) <= 1):
		return ""
	else:
		backups = links[1:]
		s = ', '
		return s.join(backups)


def import_delivery_links(f_suffix):
	d1 = {"FoodieId" : delivery_foodie_ids, 'ReferenceLink' : delivery_links, 'Addresses' : delivery_addresses, 'Source Name' : del_sources }

	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	file_path = script_dir + "/csvfiles/delivery_links/" + f_suffix + "-delivery.xlsx"

	s = pd.DataFrame(d1, index=None) 
	s.to_excel(file_path, sheet_name='Sheet1', encoding="utf8", index=False)

def fill_in_data(row):
	json = extract_json(row['FoodieID'])['Info'][0]
	row['Name'] = json['Name']
	row['Address'] = json['AddressLine']
	row['City'] = json['City']
	row['State'] = json['State']
	row['Zipcode'] = json['ZipCode']
	return row

def main(f_suffix):
	df = read_input(f_suffix)
	for i, row in df.iterrows():
		if(isNaN(row['FoodieID'])):
			row['FoodieID'] = create_foodie_id(row)
		try:
			initialize_sources()
			if(row['Status'] == "Imported"):
				continue 
			if "Scrape Info" in row['Status']:
				scrape_info(row, f_suffix, row['Neighborhood'])
				row['Status'] = 'Completed Info Scrape'
			elif "Scrape Menu" in row['Status']:
				source, source_id = scrape_menu(row)
				scrape(row, i, f_suffix)
			if "New Request" in row['Status']:
				row = scrape(row, i, f_suffix)
			if "Menu Available" in row['Status']:
				row = scrape(row, i, f_suffix)
				if("Manually add YelpID" not in row['Status']):
					row['Status'] = match_analyze_compile(row)
			if "More Reviews" in row['Status']:
				row = scrape(row, i, f_suffix)
				if("Manually add YelpID" not in row['Status']):
					row['Status'] = match_analyze_compile(row)
			if "Generate PDF" in row['Status']:
				run_generate_analytics_pdf(row, row['FoodieID'])
			if "Ready to Import" in row['Status']:
				try:
					add_to_database(row['FoodieID'])
					row['Status'] = 'Imported'
				except:
					row['Status'] = "Failed to Import"
			
			if "Caviar Images" in row['Status']:
				print("Running Caviar image scraper")
				if(isNaN(row['CaviarID'])):
					caviar_id = gather_id('Caviar', sources['Caviar'], row)
				else:
					caviar_id = row['CaviarID']

				if(caviar_id == ''):
					row['Status'] = 'Could not find CaviarID'
				else:
					row['Status'] = run_caviar_image_scraper(caviar_id, row['FoodieID'])
					df.loc[i, 'CaviarID'] = caviar_id
					# row['Status'] = 'Added Caviar Imgs'

			if "Instagram Images" in row['Status']:
				print("Running Instagram image scraper")
				if(isNaN(row['InstagramID'])):
					instagram_id = gather_id('Instagram', sources['Instagram'], row)
				else:
					instagram_id = row['InstagramID']
				if(instagram_id == ''):
					row['Status'] = 'Could not find InstagramID'
				else:					
					df.loc[i, 'InstagramID'], n = run_ig_img_scraper(instagram_id, row['FoodieID'])
					if(n <= 1):
						row['Status'] = "Zero IG Imgs scraped"
					else:	
						row['Status'] = 'Added IG Imgs'


			if "Doordash Images" in row['Status']:
				print("Running Doordash image scraper")
				if(isNaN(row['DoordashID'])):
					doordash_id = gather_id('DoorDash', sources['DoorDash'], row)
				else:
					doordash_id = row['DoordashID']
				if(doordash_id == ''):
					row['Status'] = 'Could not find DoordashID'
				else:					
					df.loc[i, 'DoordashID'] = doordash_id
					row['Status'] = scrape_doordash_images(doordash_id, row['FoodieID'])

			if "Yelp Images" in row['Status']:
				print("Running Yelp image scraper")
				if(isNaN(row['YelpID'])):
					yelp_id = gather_id('Yelp', sources['Yelp'], row)
				else:
					yelp_id = row['YelpID']
				if(yelp_id == ''):
					row['Status'] = 'Could not find YelpID'
				else:					
					df.loc[i, 'yelp_id'] = yelp_id
					output = pull_yelp_images(yelp_id, 100)
					n = analyze_yelp_images(output, row['FoodieID'], yelp_id)
					row['Status'] = "Scraped Yelp Images" + str(n)


				# print("Running Postmates image scraper")
				# if(isNaN(row['PostMatesID'])):
				# 	postmates_id = gather_id('PostMates', sources['PostMates'], row)
				# 	print("New PostMatesID: ", postmates_id)
				# else:
				# 	postmates_id = row['PostMatesID']
				# 	print("Existing PostMates ID: ", postmates_id)
				# run_postmates_image_scraper(postmates_id, row['FoodieID'])
				# df.loc[i, 'PostMatesID'] = postmates_id

				# print("Running Doordash image scraper")
				# if(isNaN(row['DoordashID'])):
				# 	doordash_id = gather_id('Doordash', sources['Doordash'], row)
				# else:
				# 	doordash_id = row['DoordashID']
				# scrape_doordash_images(doordash_id, row['FoodieID'])
				# df.loc[i, 'DoordashID'] = doordash_id


			if "Instagram Info" in row['Status']:
				run_ig_info_scraper(row['Hashtag'], 100)
				row['Status'] = row['Status'].replace('Instagram Info', '+IG Info')
			if "Pull Menu" in row['Status']:
				json = extract_json(row['FoodieID'])
				save_locally(json, row['FoodieID'])				
				run_save_items_csv(row['FoodieID'])
				row['Status'] = "Pulled Menu from Database"
			if "Enter Info" in row['Status']:
				row = fill_in_data(row)
				df.loc[i] = row 
				row['Status'] = "Entered Info from Database"
			if "User Comments General" in row['Status']:
				json = extract_json(row['FoodieID'])
				save_locally(json, row['FoodieID'])
				scrape_reviews(row, 150)
				run_match_sentences(row['FoodieID'], 4, 1)
				run_sentiment_analyzer(0, row['FoodieID'], '')
				row['Status'] = create_comments(row, 'General')
			if "User Comments DC" in row['Status']:
				json = extract_json(row['FoodieID'])
				save_locally(json, row['FoodieID'])
				scrape_reviews(row, 150)
				run_match_sentences(row['FoodieID'], 4, 1)
				run_sentiment_analyzer(0, row['FoodieID'], '')
				row['Status'] = create_comments(row, 'DC')
			if "FoursquareID" in row['Status']:
				row['FoursquareID'] = get_id(row['Name'], row['Address'], row['City'], row['State'], row['Zipcode'])
				print(row['FoursquareID'])
				df.loc[i, 'FoursquareID'] = row['FoursquareID']
			if "GooglePlaceID" in row['Status']:
				row['GooglePlaceID'], row['Status'] = generate_google_api_key(row['Name'], row['Address'], row['City'], row['State'], row['Zipcode'])
				df.loc[i, 'GooglePlaceID'] = row['GooglePlaceID']
			if "Delivery Link" in row['Status']:
				get_delivery_links(row)
				import_delivery_links(f_suffix)
				row['Status'] = 'Added Del. Link'
			if "Automated DMs" in row['Status']:
				if(isNaN(row['InstagramID'])):
					instagram_id = gather_id('Instagram', sources['Instagram'], row)
				else:
					instagram_id = row['InstagramID']
				usernames_for_automated_dms(instagram_id, 300, row['Name'], row['City'])
				row['Status'] = 'Gathered Usernames'

			if "Doordash Menu" in row['Status']:
				if(isNaN(row['DoordashID'])):
					doordash_id = gather_id('DoorDash', sources['DoorDash'], row)
					row['DoordashID'] = doordash_id
					df.loc[i, 'DoordashID'] = doordash_id
				else: 
					doordash_id = row['DoordashID']
				if doordash_id == "":
					row['Status'] = "Could not find DoordashID"
				else:
					scrape_doordash_menu(doordash_id, row['FoodieID'])
					run_save_items_csv(row['FoodieID'])
					row['Status'] = 'Menu Scraped from Doordash'

			if "Grubhub Menu" in row['Status']:
				if(isNaN(row['GrubhubID'])):
					grubhub_id = gather_id('GrubHub', sources['GrubHub'], row)
					df.loc[i, 'GrubhubID'] = grubhub_id
				else: 
					grubhub_id = row['GrubhubID']
				if grubhub_id == "":
					row['Status'] = "Could not find GrubhubID"
				else:
					scrape_grubhub_menu('https://api-gtm.grubhub.com/restaurants/' + grubhub_id, 'Bearer d738ccb5-56fa-4618-849a-0862aac27a60', row['FoodieID'])
					run_save_items_csv(row['FoodieID'])
					row['Status'] = 'Menu Scraped from GrubHub'


			if "Caviar Menu" in row['Status']:
				if(isNaN(row['CaviarID'])):
					caviar_id = gather_id('Caviar', sources['Caviar'], row)
					df.loc[i, 'CaviarID'] = caviar_id
				else: 
					caviar_id = row['CaviarID']
				if caviar_id == "":
					row['Status'] = "Could not find CaviarID"
				else:
					scrape_caviar_menu(caviar_id, row['FoodieID'])
					run_save_items_csv(row['FoodieID'])
					row['Status'] = 'Menu Scraped from Caviar'

			if "Google Description" in row['Status']:
				query = row['Name'] + row['Address'] + row['City']
				google_description = scrape_google_description(query)
				print(google_description)
				df.loc[i, 'Google Description'] = google_description
				row['Status'] = 'Scraped Description'
			if "Google Hours Spent" in row['Status']:
				query = row['Name'] + row['Address'] + row['City']
				hours_spent = scrape_google_hours_spent(query)
				df.loc[i, 'Google Hours Spent'] = hours_spent
				row['Status'] = 'Scraped Hours Spent'
			if "Categories" in row['Status']:
				name, address, city, state, zipcode, yelpId = read_row(row)
				if(isNaN(row['YelpID'])):
					row['YelpID'] = gather_id('Yelp', sources['Yelp'], row)
				categories = gather_categories(name, address, city, state, zipcode, row['YelpID'])
				df.loc[i, "Categories"] = categories		
				row['Status'] = 'Scraped Category'
			if "Yelp Neighborhood" in row['Status']:
				if(isNaN(row['YelpID'])):
					print("Gathering YelpID")
					row['YelpID'] = gather_id('Yelp', sources['Yelp'], row)
				print(row['YelpID'])
				info = scrap_data(row['YelpID'], "")
				df.loc[i, 'Yelp Neighborhood'] = info['Neighborhood']
				row['Status'] = 'Scraped Neighborhood'
			if "Woflow Menu" in row['Status']:
				run_woflow_conversion(row['FoodieID'], row['GooglePlaceID'], row['Name'])
				run_save_items_csv(row['FoodieID'])
				run_save_items_pickle(row['FoodieID'], row['FoodieID'])
				run_save_items_csv(row['FoodieID'])
				row['Status'] = 'Converted Woflow'
			if "Infatuation Reviews" in row['Status']:
				review, date = scrape_infatuation_reviews(row['InfatuationID']) 
				n = create_output(review, date, row['FoodieID']) 
				if(n == 0):
					row['Status'] = "Zero Infatuation Rvs Scraped"
				else:
					row['Status'] = "Added Infatuation Rvs" + str(n)

		except Exception:
			traceback.print_exc()
			row['Status'] = "Script Error"
		df.loc[i, 'Status'] = row['Status']
		df.loc[i, 'FoodieID'] = row['FoodieID']
		df.loc[i, 'YelpID'] = row['YelpID']
		save_output(df,f_suffix)
	try:
		zip_upwork_verify_menus(f_suffix)
	except:
		pass

sources = {# 'UberEats' : {'review_source' : False, 'menu_source' : True, 'info_source' : False, 'keyword' : 'ubereats.com/en-US/', 'id' :'', 'n_ids' : 4},
			# 'Ritual' : {'review_source' : False, 'menu_source' : True, 'info_source' : False, 'keyword' : 'order.ritual.co/menu/', 'id' : '', 'n_ids' : 2},
			# 'DoorDash' : {'review_source' : False, 'menu_source' : True, 'info_source' : False, 'keyword' : 'doordash.com/store/', 'id' : '', 'n_ids' : 1}, 
			'PostMates' : {'review_source' : False, 'menu_source' : True, 'info_source' : False, 'keyword' : 'https:/www.postmates.com/merchant/', 'id' : '', 'n_ids' : 1},
			'Yelp' : {'review_source' : True, 'menu_source' : True, 'info_source' : True, 'keyword' : 'https://www.yelp.com/biz/', 'id' : '', 'n_ids' : 1}, 
			# 'SinglePlatform' : {'review_source' : False, 'menu_source' : True, 'info_source' : False, 'keyword' : 'places.singleplatform.com/', 'id' : '', 'n_ids' : 1}, 
			'Instagram' : {'review_source' : False, 'menu_source' : False, 'info_source' : False, 'images_source' : True, 'keyword' : 'https://www.instagram.com/', 'id' : '', 'n_ids' : 3},
			'Caviar' : {'review_source' : False, 'menu_source' : False, 'info_source' : False, 'images_source' : True, 'keyword' : 'https://www.trycaviar.com/', 'id' : '', 'n_ids' : 2}, 
			'DoorDash' : {'review_source' : False, 'menu_source' : True, 'info_source' : False, 'images_source' : True, 'keyword' : 'https://www.doordash.com/store/', 'id' : '', 'n_ids' : 1},
			'GrubHub' : {'review_source' : False, 'menu_source' : True, 'info_source' : False, 'images_source' : True, 'keyword' : 'https://www.grubhub.com/restaurant/', 'id' : '', 'n_ids' : 2}}

delivery_sources = {
	'Caviar' : {'keyword' : 'https://www.trycaviar.com/', 'id' : '', 'n_ids' : 2},
	'DoorDash' : {'keyword' : 'https://www.doordash.com/store/', 'id' : '', 'n_ids' : 1}, 
	'UberEats' : {'keyword' : 'https://www.ubereats.com/en-US/', 'id' :'', 'n_ids' : 4},
	'PostMates' : {'keyword' : 'postmates.com/merchant/', 'id' : '', 'n_ids' : 1},
	'Seamless' : {'keyword' : 'https://www.seamless.com/menu/', 'id' : '', 'n_ids' : 2},
	'GrubHub' : {'keyword' : 'https://www.grubhub.com/restaurant/', 'id' : '', 'n_ids' : 2},
	'delivery.com' : {'keyword' : 'https://www.delivery.com/cities/', 'id' : '', 'n_ids' : 4}
}

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-f', '--f_suffix', help='Filename Suffix', default='11.27.18')

	args = vars(parser.parse_args())
	f_suffix = args['f_suffix']

	main(f_suffix)
