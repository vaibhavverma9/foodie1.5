import json, requests, os, pickle, requests, re
from bs4 import BeautifulSoup
from urllib.request import urlopen
import argparse as ap
import foursquare as fs 
import requests, json, math
import pandas as pd
from os import path
from scrape_reviews_googlereviews import scrape_google_description
# from bs2json import bs2json

dollar_conversion = {"Under $10" : "$", "$11-30" : "$$", "$31-60" : "$$$", "Above $61" : "$$$$", "$" : "$", "$$" : "$$", "$$$" : "$$$", "$$$$" : "$$$$", None : "$"}
category_conversion = {"American (New)" : "New American", "American (Traditional)" : "American"}

client_id = "YOCRGH1UXTDRI0OGZYX0XRKPAJXGVVBNBFCX0CGXYRBDFJVB"
client_secret = "V2PT4LKDAZIUI10SF34TL5DUINUMTOGHKHBL0I4X1CCMWZLI"
# client_id = "JKGW5VKQYONKP5MZBDFEZJQEWBRHAB0IJJCOXRJQUQBIURTP"
# client_secret = "F2DJ0145I0LT2RSUO0U4Y1SMEIWRTLYOZTMMRJSEB310TPHF"
# client_id = "1PNJHPGAS5SGRSYJR14QUJT2TISUEHM2ZV3GWPFIQZSIBVNN"
# client_secret = "FDSA5BIEV5ZNPSW3NYPGW0DZKO5HR0ABWCXVQT1YNPKB2UCG"
redirect_id = "thefoodieapp.com"

try:
	client = fs.Foursquare(client_id=client_id, client_secret=client_secret, 
                       redirect_uri=redirect_id)
except:
	pass

google_api_key = "AIzaSyCcdD3A2gcadAxVEt7q_BUlAEl-gW_qgiE"

def foursquare_info(name, address, city, state, zipcode):
	print(name, address, city, state, zipcode)
	try:
		city_state = city + ", " + state
	except:
		city_state = city
	try:
		vens = client.venues.search({'near' : city_state, 'intent' : 'match', 'name' : name, 'address' : address, 'city' : city, 'state' : state, 'zipcode' : zipcode})
		print("vens", vens)
		if 'venues' in vens and vens['venues'] != []:
			for restaurant in vens['venues']:
				print(restaurant)
				try:	
					foursquare_address = restaurant['location']['address']
				except:
					foursquare_address = ""
				if address_match(foursquare_address, address) or address != '':
					categories = []
					for category in vens['venues'][0]['categories']:
						categories.append(category['shortName'])
					return vens['venues'][0]['location']['lat'], vens['venues'][0]['location']['lng'], vens['venues'][0]['id'], categories
	except:
		return '', '', '', []
	return '','', '', []

def find_coordinates(name, address, city, state, zipcode):
	try:
		wiki = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address + ", " + city + ", " + state + "&key=" + google_api_key
	except:
		wiki = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address + ", " + city + "&key=" + google_api_key
	response = requests.get(wiki)
	output = json.loads(response.text)
	try:
		return output['results'][0]['geometry']['location']['lat'], output['results'][0]['geometry']['location']['lng']
	except:
		return '', ''

def google_maps_neighborhood(name, address, city, state, zipcode):
	try:
		wiki = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address + ", " + city + ", " + state + "&key=" + google_api_key
	except:
		wiki = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address + ", " + city + "&key=" + google_api_key
	response = requests.get(wiki)
	output = json.loads(response.text)
	print(output)
	for address_component in output['results'][0]['address_components']:
		if('neighborhood' in address_component['types']):	
			print(address_component['long_name'])		
			return address_component['long_name']
	return ''

