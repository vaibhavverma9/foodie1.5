import os, json, re, csv, pickle, string
import pandas as pd
import sys, time
import argparse as ap
from nltk.tokenize import sent_tokenize, word_tokenize, RegexpTokenizer
from nltk.corpus import stopwords
from aylienapiclient import textapi
import spacy
from menu_from_db import extract_json, save_locally

# Set up ids and keys from AYLIEN 
ids = ["ca16d389", "c1d8b559", "223c1a5b"] 
keys = ["7c89bd682b4dddd68404b32e342901fb", "d62a26c46dba4da09c526455d2a27055", "3772a183fe2fc77774e7448b2d8ff919"]
keywords = ['healthy', 'spicy', 'sweet', 'salty', 'vegetarian', 'vegan', 'gluten-free', 'huge', 'bland', 'tasty', 'unique', 'creamy', 'fresh', 'dry', 'sour', 'tangy', 'authentic', 'heavy', 'rich', 'small', 'large', 'big']

# Set up regular expression tokenizer
tokenizer = RegexpTokenizer(r'\w+')

nlp = spacy.load('en_core_web_sm')

# Reads menu_items from file 
def read_items(script_dir, restaurant_tag):
	filename = script_dir + "/output_menu_items/foodie/" + restaurant_tag + ".txt"
	if os.path.exists(filename):	
		with open(filename, 'rb') as f:
			menu_items = pickle.load(f)
	else:
		json = extract_json(restaurant_tag)
		menu_items = save_locally(json, restaurant_tag)
	return menu_items

# Read reviews from file 
def read_reviews(script_dir, restaurant_tag):
	print(script_dir + "/output_reviews/" + restaurant_tag + ".txt")
	with open(script_dir + "/output_reviews/" + restaurant_tag + ".txt", 'rb') as f:
		output = pickle.load(f)
	return output

def substring_match(sentence_words, item_words, n, foodie_id, exceptions):
	# determine n and length of words set 
	restaurant_words = re.split('_', foodie_id)
	n = min(len(item_words), n)	
	len_sentence = len(sentence_words)
	len_word = len(item_words)

	# add buffer 
	for i in range(n):
		sentence_words.append("NA_sentence")
		item_words.append("NA_item")

	# determine if item is in sentence
	for i in range(len_sentence):
		for j in range(len_word):
			if(sentence_words[i:i+n] == item_words[j:j+n]):
				if(n - len(contains_word(item_words, exceptions)) > 0):
					return True
	return False

def items_in_sentence(sentence, menu_items, n, foodie_id, exceptions):
	# set array to add items if in sentence
	items = []

	# remove punctuation and word tokenize sentence
	sentence_words = tokenizer.tokenize(sentence.lower())

	if menu_items == None:
		return []

	# loop through each item
	for menu in menu_items: 
		for menu_item in menu_items[menu]:
			# remove punctuation and word tokenize item
			item = str(menu_item[0])
			item_without_punctuation = item.translate(str.maketrans('','',string.punctuation))
			item_words = tokenizer.tokenize(item_without_punctuation.lower())
			
			# check if there is a subtring match of n consecutive words 
			if(substring_match(sentence_words, item_words, n, foodie_id, exceptions)):
				items.append(item)

	return set(items)

def percentage_of_words_in_sentence(item_words, sentence_words):
	if(len(item_words) == 0 or len(sentence_words) == 0):
		return 0.
	n = min(max(1, len(item_words)), 4)
	count = 0. 
	for item_word in item_words:
		if item_word in sentence_words:
			count += 1
	return count / n

def optimize_list(items, sentence):
	sentence_words = tokenizer.tokenize(sentence)

	# optimize for percentage of item words in sentence	
	pmax = 0. 
	poptimized_items = []
	for item in items:
		item_words = tokenizer.tokenize(item.lower())
		
		# ensures not more 15 matches per item
		if item not in item_count:
			item_count[item] = 1
		else:
			item_count[item] += 1
		if(item_count[item] > 15):
			continue
		# item_words = tokenizer.tokenize(item.lower())
		if(len(item_words) == 1 and item_count[item] > 5):
			continue

		p = percentage_of_words_in_sentence(item_words, sentence_words)
		n = min(len(item_words), 4)

		thresholds = {0 : 1, 1 : 1, 2 : 1, 3 : 0.66, 4 : 0.5}

		if p < thresholds[n]:
			continue 
		if p == pmax:
			poptimized_items.append(item)
		elif p > pmax:
			pmax = p
			poptimized_items = [item]

	# optimize for longest word 
	nmax = 0. # max number of words 
	noptimized_items = []
	for item in poptimized_items:
		item_words = tokenizer.tokenize(item.lower())

		n = len(item_words)
		if n == nmax:
			noptimized_items.append(item)
		elif n > nmax:
			nmax = n
			noptimized_items = [item]

	return noptimized_items

