# standard lib
import os
import sys
import string
import csv
import operator
import json

# data / numeric
import pandas as pd
import numpy as np

# algorithmic
import ahocorasick

# graphics
from yattag import Doc
import pdfkit

options = {
    'page-size': 'Letter',
    'margin-top': '.1in',
    'margin-right': '.1in',
    'margin-bottom': '.1in',
    'margin-left': '.1in',
    'encoding': "UTF-8",
    'no-outline': None,
    'dpi': '100'
}

def rating_sequence(rating):
    points = int(rating*10)
    buckets = [0,0,0,0,0]
    for i, _ in enumerate(buckets):
        if points < 10:
            buckets[i] = points
            return buckets
        else:
            buckets[i] = 10
            points -= 10
    return buckets

"""
Folds the data into a dictionary from values in the KEY column to a summary of
values from the val column
"""
def pandas_reduce(dataframe, key, val):
    # df = dataframe.groupby(by=key)[key, val]
    # return df.mean()
    collapsed_data = {}
    for i in dataframe.keys():
        row = dataframe[i]
        names = row[key].split(',')
        for name in names:
            name = name.strip()
            if name == '':
                continue
            ordinal = int(row[val])
            if name not in collapsed_data:
                collapsed_data[name] = []
            collapsed_data[name].append(ordinal)
    for entry in collapsed_data:
        collapsed_data[entry] = (np.mean(collapsed_data[entry]), len(collapsed_data[entry]))
    return collapsed_data

def get_collapsed_data(data, label, sortBy):
    collapsed_data = {}
    for row in data:
        names = row[label].split(',')
        for name in names:
            name = name.strip()
            if name == '':
                continue
            print(row)
            ordinal = int(row[sortBy])
            if name not in collapsed_data:
                collapsed_data[name] = []
            collapsed_data[name].append(ordinal)
    for entry in collapsed_data:
        collapsed_data[entry] = (np.mean(collapsed_data[entry]), len(collapsed_data[entry]))
    return collapsed_data

def display(item_info, rank=None):
    name, (rating, rating_count) = item_info
    if rank:
        return "{}. {}".format(rank, name)
    else:
        return "{}".format(name)

def buildHTML(restaurant_name, good_dish_data, bad_dish_data, good_descriptor_data, bad_descriptor_data, all_data, asset_path, style_path):
    doc,tag,text = Doc().tagtext()

    def nl():
        doc.asis('\n')

    def br():
        doc.asis('<br>')

    def display_review(sentence, sentiment, words):
        table = str.maketrans(dict.fromkeys(string.punctuation))
        keywords = list(map(lambda s: s.translate(table), words.split()))
        segmentations = []
        ptr = 0
        # if len(keywords) != 0:
        #     A = ahocorasick.Automaton()
        #     for i, w in enumerate(keywords):
        #         A.add_word(w, (i,w))
        #     A.make_automaton()
        #     for end_idx, (insert_order, original_value) in A.iter(sentence):
        #         segmentations.append((end_idx, original_value))
        doc.asis('\n')
        seq = rating_sequence(float(sentiment))
        with tag('p'):
            text('\"')
            for end, word in segmentations:
                start = end - len(word) + 1
                text(sentence[ptr:start])
                with tag('b'):
                    text(word)
                ptr = end + 1
            text(sentence[ptr:])
            text('\"')
        sentence_star_div(seq, sentiment, ratings=0, size=20, show_number=True, c='sentence_stars')

    def sentence_star_div(seq, rating, ratings=0, size=20, show_number=True, c=None):
        doc.asis('\n')
        with tag('div'):
            if c:
                doc.attr(klass = c)
            for s in seq:
                nl()
                doc.stag('img', src=os.path.join(asset_path, '{}.png'.format(s)), width=str(size), height=str(size))
            if show_number:
                doc.asis('\n')
                with tag('h8'):
                    doc.attr(klass="sentence_star_number")
                    text(" {}/5 ".format(int(rating)))
            if ratings != 0:
                doc.asis('\n')
                with tag('h3'):
                    doc.attr(klass="ratings_number")
                    text("{} rating{}".format(ratings, '' if ratings == 1 else 's'))

    def star_div(seq, rating, ratings=0, size=30, show_number=True, c=None):
        doc.asis('\n')
        with tag('div'):
            if c:
                doc.attr(klass = c)
            for s in seq:
                nl()
                doc.stag('img', src=os.path.join(asset_path, '{}.png'.format(s)), width=str(size), height=str(size))
            if show_number:
                doc.asis('\n')
                with tag('h3'):
                    doc.attr(klass="star_number")
                    text(" {:.1f} ".format(float(rating)))
            if ratings != 0:
                doc.asis('\n')
                with tag('h3'):
                    doc.attr(klass="ratings_number")
                    text("{} rating{}".format(ratings, '' if ratings == 1 else 's'))

    doc.asis("<!DOCTYPE html>")

    # Open the HTML
    doc.asis('\n')
    with tag('html'):

        # Add the stylesheet
        doc.asis('\n')
        with tag('head'):
            doc.asis("<link rel=\"stylesheet\" type=\"text/css\" href=\"{}\">".format(style_path))

        # Add the header banner.
        doc.asis('\n')
        with tag('header'):

            doc.asis('\n')
            with tag('div'):
                doc.attr(klass = "rectangle")
            doc.asis('<br><br>')

            doc.asis('\n')
            with tag('h5'):
                text(" Restaurant Analytics powered by Foodie ")

            doc.asis('\n')
            with tag('h1'):
                text(restaurant_name)

        # Begin the body
        doc.asis('\n')
        with tag('body'):

            # Add the highest rated dishes
            doc.asis("<br><br>")
            doc.asis('\n')
            with tag('h2'):
                text("Highest Rated Dishes:")
            i = 1
            for dish in good_dish_data:
                rating = dish[1][0]
                rating_count = dish[1][1]
                seq = rating_sequence(rating)
                doc.asis('\n')
                with tag('h3'):
                    text(display(dish, rank=i))
                star_div(seq, rating, rating_count, 30, c='stars')
                i += 1

            # Add the lowest rated dishes
            doc.asis('\n')
            doc.asis("<br>")
            doc.asis('\n')
            with tag('h2'):
                text("Lowest Rated Dishes:")
            for dish in bad_dish_data:
                rating = dish[1][0]
                rating_count = dish[1][1]
                seq = rating_sequence(rating)
                doc.asis('\n')
                with tag('h3'):
                    text(display(dish))
                star_div(seq, rating, rating_count, 30, c='stars')

            # Add the highest rated adjectives
            # nl()
            # br()
            # nl()
            # with tag('h2'):
            #     text("Highest Rated Descriptors:")
            # i = 1
            # for descriptor in good_descriptor_data:
            #     rating = descriptor[1][0]
            #     rating_count = descriptor[1][1]
            #     seq = rating_sequence(rating)
            #     nl()
            #     with tag('h3'):
            #         text(display(descriptor, rank=i))
            #     star_div(seq, rating, rating_count, 30, c='stars')
            #     i += 1

            # Add the lowest rated adjectives
            # nl()
            # br()
            # nl()
            # with tag('h2'):
            #     text("Lowest Rated Descriptors:")
            # for descriptor in bad_descriptor_data:
            #     rating = descriptor[1][0]
            #     rating_count = descriptor[1][1]
            #     seq = rating_sequence(rating)
            #     nl()
            #     with tag('h3'):
            #         text(display(descriptor))
            #     star_div(seq, rating, rating_count, 30, c='stars')

            nl()
            br()
            nl()
            with tag('h2'):
                text("Comments by Dish:")

            for dish in sorted(all_data.keys()):
                nl()
                with tag('h7'):
                    br()
                    nl()
                    text(dish)

                for rating, review, words in sorted(all_data[dish])[::-1]:
                    display_review(review, rating, words)

    return doc.getvalue()

