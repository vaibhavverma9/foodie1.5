# -*- coding: utf-8-sig-*-

import ast, json, string, operator, re, os, pickle, math
import argparse as ap
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests

# Pull Yelp HTML 
def pull_yelp_html(restaurant_sublink):
	wiki = "https://www.yelp.com" + restaurant_sublink
	try:
		page = urlopen(wiki)
	except:
		print("Did not work: ", wiki)
		if '%' in wiki:
			wiki = wiki[:wiki.index('%')]
		page = urlopen(wiki)

	soup = BeautifulSoup(page, "lxml")
	return soup

# Pull Yelp HTML 
def pull_ot_html(restaurant_tag):
	url = "https://www.opentable.com/" + restaurant_tag
	r = requests.get(url)
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
				price = round(float(price[1:].replace(',', '')))

			menu_items.append([item, description, price, section, menu_name])

	return menu_items

# Scrapes menu names from OpenTable 
def scrape_ot_menus(soup):
	i = 1
	menus = []
	while(1):
		menu_link = "menu-" + str(i) + "-link"
		menu = soup.find('button', attrs={'id' : menu_link})
		if(menu == None):
			break
		else:
			menus.append(menu.get_text())
			i += 1
	return menus

# Scrape menu items from OpenTable
def scrape_ot_items(soup):
	menu_items = {}
	menus = scrape_ot_menus(soup)
	for i, div in enumerate(soup.find_all(class_='menuContent')):
		menu_name = menus[i]
		menu_items[menu_name] = []
		for div_item in div.find_all(class_='menu-item f42dd212'):
			item_div = div_item.find(class_="menu-item-title")
			if item_div == None:
				continue
			else:
				item = item_div.get_text()

			section_div = div_item.parent.parent.find('h3')
			if section_div == None:
				section = ""
			else:
				section = section_div.get_text()

			description_div = div_item.find(class_="menu-item-desc")
			if description_div == None:
				description = ""
			else:
				description = description_div.get_text()

			price_div = div_item.find(class_="menu-item-price c9ba0d02")			
			price_options_div = div_item.find_all(class_="menu-option-price c9ba0d02")
			if price_div != None:
				price = price_div.get_text()
			elif price_options_div != []:
				price = price_options_div[0].get_text()
			else:
				price = ""

			menu_items[menu_name].append([item, description, price, section, menu_name])

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

# Find categories 
def find_categories(soup):
	categories = []
	for category in soup.find_all('h2', attrs={'class': "alternate"}):
		categories.append(category.get_text().strip())
	return categories

# Save menu_items as a file using pickle library (not necessarily human readable)
def write_menu(menu_items, restaurant_tag):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	with open(script_dir + "/output_menu_items/" + restaurant_tag + ".txt", 'wb') as f:
		pickle.dump(menu_items, f)

# Reads menu_items from file 
def read_menu(restaurant_tag):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	fname = script_dir + "/output_menu_items/foodie/" + restaurant_tag + ".txt"
	try:
		if Path(fname).is_file():		
			print("Reading existing menu: ", restaurant_tag)
			with open(script_dir + "/output_menu_items/foodie/" + restaurant_tag + ".txt", 'rb') as f:
				menu_items = pickle.load(f)
			return menu_items
		else:
			print("Menu does not exist: ", restaurant_tag)
			return None 
	except:
		return None 


if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-t', '--restaurant_tag', help='Restaurant tag', default='girl-and-the-goat-chicago')
	parser.add_argument('-ot', '--ot_restaurant_tag', help='OpenTable restaurant tag', default='r/girl-and-the-goat-chicago')
	parser.add_argument('-s', '--source', help='Source: 0 (Yelp) or 1 (OpenTable)', default='0')

	args = vars(parser.parse_args())
	restaurant_tag = args['restaurant_tag']
	ot_restaurant_tag = args['ot_restaurant_tag']
	source = int(args['source'])

	if(source == 0):
		restaurant_sublink = '/menu/' + restaurant_tag
		soup = pull_yelp_html(restaurant_sublink)
		menu_items = {}		
		menus = find_yelp_menus(soup, restaurant_sublink)

		if not menus:
			menu_items['Food'] = scrape_yelp_items(soup, "")
		else:
			for (link, name) in menus:
				link = link.replace(' ', '-')
				soup = pull_yelp_html(link)
				menu_items[name] = scrape_yelp_items(soup, name)

		write_menu(menu_items, restaurant_tag)
	elif(source == 1):
		soup = pull_ot_html(ot_restaurant_tag)
		menu_items = scrape_ot_items(soup)
		write_menu(menu_items, restaurant_tag)
	