def contains_word(sentence, words):
	word_list = []
	for word in words:
		if word in sentence:
			word_list.append(word)
	return word_list

def contains_word_or_not(sentence, words):
	word_list = []
	for word in words:
		if word in sentence:
			not_word = 'not ' + word
			if not_word in sentence:
				word_list.append(not_word)
			else:
				word_list.append(word)
	return word_list

def arr_to_str(word_list):
	string = ""
	for word in word_list:
		if len(string) == 0:
			string = word 
		else:
			string = string + ", " + word
	return string

item_count = {}

def items_in_sentence_spacy(sentence, menu_items, exceptions, n):
	doc = nlp(sentence)
	items = []
	for chunk in doc.noun_chunks:
		obj = chunk.text
		matched_item = match(obj, menu_items, exceptions, n)
		if(matched_item == ""):
			continue

		# ensures not more 15 matches per item
		if matched_item not in item_count:
			item_count[matched_item] = 1
		else:
			item_count[matched_item] += 1
		if(item_count[matched_item] > 15):
			continue

		item_words = tokenizer.tokenize(matched_item.lower())

		items.append(matched_item)

	return set(items)

def remove_exceptions(words, exceptions):
	final = []
	for word in words:
		if word not in exceptions:
			final.append(word)
	return final

def match(obj, menu_items, exceptions, n):
	thresholds = {0 : 1, 1 : 1, 2 : 1, 3 : 0.66, 4 : 0.5}
	if n <= 1:
		thresholds = {0 : 1, 1 : 1, 2 : 0.5, 3 : 0.33, 4 : 0.25}

	max_p = 0.
	matched_item = ""
	for menu in menu_items: 
		for menu_item in menu_items[menu]:
			# remove punctuation and word tokenize item
			item = str(menu_item[0])
			item_without_punctuation = item.translate(str.maketrans('','',string.punctuation))
			item_words = tokenizer.tokenize(item_without_punctuation.lower())
			obj_words = tokenizer.tokenize(obj.lower())

			item_words = remove_exceptions(item_words, exceptions)
			obj_words = remove_exceptions(obj_words, exceptions)
			n = min(max(len(item_words), 2), 4)
			
			p = percentage_of_words_in_sentence(item_words, obj_words)
			# print(p, item_words, obj_words)
			if(p < thresholds[n]):
				continue
			if(p > max_p):
				max_p = p
				matched_item = item
	return matched_item

def run_match_sentences(foodie_id, n, c):
	client = textapi.Client(ids[c], keys[c])

	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	menu_items = read_items(script_dir, foodie_id)
	output = read_reviews(script_dir, foodie_id)

	exceptions = ['a', 'an', 'of', 'the', 'is', 'with', 'or', 'and', 'to', 'from'] + foodie_id.split('-')
	neutral_words = ['had', 'shared', 'got', 'ordered', 'came', 'decided', 'went', 'started', 'tried', 'split', 'served', 'get', 'chose']

	# set arrays 
	sentence_output = []
	item_output = []
	keyword_output = []

	i = 0 
	j = 0
	for review in output:
		tokenized_sentences = sent_tokenize(review)
		for tokenized_sentence in tokenized_sentences:
			print(tokenized_sentence)

			# remove sentence if it does not contain a menu item 
			items_in_given_sentence = items_in_sentence_spacy(tokenized_sentence, menu_items, exceptions, n)
			# items_in_given_sentence = items_in_sentence(tokenized_sentence, menu_items, n, foodie_id, exceptions)
			if(len(items_in_given_sentence) == 0):
				continue

			# optimized_items = optimize_list(items_in_given_sentence, tokenized_sentence.lower())
			keyword_matches = arr_to_str(contains_word_or_not(tokenized_sentence, keywords))
			for item in items_in_given_sentence:
				sentence_output.append(tokenized_sentence)
				item_output.append(item)
				keyword_output.append(keyword_matches)					
				i += 1

		# adjusting n depending on number of matches
		if j % 50 == 0 and j != 0:
			if i > j:
				n += 1
			if i < j / 4:
				n = max(1, n - 1)

		# break once there are over 200 matches
		if i > 200:
			break 

		j += 1 
		print(i, j)
		

	d = {'Item' : item_output, 'Sentence' : sentence_output, 'Keywords' : keyword_output}

	df = pd.DataFrame(d)
	df.to_excel(script_dir + "/csvfiles/sentences/labeled/" + foodie_id + "-labeled.xlsx", sheet_name='Sheet1', encoding="utf8")
	return i 

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-t', '--restaurant_tag', help='Restaurant tag', default='girl-and-the-goat-chicago')
	parser.add_argument('-n', '--substring_match', help='Substring match', default='2')
	parser.add_argument('-c', '--client', help='Client', default='0')

	args = vars(parser.parse_args())
	restaurant_tag = args['restaurant_tag']
	n = int(args['substring_match'])
	c = int(args['client'])
	print("running match sentences")
	run_match_sentences(restaurant_tag, n, c)
	