import os
import re
import argparse as ap
import joblib
import numpy as np
import pandas as pd
# import tensorflow as tf
import spacy, traceback

# from keras.models import load_model
# from keras.preprocessing.sequence import pad_sequences
from aylienapiclient import textapi


ASSETS_PATH = os.path.join(os.getcwd(), 'assets')
model = graph = nlp = tokenizer = None

# Set up ids and keys from AYLIEN 
ids = ["ca16d389", "c1d8b559", "223c1a5b", "0fe78353"] 
keys = ["7c89bd682b4dddd68404b32e342901fb", "d62a26c46dba4da09c526455d2a27055", "3772a183fe2fc77774e7448b2d8ff919", "cd79c739d444bfec131a1f9833425a2f"]
keywords = ['healthy', 'spicy', 'sweet', 'salty', 'vegetarian', 'vegan', 'gluten-free', 'huge', 'bland', 'tasty', 'unique', 'creamy', 'fresh', 'dry', 'sour', 'tangy', 'authentic', 'heavy', 'rich', 'small', 'large', 'big']


# def load_pretrained_models():
# 	global model, graph, nlp, tokenizer
# 	model = load_model(os.path.join(ASSETS_PATH, 'model.h5'))
# 	graph = tf.get_default_graph()
# 	nlp = spacy.load('en', disable=['parser', 'tagger', 'ner'])
# 	tokenizer = joblib.load(os.path.join(ASSETS_PATH, 'tokenizer.pkl'))


def preprocess(text, lowercase=True, remove_stopwords=False):
	if lowercase:
		text = text.lower()
	text = nlp(text)
	lemmatized = []
	for word in text:
		lemma = word.lemma_.strip()
		if lemma:
			if remove_stopwords and word.is_stop:
				continue
			lemmatized.append(lemma)

	return ' '.join(lemmatized)


def predict(reviews):
	# with graph.as_default():
	# 	texts = [preprocess(r) for r in reviews]
		# prepared_text = pad_sequences(tokenizer.texts_to_sequences(texts), maxlen=100)
		# predictions_proba = model.predict(prepared_text)
		# try: 
		# 	final_predictions = np.argmax(predictions_proba, axis=1) + 1
		# except:
	final_predictions = []
	return final_predictions

def remove_weird_sentences(reviews):
	for i, row in reviews.iterrows():
		if(str(row['Sentence']) == '0'):
			reviews = reviews.drop([i])
	return reviews

def clean(reviews, c):
	# remove all 1 star ratings (too inaccurate)
	reviews = reviews.loc[reviews['Rating'] != 1]

	for i, row in reviews.iterrows():
		reviews.loc[i, 'Rating'] = row['Rating'] * 2 - 1

	# remove 3 star objective sentences
	'''
	client = textapi.Client(ids[c], keys[c])
	sentiment = client.Sentiment({'text': 'We ordered the fish.'})

	for i, row in reviews.iterrows():
		print(i)
		if(row['Rating'] == 3):
			# call API to gather sentiment analysis 
			try:
				sentiment = client.Sentiment({'text': row['Sentence']})
				print(sentiment)
			except:
				print("changing client from: ", c)
				c = (c + 1) % 4
				client = textapi.Client(ids[c], keys[c])
				try:
					sentiment = client.Sentiment({'text': row['Sentence']})
				except: 
					print("Error: Too many subjectivity requests from API.")
					i += 1
					continue

			# remove sentence if it is objective or neutral
			if(sentiment['subjectivity'] == 'objective'):
				print("Dropping row", row, i)
				reviews = reviews.drop([i])
	'''

	return reviews 

def run_sentiment_analyzer(encoding, restaurant_tag, userid):
	print(restaurant_tag)

	# set file paths 
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	if(userid == ''):
		reviews_file_path = script_dir + "/csvfiles/sentences/labeled/" + restaurant_tag + "-labeled.xlsx"
		results_file_path = script_dir + "/csvfiles/sentences/labeled-rated/" + restaurant_tag + "-labeled-rated.xlsx"
	else:
		reviews_file_path = script_dir + "/csvfiles/comments/" + userid + ".csv"
		results_file_path = script_dir + "/csvfiles/comments/" + userid + ".xlsx"

	# set encoding
	try:
		encoding = int(encoding)
		if encoding == 0:
			encoding = 'mac_roman'
		elif encoding == 1:
			encoding = 'utf-8'
		else:
			raise Exception()

		print('Loading reviews...')
		print(reviews_file_path)
		reviews = pd.read_excel(reviews_file_path, encoding=encoding)

		try:
			pattern = re.compile('\s+')
			reviews['Sentence'] = reviews['Sentence'].map(
				lambda text: re.sub(pattern, ' ', text)
			)
		except:
			reviews = remove_weird_sentences(reviews)
			pattern = re.compile('\s+')
			reviews['Sentence'] = reviews['Sentence'].map(
				lambda text: re.sub(pattern, ' ', text)
			)

		print('Reviews loaded.')
	except:
		traceback.print_exc()
		exit(1)
		print("There may be an invalid sentence in your -labeled file!")

	print('Loading model...')
	# load_pretrained_models()
	print('Model loaded.')

	print('Predicting sentiments...')
	reviews['Rating'] = predict(reviews['Sentence'])
	print('Predicting finished.')

	reviews = clean(reviews, 0)

	# save results
	if(userid == ''):
		reviews[['Item', 'Rating', 'Sentence', 'Keywords']].to_excel(results_file_path, index=False, header=True)
	else:
		reviews[['Source', 'SourceUserCode', 'SourceRestaurantCode', 'Month', 'Day', 'Year', 'Item', 'Sentence', 'Rating']].to_excel(results_file_path, index=False, header=True)
	print('Results saved to file {results_file_path}')		

if __name__ == '__main__':
	# argument parser
	parser = ap.ArgumentParser()
	parser.add_argument('-e', '--encoding', help='Encoding of the input file (0 - mac_roman, 1 - utf-8', default=0)
	parser.add_argument('-t', '--restaurant_tag', help='Restaurant tag', default='girl-and-the-goat-chicago')
	parser.add_argument('-u', '--userid', help='User ID', default='')
	
	args = vars(parser.parse_args())
	encoding = args['encoding']
	restaurant_tag = args['restaurant_tag']
	userid = args['userid']
	run_sentiment_analyzer(encoding, restaurant_tag, userid)
	
