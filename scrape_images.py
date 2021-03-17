from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from scrape_menu_yelp import read_menu
from save_sentences_csv import remove_sentence, items_in_sentence, optimize_list
from aylienapiclient import textapi
from nltk.tokenize import sent_tokenize
from pathlib import Path
import time, random, os, pickle,requests
import argparse as ap
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

# Pull Yelp HTML 
def pull_yelp_html(userid, n):
	url = "https://www.yelp.com/user_details_reviews_self?rec_pagestart=" + str(n) + "&" + userid
	r = requests.get(url)
	encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
	soup = BeautifulSoup(r.content, from_encoding=encoding) # BeautifulSoup produces HTML of webpage
	return soup

def scrape_images(userid):
	data = []
	maxn = count(userid)
	n = 0
	c = 0

	while(n < maxn):
		print(n)
		soup = pull_yelp_html(userid, n)
		images = soup.find_all('img', attrs={'class' : 'photo-box-img'})
		for image in images:
			review_detail = image.parent.parent.parent.parent.parent.parent
			restaurantDetail = review_detail.find('a', attrs={'class' : "biz-name js-analytics-click", 'data-analytics-label' : "biz-name"})

			if restaurantDetail == None:
				continue

			restaurantName = restaurantDetail.get_text()
			restaurantCode = restaurantDetail.get('href')[5:]

			if(image['alt'] == restaurantName):
				continue 

			menu_items = read_menu(restaurantCode)
			if(menu_items == None):
				continue 

			extended_caption = image['alt']
			items, c = match_sentence_item(extended_caption, menu_items, c)

			if items == []:
				continue

			photoid = str(random.randint(1, 10000000))
			photoFilename = userid + "-" + photoid + ".jpg"
			script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
			link = image['src']
			urlretrieve(link, script_dir + "/output_images/" + photoFilename)
			date = review_detail.find('span', attrs={'class' : "rating-qualifier"}).get_text()
			(month, day, year) = date.split('/')

			for item in items:
				data.append(["Yelp", userid, restaurantCode, month, day, year, photoFilename, item, extended_caption])
		n += 10
	print(data)
	return data

def write_user(data, userid):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	print("Saving user data at " + script_dir + "/output_user/" + userid + ".txt")
	with open(script_dir + "/output_user/" + userid + ".txt", 'wb') as f:
		pickle.dump(data, f)

def read_user(userid):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	fname = script_dir + "/output_user/" + userid + ".txt"
	if Path(fname).is_file():
		print("Reading existing file: ", userid)
		with open(script_dir + "/output_user/" + userid + ".txt", 'rb') as f:
			data = pickle.load(f)
		return data
	else:
		print("File does not exist: ", userid)
		return None

def match_sentence_item(sentence, menu_items, c):
	client = textapi.Client(ids[c], keys[c])
	neutral_words = ['got', 'shared', 'ordered', 'split', 'had']
	# remove sentence if it contains neutral-indicating words 
	if(remove_sentence(sentence, neutral_words)):
		return [], c

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

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-u', '--userid', help='User ID', default='userid=iFadxdXUK118lr-gx6-2tA')
	parser.add_argument('-c', '--client', help='Client', default='0')

	args = vars(parser.parse_args())
	userid = args['userid']
	c = int(args['client'])
	client = textapi.Client(ids[c], keys[c])
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))

	data = scrape_images(userid)
	s = pd.DataFrame(data, index=None, columns=['Source', 'SourceUserCode', 'SourceRestaurantCode', 'Month', 'Day', 'Year', 'Filename', 'Item', 'Caption']) 
	s.to_csv(script_dir + "/csvfiles/images/" + userid + ".csv", index=False)
	