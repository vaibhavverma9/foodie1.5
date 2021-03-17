import foursquare as fs 
import argparse as ap
import os, pickle

client_id = "YOCRGH1UXTDRI0OGZYX0XRKPAJXGVVBNBFCX0CGXYRBDFJVB"
client_secret = "V2PT4LKDAZIUI10SF34TL5DUINUMTOGHKHBL0I4X1CCMWZLI"
redirect_id = "thefoodieapp.com"

client = fs.Foursquare(client_id=client_id, client_secret=client_secret, 
                       redirect_uri=redirect_id)

def foursquare_vens(name, address, city, state, zipcode):
	city_state = city + ", " + state
	vens = client.venues.search({'near' : city_state, 'intent' : 'match', 'name' : name, 'address' : address, 'city' : city, 'state' : state, 'zipcode' : zipcode})
	return vens

def foursquare_menus(venu_id):
	output = []
	menus_json = client.venues.menu(venu_id)
	if 'items' in menus_json['menu']['menus']:
		for menu_json in menus_json['menu']['menus']['items']:
			menu = menu_json['name']
			for category_json in menu_json['entries']['items']:
				category = category_json['name']
				for item_json in category_json['entries']['items']:
					item = item_json['name']
					description = ''
					price = ''
					if 'description' in item_json:
						description = item_json['description']
					if 'price' in item_json:
						price = item_json['price']
					output.append([item, description, price, category, menu])
	else:
		print('No menu', menus_json)
	return output

# Save menu_items as a file using pickle library
def write_menu(menu_items, foursquare_code):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	print("Saving menu items at " + script_dir + "/output_menu_items/foursquare/" + foursquare_code + ".txt")
	with open(script_dir + "/output_menu_items/foursquare/" + foursquare_code + ".txt", 'wb') as f:
		pickle.dump(menu_items, f)

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-n', '--name', help='Name', default='Mott St')
	parser.add_argument('-a', '--address', help='Address', default='1401 N Ashland Ave')
	parser.add_argument('-c', '--city', help='City', default='Chicago')
	parser.add_argument('-s', '--state', help='State', default='IL')
	parser.add_argument('-z', '--zipcode', help='Zipcode', default='60622')

	args = vars(parser.parse_args())
	name = args['name']
	address = args['address']
	city = args['city']
	state = args['state']
	zipcode = args['zipcode']

	vens = foursquare_vens(name, address, city, state, zipcode)
	if 'venues' in vens:
		foursquare_code = vens['venues'][0]['id']
		output = foursquare_menus(foursquare_code)
		write_menu(output, foursquare_code)
	else:
		print('Error: venue not found')
