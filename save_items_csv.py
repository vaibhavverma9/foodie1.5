import os, csv, pickle
import pandas as pd 
import argparse as ap
import time 

# Reads menu_items from file 
def read_items(script_dir, foodie_id):
	foodie_id = foodie_id.replace('/', '-')
	foodie_id = foodie_id.replace(',', '')
	with open(script_dir + "/output_menu_items/foodie/" + foodie_id + ".txt", 'rb') as f:
		items = pickle.load(f)
	return items

def run_save_items_csv(foodie_id):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	items = read_items(script_dir, foodie_id)
	food_items = []

	for key in items:
		for item in items[key]:
			food_items.append(item)

	print("run_save_items_csv:")
	print(food_items)
	print(food_items)
	s = pd.DataFrame(food_items, index=None, columns=['Item', 'Description', 'Price', 'Categories', 'Menu']) 
	s.to_excel(script_dir + "/csvfiles/items/" + foodie_id + "-items.xlsx", sheet_name='Sheet1', encoding="utf8", index=False)

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-f', '--foodie_id', help='Foodie ID', default='girl--the-goat-807')

	args = vars(parser.parse_args())
	foodie_id = args['foodie_id']
	run_save_items_csv(foodie_id)