# Scraps review data 
def scrap_data(yelp_id, foursquare_id, chain_id, row):
	wiki = "https://www.yelp.com/biz/" + yelp_id
	try:
		page = urlopen(wiki)
	except:
		if '%' in yelp_id:
			yelp_id = yelp_id[:yelp_id.index('%')]
		wiki = "https://www.yelp.com/biz/" + yelp_id
		page = urlopen(wiki)

	soup = BeautifulSoup(page, "lxml")
	# converter = bs2json()

	info = {}
	info['Address'] = [""]

	script_out = None

	script_jsons = soup.find_all("script", type="application/ld+json")
	print("script_jsons")
	for script_json in script_jsons:
		print(script_json)
		loaded = json.loads(script_json.text)
		if 'aggregateRating' in loaded:
			script_out = loaded

	description = scrape_google_description(row['Name'] + ' ' + row['City'])
	info['Description'] = description.capitalize()	

	categories = []
	if(script_out != None):
		try:
			priceRange = script_out["priceRange"]
			info['DollarSign'] = dollar_conversion[priceRange]
		except:
			info['DollarSign'] = ""

		address = script_out["address"]
		
		info['Name'] = [script_out["name"]]
		info['YelpID'] = yelp_id
		info['Address'] = [address['streetAddress']]
		info['City'] = [address['addressLocality']]
		info['State'] = [address['addressRegion']]
		if(info['State'][0] == None):
			info['State'] = ['']

		if(info['City'][0] == "Washington, DC" and info['State'][0] == ""):
			info['City'] = "Washington"
			info['State'] = "DC"

		info['Zipcode'] = [address['postalCode']]

		lat, lng, temp_foursquare_id, categories = foursquare_info(info['Name'][0], info['Address'][0], info['City'][0], info['State'][0], info['Zipcode'][0])
		if(foursquare_id == ""):
			info['FoursquareID'] = temp_foursquare_id
		elif(temp_foursquare_id == ""):
			info['FoursquareID'] = foursquare_id
		elif(temp_foursquare_id == foursquare_id):
			info['FoursquareID'] = foursquare_id
		else:
			info['FoursquareID'] = temp_foursquare_id

		if lat != '' and lng != '':
			info['Latitude'] = lat
			info['Longitude'] = lng
		else:
			info['Latitude'], info['Longitude'] = find_coordinates(info['Name'][0], info['Address'][0], info['City'][0], info['State'][0], info['Zipcode'][0])

	else:
		info['Name'] = row['Name']
		info['YelpID'] = ''
		info['Address'] = ''
		info['City'] = row['City']
		info['State'] = row['State']
		info['Zipcode'] = ''
		info['Latitude'] = ''
		info['Longitude'] = ''
		info['DollarSign'] = ''

		lat, lng, temp_foursquare_id, categories = foursquare_info(info['Name'], '', info['City'], info['State'], '')
		if(foursquare_id == ""):
			info['FoursquareID'] = temp_foursquare_id
		elif(temp_foursquare_id == ""):
			info['FoursquareID'] = foursquare_id
		elif(temp_foursquare_id == foursquare_id):
			info['FoursquareID'] = foursquare_id
		else:
			info['FoursquareID'] = temp_foursquare_id


	p_neighborhood = soup.find_all('p', attrs=("class", "text__373c0__2Kxyz text-color--normal__373c0__3xep9 text-align--left__373c0__2XGa- text-weight--semibold__373c0__2l0fe"))
	print(p_neighborhood)
	# neighborhood = p_neighborhood[1].get_text()	
	# print("neighborhood", neighborhood)
	# info['Neighborhood'] = neighborhood

	info['Neighborhood'] = ''

	yelp_categories = []
	try:
		print(script_out)
		yelp_categories = [script_out["servesCuisine"]]
	except:
		yelp_categories = []
	print("FS categories:", categories)
	print(categories)
	print(yelp_categories)
	categories = categories + yelp_categories
	print("FS + Yelp categories:", categories)
	if(len(categories) > 0):
		categories = ", ".join(set(categories))
	else:
		categories = ""

	info['Categories'] = [categories]
	# info['ChainID'] = chain_id
	print("info in scrape_info", info)
	return info

