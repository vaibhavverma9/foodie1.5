from bs4 import BeautifulSoup
from urllib.request import urlopen
from menu_from_db import extract_json, save_locally
import pandas as pd
import argparse as ap
import json, os
from analyze_sentiment import predict
from save_sentences_csv import contains_word

# account password: infatuation

# collecting review and date based on infatuation id and city 
def scrape_infatuation_reviews(infatuation_id):
    wiki = "https://www.theinfatuation.com/"+ infatuation_id
    page = urlopen(wiki)
    soup = BeautifulSoup(page, "lxml")
    text = json.loads(soup.find("script", attrs={"type" : "application/ld+json"}).get_text())
    return text['reviewBody'], text['datePublished'][:10]

# takes date in the format YYYY-MM-DD and return month, day and year
def date_breakdown(date):
    year = date[:4]
    month = date[5:7]
    day = date[8:10]
    return month, day, year

def match(sentence, item):
    i = 0.
    sentence_words = sentence.split()
    item_words = item.split()
    for sentence_word in sentence_words:
        if sentence_word in item_words:
            i += 1
    sentence_length = max(max(1, len(sentence_words)), len(item_words))
    percentage = i / sentence_length
    if(percentage >= 0.5):
        return True
    else:
        return False 

def best_match(matches, item, split_text):
    item_words = item.split()
    max_p = 0.
    best_word = matches[0]
    for match in matches:
        i = 0
        match_words = split_text[match].split()
        for match_word in match_words:
            if match_word in item_words:
                i += 1
        total_length = max(max(1, len(match_words)), len(item_words))
        percentage = i / total_length
        if percentage > max_p:
            best_word = split_text[match]
    print(best_word)
    return best_word

def get_yelp_id(json):
    if(json['Info'] != []):
        return json['Info'][0]['YelpID']
    else:
        return ''

# create an Excel output saved under csvfiles/comments
def create_output(review, date, foodie_id):
    output = []
    month, day, year = date_breakdown(date)

    # splits the text with \n
    split_text = review.split('\n')
    split_text = [elem.strip() for elem in split_text]
    
    # extracts json from database and save menu items locally on your machine
    json = extract_json(foodie_id)
    menu_items = save_locally(json, foodie_id)
    yelpid = get_yelp_id(json) # given json, we can extract yelp_id

    for item, description, price, category, menu, tag in menu_items['Food']: # iterating through each item for a restaurant
        matching = [split_text.index(s) for s in split_text if match(s, item)]

        if(matching != []): # checking if there is a match 
            # appending the paragraph that follows if there is an item
            best_word = best_match(matching, item, split_text)
            output.append(["Infatuation", "the-infatuation", yelpid, month, day, year, item, split_text[matching[0] + 1], '', category, menu, split_text[matching[0]]]) 

    # setting up DataFrame
    s = pd.DataFrame(output, index=None, columns=['Source', 'SourceUserCode', 'SourceRestaurantCode', 'Month', 'Day', 'Year', 'Item', 'Sentence', 'Rating', 'Categories', 'Menu', 'Item Match']) 

    # applying the sentiment analyzer
    # load_pretrained_models()
    s['Rating'] = predict(s['Sentence'])

    # dropping duplicates
    s = s.drop_duplicates(subset=['Sentence'], keep="first")

    s = convert_to_ten_scale(s)

    # saving Excel in csvfiles/comments
    script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
    s.to_excel(script_dir + "/csvfiles/sentences/comments/" + foodie_id + "-infatuation.xlsx", index=False)

    return len(s)

def convert_to_ten_scale(s):
    for i, row in s.iterrows():
        s.loc[i, 'Rating'] = row['Rating'] * 2 - 1
    return s

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-i', '--infatuation_id', help='Infatuation ID', default='chicago/reviews/girl-the-goat')
    parser.add_argument('-f', '--foodie_id', help='Foodie ID', default='girl--the-goat-chicago-807')

    args = vars(parser.parse_args())
    infatuation_id = args['infatuation_id']
    foodie_id = args['foodie_id']

    review, date = scrape_infatuation_reviews(infatuation_id) 
    create_output(review, date, foodie_id) 