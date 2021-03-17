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

def foursquare_tips(venue_id):
	output = []
	json = client.venues(venue_id)#, 'sort' : 'recent', 'limit' : '100'})
	print(json)


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
		foursquare_id = vens['venues'][0]['id']
		foursquare_tips(foursquare_id)
	else:
		print('Error: venue not found')