import os, pickle
import pandas as pd 
import numpy as np 
import argparse as ap
import re
from nltk.tokenize import sent_tokenize

def title_except(text, exceptions):
	special_chars = ['[', '{', '(', '\"', '\'', '“', '-']
	word_list = re.split(' ', text)       # re.split behaves as expected
	final = []
	for i in range(len(word_list)):
		word = word_list[i]
		if(word == ""):
		 	continue
		# Handling special_chars
		if(word[0] in special_chars):
			subword = word[1:]
			if subword in exceptions:
				final.append(word.lower())
			else:
				subword = capitalize_word(subword)
				word = word[0] + subword
				final.append(word)
				
		# Handling no special_chars
		else:
			if word.lower() in exceptions and i != 0:
				word = word.lower()
			elif '.' in word and hasNumbers(word):
				word = ''
			elif '.' in word:
				word = word
			else:
				word = capitalize_word(word)

			final.append(word)
	
	return " ".join(final)

def hasNumbers(inputString):
	return bool(re.search(r'\d', inputString))

def capitalize_word(text):
	special_upper_case_words = ["BLT", "BBQ"]
	if not text.islower() and not text.isupper():
		return text
	elif text in special_upper_case_words:
		return text
	else:
		return text.capitalize()

def capitalize_sentences(text):
	sentences = sent_tokenize(text.lstrip())
	sentences = [sent.capitalize() for sent in sentences]
	return " ".join(sentences)

# Save menu_items as a file using pickle library (not necessarily human readable)
def write(menu_items, restaurant_tag):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	with open(script_dir + "/output_menu_items/foodie/" + restaurant_tag + ".txt", 'wb') as f:
		pickle.dump(menu_items, f)

def remove_parenthesis(text):
	if '(' in str(text):
		index = str(text).find('(')
		return str(text)[:index]
	return str(text)

def remove_dollar(price):
	price = str(price).replace('$', '').replace('+', '')
	prices = []
	for p in price.split():
		try:
			prices.append(float(p))
		except:
			pass
	if prices == []:
		prices.append('')
	return prices

def run_save_items_pickle(foodie_id, item_file_name):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	items_file_path = script_dir + "/csvfiles/items/" + item_file_name + "-items.xlsx"
	
	menu_items = {}
	menu_items['Food'] = []
	articles = ['a', 'an', 'of', 'the', 'is', 'with', 'or', 'and', 'w/', 'di', 'to', 'from', 'by', 'on', 'at', 'for', 'oz']
	df = pd.read_excel(items_file_path)
	df = df.replace(np.nan, '', regex=True)
	for index, row in df.iterrows():
		prices = remove_dollar(row['Price'])
		for price in prices:
			row['Item'] = title_except(row['Item'].lstrip(), articles)
			row['Categories'] = title_except(row['Categories'].lstrip(), articles)
			row['Categories'] = row['Categories'].replace(' (Must Be 21 to Purchase)', '')
			row['Menu'] = title_except(row['Menu'].lstrip(), articles)
			row['Description'] = row['Description'][0:1].capitalize() + row['Description'][1:]
			row['Description'] = row['Description'].replace('Must be 21 to purchase.', '')
			row['Price'] = price
			# row['Tags'] = row['Tags'].upper()
			if(pd.isna(row['Item']) == False):
				menu_items['Food'].append(row)
	write(menu_items, foodie_id)
	return True

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-f', '--foodie_id', help='Foodie ID', default='the-cheesecake-factory-elmhurst-11373')
	parser.add_argument('-i', '--item_file_name', help='Item File Name', default='the-cheesecake-factory-elmhurst-11373')

	args = vars(parser.parse_args())
	foodie_id = args['foodie_id']
	item_file_name = args['item_file_name']
	run_save_items_pickle(foodie_id, item_file_name)
	