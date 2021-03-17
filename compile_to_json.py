import pandas as pd
import argparse as ap
import os, json, requests, shutil

url = "https://thefoodieapi.com/Api/ImportRestaurantJSON"
url_lite = "https://thefoodieapi.com/Apilite/ImportRestaurantJSON"
	
def compile_data(restaurant_tag, option):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	file_path = script_dir + "/csvfiles/final/" + restaurant_tag + "-final.xlsx"
	data = {}
	
	data['Info'] = {}
	df1 = pd.read_excel(file_path, 'Info')
	for index, row in df1.iterrows():
		data['Info']['Name'] = row['Name']
		data['Info']['YelpID'] = row['YelpID']
		data['Info']['Address'] = row['Address']
		data['Info']['City'] = row['City']
		data['Info']['State'] = row['State']
		data['Info']['Zipcode'] = row['Zipcode']
		data['Info']['DollarSign'] = row['DollarSign']
		data['Info']['Latitude'] = row['Latitude']
		data['Info']['Longitude'] = row['Longitude']
		data['Info']['Neighborhood'] = row['Neighborhood']
		data['Info']['Categories'] = row['Categories']
		data['Info']['FoursquareID'] = row['FoursquareID']

	data['Items'] = []
	df2 = pd.read_excel(file_path, 'Items')
	for index, row in df2.iterrows():
		item_dict = {}
		item_dict['Item'] = row['Item']
		item_dict['Description'] = row['Description']
		item_dict['Price'] = row['Price']
		item_dict['Categories'] = row['Categories']
		item_dict['Menu'] = row['Menu']
		data['Items'].append(item_dict)
	
	data['Ratings'] = []
	df3 = pd.read_excel(file_path, 'Ratings')
	for index, row in df3.iterrows():
		rating_dict = {}
		rating_dict['Item'] = row['Item']
		rating_dict['Rating'] = row['Rating']
		if(option == 1):
			rating_dict['Sentence'] = row['Sentence']
			rating_dict['keywords'] = row['Keywords']
		data['Ratings'].append(rating_dict)

	return data

def save_json(data, restaurant_tag):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	file_path = script_dir + "/csvfiles/final/" + restaurant_tag + "-json.txt"
	with open(file_path, 'w') as f:
		json.dump(data, f)

def move_file_to_archives(foodie_id):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	src_path = script_dir + "/csvfiles/final/" + foodie_id + "-final.xlsx"
	dst_path = script_dir + "/csvfiles/final/Archive/" + foodie_id + "-final.xlsx"
	shutil.move(src_path, dst_path)

def add_to_database(foodie_id):
	print("add_to_database")
	data = compile_data(foodie_id, 0)
	params = {'jsonContent' : json.dumps(data)}
	print(params)
	headers = {'Content-Type' : "application/x-www-form-urlencoded",
			'Authorization' : "o83tKj7ebbA3"}
	response = requests.post(url, data=params, headers=headers)
	print("Importing:", foodie_id)
	print(response.text)
	if(json.loads(response.text)['Message'] == 'Restaurant and menu items imported successfully!'):
		move_file_to_archives(foodie_id)
	
if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-t', '--restaurant_tag', help='Restaurant tag', default='girl-and-the-goat-chicago')
	parser.add_argument('-o', '--option', help='0: no sentences or keywords; 1: sentences and keywords', default='0')

	args = vars(parser.parse_args())
	restaurant_tag = args['restaurant_tag']
	option = int(args['option'])

	add_to_database(restaurant_tag)
