# -*- coding: utf-8-sig-*-

import ast, json, string, operator, re, os, pickle, math
import argparse as ap
from bs4 import BeautifulSoup
from urllib.request import urlopen
from pathlib import Path
import requests
from rotating_proxies import get_proxies, rotate_proxies

# Pull Yelp HTML 
def pull_yelp_html(restaurant_sublink):
	url = "https://www.yelp.com" + restaurant_sublink
	r = requests.get(url)

	if(str(r.status_code) != '200'):
		r = rotate_proxies(r, url)

	encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
	soup = BeautifulSoup(r.content, from_encoding=encoding) # BeautifulSoup produces HTML of webpage
	return soup

# Scrapes menu data from Yelp 
def scrape_yelp_items(soup, menu_name):
	menu_items = []
	headers = soup.find_all(["h2", "h4"])
	section = ""

	for header in headers[1:len(headers)-1]:
		if(header.attrs != {}):
			section = header.get_text().strip()

		if(header.attrs == {}): 
			item = header.get_text().strip()
			# item = item.lstrip('0123456789.- ')
			parent = header.parent.parent
			description = parent.find('p', attrs={"class" : "menu-item-details-description"})
			price = parent.find('li', attrs={"class" : "menu-item-price-amount"})

			if(description == None):
				description = ""
			else:
				description = description.get_text().strip()

			if(price == None):
				price = ""
			else:
				price = price.get_text().strip()
				try:
					price = round(float(price[1:].replace(',', '')))
				except:
					pass

			menu_items.append([item, description, price, section, menu_name])

	return menu_items
	
# Find menus 
def find_yelp_menus(soup, restaurant_sublink):
	menus = []
	for menu in soup.find_all('li', attrs={'class': "sub-menu inline-block"}):
		for holder in menu.find_all('a'):
			menus.append([holder.get('href'), holder.get_text()])
		for holder in menu.find_all('strong'):
			menus.append([restaurant_sublink + "/" + holder.get_text().lower(), holder.get_text()])
	return menus

# Save menu_items as a file using pickle library (not necessarily human readable)
def write_menu(menu_items, restaurant_tag):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	with open(script_dir + "/output_menu_items/foodie/" + restaurant_tag + ".txt", 'wb') as f:
		pickle.dump(menu_items, f)

# Save menu_items as a file using pickle library (not necessarily human readable)
def write_yelp_menu(menu_items, restaurant_tag):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	with open(script_dir + "/output_menu_items/yelp/" + restaurant_tag + ".txt", 'wb') as f:
		pickle.dump(menu_items, f)

# Reads menu_items from file 
def read_menu(foodie_id):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	fname = script_dir + "/output_menu_items/foodie/" + foodie_id + ".txt"
	try:
		if Path(fname).is_file():		
			with open(script_dir + "/output_menu_items/foodie/" + foodie_id + ".txt", 'rb') as f:
				menu_items = pickle.load(f)
			return menu_items
		else:
			return None 
	except:
		return None 

def scrape_yelp_menus(yelp_id, foodie_id):
	restaurant_sublink = '/menu/' + yelp_id
	soup = pull_yelp_html(restaurant_sublink)
	menu_items = {}		
	menus = find_yelp_menus(soup, restaurant_sublink)

	i = 0

	if not menus:
		menu_items['Food'] = scrape_yelp_items(soup, "")
		i += len(menu_items['Food'])
	else:
		for (link, name) in menus:
			link = link.replace(' ', '-')
			soup = pull_yelp_html(link)
			menu_items[name] = scrape_yelp_items(soup, name)
			i += len(menu_items[name])

	# insufficient number of menu items
	if i < 6:
		return False
	write_yelp_menu(menu_items, yelp_id)
	write_menu(menu_items, foodie_id)

	return True 

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-t', '--restaurant_tag', help='Restaurant tag', default='girl-and-the-goat-chicago')

	args = vars(parser.parse_args())
	restaurant_tag = args['restaurant_tag']
	scrape_yelp_menus(restaurant_tag, restaurant_tag)

