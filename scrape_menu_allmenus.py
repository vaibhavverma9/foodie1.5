# -*- coding: utf-8-sig-*-

import ast, json, string, operator, re, os, pickle, math
import argparse as ap
from bs4 import BeautifulSoup
from urllib.request import urlopen
from pathlib import Path
import requests
from scrape_menu_items import write_menu

# Pull Allmenus HTML 
def pull_allmenus_html(allmenus_id):
	url = "https://www.allmenus.com/" + allmenus_id + '/menu'
	r = requests.get(url)
	encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
	soup = BeautifulSoup(r.content, from_encoding=encoding) # BeautifulSoup produces HTML of webpage
	return soup

def clean(text):
	return text.strip().replace('&comma;', ',')

def pull_items(soup):
	menu_items = {}
	menu_items['Food'] = []
	items_html = soup.find_all('li', attrs={'class' : 'menu-items'})
	for item_html in items_html:
		category_html = item_html.parent.parent
		item = clean(item_html.find('span', attrs={'class' : 'item-title'}).get_text())
		price = clean(item_html.find('span', attrs={'class' : 'item-price'}).get_text().strip())
		description = clean(item_html.find('p', attrs={'class' : 'description'}).get_text().strip())
		category = clean(category_html.find('div', attrs={'class' : 'h4 category-name menu-section-title'}).get_text().strip())
		menu_items['Food'].append([item, description, price, category, ''])
	return menu_items

# Save menu_items as a file using pickle library (not necessarily human readable)
def write_allmenus_menu(menu_items, allmenus_id):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	with open(script_dir + "/output_menu_items/allmenus/" + allmenus_id.replace('/', '-') + ".txt", 'wb') as f:
		pickle.dump(menu_items, f)

def scrape_allmenus_menus(allmenus_id, foodie_id):
	soup = pull_allmenus_html(allmenus_id)
	menu_items = pull_items(soup)
	write_menu(menu_items, foodie_id)
	return True

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-a', '--allmenus_id', help='Allmenus ID', default='il/chicago/338299-girl-the-goat')
	parser.add_argument('-f', '--foodie_id', help='Foodie ID', default='girl--the-goat-807')

	args = vars(parser.parse_args())
	allmenus_id = args['allmenus_id']
	foodie_id = args['foodie_id']
	
	menu_items = scrape_allmenus_menus(allmenus_id, foodie_id)
	