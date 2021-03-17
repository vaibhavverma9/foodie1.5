#!/usr/bin/env python
# encoding: utf-8

import os, csv, pickle
from nltk import word_tokenize
import pandas as pd 
import numpy as np
import argparse as ap
import ftfy

# Reads items from file 
def read_items(script_dir, filename):
	df = pd.read_csv(script_dir + "/csvfiles/mturk/output/" + filename, sep=',', usecols=[27,28,29,30,31,32,33], encoding='latin1')
	return df 

def process(row):
	print(row.loc['Input.website_url'])
	menu = row.loc['Input.menu']
	categories = strip_and_capitalize(row.loc['Answer.Category'].split('|'), 'Answer.Category')
	descriptions = strip_and_capitalize(row.loc['Answer.Description'].split('|'), 'Answer.Description')
	items = strip_and_capitalize(row.loc['Answer.Menu Item'].split('|'), 'Answer.Menu Item')
	prices = strip_and_capitalize(row.loc['Answer.Price'].split('|'), 'Answer.Price')
	return items, descriptions, prices, categories, menu

def strip_and_capitalize(elements, column):
	arr = []
	for element in elements:
		if element == conversion[column] or element == 'N/A':
			element = ''
		elif(column == 'Answer.Category' or column == 'Answer.Menu Item'):
			element = element.title()
			element = replace_caps(element)
		elif(column == 'Answer.Price'):
			try:
				element = int(float(element.replace('$', '')))
			except:
				element = ""
		arr.append(element)
	return arr 

def replace_caps(element):
	for word in words_to_not_capitalize:
		titled_word = word.title()
		element = element.replace(titled_word, word)
	return element

words_to_not_capitalize = [' a ', ' an ', ' the ', ' at ', ' by ', ' for ', ' in ', ' of ', ' on ', ' to ', ' up ', ' and ', ' as ', ' but ', ' or ', ' nor ', ' from ', ' with ']
conversion = {'Answer.Category' : 'Category', 'Answer.Menu Item' : 'Menu Item', 'Answer.Description' : 'Description', 'Answer.Price' : 'Price'}

def add_items(pickle_data, items, descriptions):
	for i in range(len(items)):
		pickle_data['Food'].append([ftfy.fix_encoding(items[i]), ftfy.fix_encoding(descriptions[i])])
	return pickle_data

# Save menu_items as a file using pickle library (not necessarily human readable)
def write(script_dir, menu_items, restaurant_tag):
	with open(script_dir + "/output_menu_items/" + restaurant_tag + ".txt", 'wb') as f:
		pickle.dump(menu_items, f)

if __name__ == '__main__':
	replace_caps("happy")

	parser = ap.ArgumentParser()
	parser.add_argument('-t', '--restaurant_tag', help='Restaurant tag', default='girl-and-the-goat-chicago')
	
	args = vars(parser.parse_args())

	restaurant_tag = args['restaurant_tag']
	filename = restaurant_tag + "-batch-results.csv"
	
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	df_read = read_items(script_dir, filename)
	
	df_fin = pd.DataFrame(columns=['Categories', 'Item', 'Description', 'Price'], index=None)

	pickle_data = {}
	pickle_data['Food'] = []

	for (idx, row) in df_read.iterrows():
		items, descriptions, prices, categories, menu = process(row)
		categories = categories[:len(items)]
		items = items[:len(items)]
		descriptions = descriptions[:len(items)]
		prices = prices[:len(items)]
		menus = [menu] * len(items)
		pickle_data = add_items(pickle_data, items, descriptions)
		df_temp = pd.DataFrame({'Item' : items, 
								'Description' : descriptions, 
								'Price' : prices, 
								'Category' : categories, 
								'Menu' : menus})
		df_fin = df_fin.append(df_temp)
	'''
	cols = ['Item', 'Description', 'Price', 'Categories', 'Menu']
	df_fin = df_fin[cols]

	df_fin = df_fin[df_fin['Item'] != '']
	write(script_dir, pickle_data, restaurant_tag)
	
	df_fin.to_excel(script_dir + "/csvfiles/items/" + restaurant_tag + "-items.xlsx", sheet_name='Sheet1')
	'''