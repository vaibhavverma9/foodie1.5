from bs4 import BeautifulSoup
from urllib.request import urlopen
from scrape_menu_yelp import read_menu
from save_sentences_csv import items_in_sentence, optimize_list
from aylienapiclient import textapi
from nltk.tokenize import sent_tokenize
from pathlib import Path
import time
import argparse as ap
import os, pickle,requests
import pandas as pd 

# Set up ids and keys from AYLIEN 
ids = ["ca16d389", "c1d8b559", "223c1a5b"] 
keys = ["7c89bd682b4dddd68404b32e342901fb", "d62a26c46dba4da09c526455d2a27055", "3772a183fe2fc77774e7448b2d8ff919"]


# count # of reviews 
def count(userid):
	url = "https://www.yelp.com/user_details?" + userid
	r = requests.get(url)
	encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
	soup = BeautifulSoup(r.content, from_encoding=encoding) # BeautifulSoup produces HTML of webpage
	count = soup.find('li', attrs={'class' : 'review-count'}).find('strong').get_text()
	return int(count)

def round_down(num, divisor):
    return num - (num%divisor)

# Pull Yelp HTML 
def pull_yelp_html(userid, n):
	url = "https://www.yelp.com/user_details_reviews_self?rec_pagestart=" + str(n) + "&" + userid
	r = requests.get(url)
	encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
	soup = BeautifulSoup(r.content, from_encoding=encoding) # BeautifulSoup produces HTML of webpage
	return soup

def scrape_comments(userid):
	data = []
	maxn = count(userid)
	n = 0

	while(n < maxn):
		print(n)
		soup = pull_yelp_html(userid, n)
		comments = soup.find_all('p', attrs={'lang': "en"})
		for comment in comments:
			review_detail = comment.parent.parent.parent
			date = review_detail.find('span', attrs={'class' : "rating-qualifier"}).get_text()
			restaurantCode = review_detail.find('a', attrs={'class' : "biz-name js-analytics-click", 'data-analytics-label' : "biz-name"}).get('href')[5:]
			text = comment.get_text()
			data.append([restaurantCode, text, date])
		n += 10
	return data

def write_user(data):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	print("Saving user data at " + script_dir + "/output_user/users.txt")
	with open(script_dir + "/output_user/users.txt", 'wb') as f:
		pickle.dump(data, f)

def read_user():
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	fname = script_dir + "/output_user/users.txt"
	if Path(fname).is_file():
		print("Reading existing file: output_user/users.txt")
		with open(script_dir + "/output_user/users.txt", 'rb') as f:
			data = pickle.load(f)
		return data
	else:
		print("File does not exist: ", userid)
		return None

def match_sentence_item(sentence, menu_items, c):
	client = textapi.Client(ids[c], keys[c])

	# remove sentence if it does not contain a menu item 
	items_in_given_sentence = items_in_sentence(sentence, menu_items, 2)
	if(len(items_in_given_sentence) == 0):
		return [], c

	# call API to gather sentiment analysis 
	try:
		sentiment = client.Sentiment({'text' : sentence})
	except:
		print("changing client from: ", c)
		c = (c + 1) % 3
		print("to: ", c)
		client = textapi.Client(ids[c], keys[c])
		try:
			sentiment = client.Sentiment({'text': tokenized_sentence})
		except: 
			print("Error: Too many subjectivity requests from API. Pausing for 5.")
			time.sleep(5)
			return [], c

	# remove sentence if it is objective or neutral
	if(sentiment['subjectivity'] == 'objective'):
		return [], c
			
	# add single item if list of items is one-item long 
	if(len(items_in_given_sentence) == 1):
		return [next(iter(items_in_given_sentence))], c

	# add most optimal item out of list of multiple items 
	if(len(items_in_given_sentence) > 1):
		optimized_items = optimize_list(items_in_given_sentence, sentence.lower())
		return optimized_items, c

def iterate_restaurants(data, userid, c):
	output = []
	for (restaurantCode, text, date) in data:		
		menu_items = read_menu(restaurantCode)
		if(menu_items == None):
			continue 

		for sentence in sent_tokenize(text):
			items, c = match_sentence_item(sentence, menu_items, c)
			if(items == []):
				continue
			for item in items:
				(month, day, year) = date.split('/')
				print("appending: ", sentence)
				output.append(('Yelp', userid, restaurantCode, month, day, year, item, sentence))
	return output

def iterate_users(data, restaurantCode, c):
	output = []
	menu_items = read_menu(restaurantCode)

	if(menu_items == None):
		print("No menus for: ", restaurantCode)
		return None

	for (userid, text, date) in data:
		for sentence in sent_tokenize(text):
			items, c = match_sentence_item(sentence, menu_items, c)
			if(items == []):
				continue
			for item in items:
				(month, day, year) = date.split('/')
				print("appending: ", sentence)
				output.append(('Yelp', userid, restaurantCode, month, day, year, item, sentence)) 
	return output

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-u', '--userid', help='User ID', default='userid=iFadxdXUK118lr-gx6-2tA')
	parser.add_argument('-o', '--option', help='0 to scrape by user, 1 to scrape by restaurant', default='0')
	parser.add_argument('-t', '--restaurantCode', help='Yelp Restaurant Code', default='girl-and-the-goat-chicago')

	args = vars(parser.parse_args())
	userid = args['userid']
	c = 0
	o = int(args['option'])
	restaurantCode = args['restaurantCode']
	client = textapi.Client(ids[c], keys[c])
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	userids = read_user()

	if o == 0:
		data = scrape_comments(userid)
		output = iterate_restaurants(data, userid, c)		
		if userid not in userids:
			userids.append(userid)
			write_user(userids)
		s = pd.DataFrame(output, index=None, columns=['Source', 'SourceUserCode', 'YelpID', 'Month', 'Day', 'Year', 'Item', 'Sentence']) 
		s.to_csv(script_dir + "/csvfiles/comments/" + userid + ".csv", index=False)
	elif o == 1:
		with open(script_dir + "/output_reviews/" + restaurantCode + "-users.txt", 'rb') as f:
			data = pickle.load(f)
		output = iterate_users(data, restaurantCode, c)
		s = pd.DataFrame(output, index=None, columns=['Source', 'SourceUserCode', 'YelpID', 'Month', 'Day', 'Year', 'Item', 'Sentence']) 
		s.to_csv(script_dir + "/csvfiles/comments/" + restaurantCode + ".csv", index=False)




	