def main(r_name, input_path, output_path, style_path, asset_path):
    if input_path.endswith('.csv'):
        print("Currently does not have support for csvs. Coming soon.")
    if input_path.endswith('.xlsx'):
        df = pd.read_excel(input_path, sheet_name=2).replace(np.nan, '', regex=True).T
        all_data = {}

        for i in df.keys():
            row = df[i]
            d = row['Item']
            if d not in all_data:
                all_data[d] = []
            all_data[d].append((row['Rating'], row['Sentence'], row['Keywords']))

        n = 3

        dish_data = pandas_reduce(df, key='Item', val='Rating')
        dish_sort = sorted(dish_data.items(), key=operator.itemgetter(1))
        good_dish_data = dish_sort[::-1][:n]
        bad_dish_data = dish_sort[:n][::-1]

        keyword_data = pandas_reduce(df, key='Keywords', val='Rating')
        keyword_sort = sorted(keyword_data.items(), key=operator.itemgetter(1))
        good_keyword_data = keyword_sort[::-1][:n]
        bad_keyword_data = keyword_sort[:n][::-1]

        html_string = buildHTML(r_name, good_dish_data, bad_dish_data, good_keyword_data, bad_keyword_data, all_data, asset_path, style_path)
        html_path = output_path + '.html'
        with open(html_path, 'w+') as htmlOut:
            htmlOut.write(html_string)
        print("Generated HTML file at: {}".format(html_path))
        pdfkit.from_string(html_string, output_path + '.pdf', options=options, css=style_path)

        buildJSON(r_name, good_dish_data, bad_dish_data, all_data, output_path)

def buildJSON(r_name, good_dish_data, bad_dish_data, all_data, output_path):
    output_path = output_path + ".json"
    data = {}
    data['Restaurant Name'] = r_name
    
    data['Highest Rated Dishes'] = []
    for dish in good_dish_data:
        data['Highest Rated Dishes'].append([dish[0], dish[1][0], dish[1][1]])

    data['Lowest Rated Dishes'] = []
    for dish in bad_dish_data:
        data['Lowest Rated Dishes'].append([dish[0], dish[1][0], dish[1][1]])

    data['Comments by Dish'] = all_data

    with open(output_path, 'w') as f:
        json.dump(data, f)

def run_generate_analytics_pdf(row, foodie_id):
    r_name = row['Name']
    script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
    input_path = script_dir + "/csvfiles/final/" + foodie_id + "-final.xlsx"
    output_path = script_dir + "/csvfiles/pdfs/" + foodie_id
    style_path = script_dir + "/scraping_scripts/visual/styles.css" 
    asset_path = script_dir + "/scraping_scripts/visual/assets/"
    main(r_name, input_path, output_path, style_path, asset_path)

if __name__ == "__main__":
    # try:
    asset_path = os.path.join(os.getcwd(), sys.argv[5])
    style_path = os.path.join(os.getcwd(), sys.argv[4])
    input_path = os.path.join(os.getcwd(), sys.argv[2])
    output_path = os.path.join(os.getcwd(), sys.argv[3])
    main(sys.argv[1], input_path, output_path, style_path, asset_path)
    # except IndexError:
    #     sys.stderr.write('Error. Usage: caller <restaurant_name> <input_path> <output_path> <style_path> <asset_path>\n')