def gather_categories(name, address, city, state, zipcode, yelp_id):
	city_state = city + ", " + state
	try:
		if(math.isnan(float(state))):
			city_state = city
			state = ''
	except:
		pass
	print(name, address, city, state, zipcode, city_state)
	vens = client.venues.search({'near' : city_state, 'intent' : 'match', 'name' : name, 'address' : address, 'city' : city, 'state' : state, 'zipcode' : zipcode})
	categories = []
	if 'venues' in vens and vens['venues'] != []:
		for restaurant in vens['venues']:
			try:	
				foursquare_address = restaurant['location']['address']
			except:
				foursquare_address = ""
			if address_match(foursquare_address, address):
				for category in vens['venues'][0]['categories']:
					categories.append(category['shortName'])

	wiki = "https://www.yelp.com/biz/" + yelp_id
	try:
		page = urlopen(wiki)
	except:
		if '%' in yelp_id:
			yelp_id = yelp_id[:yelp_id.index('%')]
		wiki = "https://www.yelp.com/biz/" + yelp_id
		page = urlopen(wiki)

	soup = BeautifulSoup(page, "lxml")

	script_out = None

	script_jsons = soup.find_all("script", type="application/ld+json")
	for script_json in script_jsons:
		loaded = json.loads(script_json.text)
		if 'aggregateRating' in loaded:
			script_out = loaded

	yelp_categories = []
	try:
		yelp_categories = [script_out["servesCuisine"]]
	except:
		yelp_categories = []

	print("FS categories:", categories)
	categories = categories + yelp_categories
	if(len(categories) > 0):
		print(categories)
		categories = set(categories)
	print("FS + Yelp categories:", categories)

	categories = ", ".join(set(categories))

	return categories

# Save info as a file using pickle library 
def write(info, restaurant_tag):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	with open(script_dir + "/output_info/" + restaurant_tag + ".txt", 'wb') as f:
		pickle.dump(info, f)

def address_match(yelp_address, input_address):
	yelp_address = re.sub('[^0-9]','', yelp_address)
	input_address = re.sub('[^0-9]','', input_address)
	
	if(yelp_address[:2] == input_address[:2]):
		return True
	return False


def run_scrape_info(yelp_id, foodie_id, foursquare_id, input_address, chain_id, f_suffix, row):	
	info = scrap_data(yelp_id, foursquare_id, chain_id, row)
	write(info, foodie_id)
	save_excel(info, f_suffix, row)
	return True

def save_excel(info, f_suffix, row):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	file_path = script_dir + "/csvfiles/final/" + f_suffix + "-final.xlsx"
	print("seeing if file exists", path.exists(file_path))
	print(info)
	if(path.exists(file_path)):
		df = pd.read_excel(file_path)
		df = df.append({ 'Name': row['Name'], 
						'Address': info['Address'][0],
						'City': row['City'],
						'State': row['State'],
						'Zipcode': info['Zipcode'][0],
						'Description': info['Description'],
						'DollarSign': info['DollarSign'],
						'Latitude': info['Latitude'],
						'Longitude': info['Longitude'],
						'Neighborhood': row['Neighborhood'],
						'Categories': info['Categories'][0],
						'FoursquareID': info['FoursquareID'],
						'YelpID': info['YelpID']
						}, ignore_index=True)
		writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
		df1 = pd.DataFrame(df)
		df1 = df1[['Name', 'Neighborhood', 'Address', 'City', 'State', 'Zipcode', 'Description', 'DollarSign', 'Latitude', 'Longitude', 'Categories', 'FoursquareID', 'YelpID']]
		df1.to_excel(writer, index=False, sheet_name='Info')
		print("Compiled.") 
		writer.close()

	else:
		writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
		df1 = pd.DataFrame(info)
		df1 = df1[['Name', 'Address', 'City', 'State', 'Zipcode', 'Description', 'DollarSign', 'Latitude', 'Longitude', 'Neighborhood', 'Categories', 'FoursquareID', 'YelpID']]
		df1.to_excel(writer, index=False, sheet_name='Info')
		print("Compiled.") 
		writer.close()

if __name__ == '__main__':
	name = 'Rubirosa'
	address = '235 Mulberry St'
	city = 'New York'
	state = 'NY'
	zipcode = 10012
	google_maps_neighborhood(name, address, city, state, zipcode)