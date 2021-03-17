import json, os, pickle
import argparse as ap

def open_json(google_place_id, restaurant_name):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	file_path = script_dir + "/woflow-jsons/" + google_place_id + ' - ' + restaurant_name + ".json"
	with open(file_path) as json_file:
		data = json.load(json_file)
	return data

def check_subcategories(data):
	for category_id in data['data']['categories']:
		print(category_id)
		print(data['data']['categories'])
		category_data = data['data']["categories"][category_id]
		print(category_data)
		if(category_data['sub_categories'] != []):
			return True

def convert_json_to_xlsx(data):
	subcategories_exist = check_subcategories(data)
	menu_items = {}
	menu_items['Food'] = []
	subcategory_ids = []
	print(data)
	for category_id in data['data']["categories"]:
		if category_id in subcategory_ids:
			continue
		category_data = data['data']["categories"][category_id]
		category_name = category_data["name"]

		if(category_data['sub_categories'] != []):
			for subcategory_id in category_data['sub_categories']:
				subcategory_ids.append(subcategory_id)
				subcategory_data = data['data']["categories"][subcategory_id]
				subcategory_name = subcategory_data["name"]

				for item_id in subcategory_data['items']:
					item_data = data['data']["items"][item_id]
					name = item_data['title']
					description = item_data['description']

					# prices array contains at least the base price
					prices = []
					base_price = item_data['price']
					prices.append(base_price)

					for modifier_id in item_data["modifiers"]:
						modifier = data['data']["modifiers"][modifier_id]
						if(modifier['name'] == "Size Choice"):
							for option_id in modifier["options"]:
								option = data["options"][option_id]
								price = base_price + option['price']
								prices.append(price)
					prices = set(prices)
					if(len(prices) == 0):
						prices = [0.0]

					tags = []
					for tag_id in item_data['tags']:
						tags.append(data['data']["tags"][tag_id]['name'])
					if(len(tags) == 0):
						tags = ['']

					for tag in tags:				
						for price in prices:
							menu_items['Food'].append([name, description, price, subcategory_name, category_name, tag])



		for item_id in category_data['items']:
			item_data = data['data']["items"][item_id]
			name = item_data['title']
			description = item_data['description']

			# prices array contains at least the base price
			prices = []
			base_price = item_data['price']
			prices.append(base_price)

			for modifier_id in item_data["modifiers"]:
				modifier = data['data']["modifiers"][modifier_id]
				if(modifier['name'] == "Size Choice"):
					for option_id in modifier["options"]:
						option = data['data']["options"][option_id]
						price = base_price + option['price']
						prices.append(price)
			prices = set(prices)
			if(len(prices) == 0):
				prices = [0.0]

			tags = []
			for tag_id in item_data['tags']:
				tags.append(data['data']["tags"][tag_id]['name'])
			if(len(tags) == 0):
				tags = ['']

			for tag in tags:				
				for price in prices:
					menu_items['Food'].append([name, description, price, category_name, "", tag])

	return menu_items

# Save menu_items as a file using pickle library (not necessarily human readable)
def write_menu(menu_items, restaurant_tag):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	with open(script_dir + "/output_menu_items/foodie/" + restaurant_tag + ".txt", 'wb') as f:
		pickle.dump(menu_items, f)

def run_woflow_conversion(foodie_id, google_place_id, restaurant_name):
	data = open_json(google_place_id, restaurant_name)
	menu_items = convert_json_to_xlsx(data)
	write_menu(menu_items, foodie_id)

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-f', '--foodie_id', help='Foodie ID', default="big-bear-cafe-134")
	parser.add_argument('-n', '--restaurant_name', help='Restaurant Name', default='Big Bear Cafe')
	parser.add_argument('-g', '--google_place_id', help='Google Place ID', default='ChIJWbmml_e3t4kRDzgyQ5HJP_c')
	args = vars(parser.parse_args())
	foodie_id = args['foodie_id']
	restaurant_name = args['restaurant_name']
	google_place_id = args['google_place_id']
	run_woflow_conversion(foodie_id, google_place_id, restaurant_name)
