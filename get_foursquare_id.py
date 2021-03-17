import foursquare as fs 
import argparse as ap
from scrape_info import address_match

# client_id = "YOCRGH1UXTDRI0OGZYX0XRKPAJXGVVBNBFCX0CGXYRBDFJVB"
# client_secret = "V2PT4LKDAZIUI10SF34TL5DUINUMTOGHKHBL0I4X1CCMWZLI"
# client_id = "JKGW5VKQYONKP5MZBDFEZJQEWBRHAB0IJJCOXRJQUQBIURTP"
# client_secret = "F2DJ0145I0LT2RSUO0U4Y1SMEIWRTLYOZTMMRJSEB310TPHF"
client_id = "1PNJHPGAS5SGRSYJR14QUJT2TISUEHM2ZV3GWPFIQZSIBVNN"
client_secret = "FDSA5BIEV5ZNPSW3NYPGW0DZKO5HR0ABWCXVQT1YNPKB2UCG"
redirect_id = "thefoodieapp.com"

client = fs.Foursquare(client_id=client_id, client_secret=client_secret, 
                       redirect_uri=redirect_id)

def get_id(name, address, city, state, zipcode):
	city_state = city + ", " + state
	vens = client.venues.search({'near' : city_state, 'intent' : 'match', 'name' : name, 'address' : address, 'city' : city, 'state' : state, 'zipcode' : zipcode})
	if 'venues' in vens and vens['venues'] != []:
		for restaurant in vens['venues']:
			if(address_match(address, restaurant['location']['address'])):
				print(restaurant['id'])
				return restaurant['id']
	return ''

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-n', '--name', help='Restaurant Name', default='Girl & the Goat')
	parser.add_argument('-a', '--address', help='Address', default='809 W Randolph St')
	parser.add_argument('-c', '--city', help='City', default='Chicago')
	parser.add_argument('-s', '--state', help='State', default='IL')
	parser.add_argument('-z', '--zipcode', help='Zipcode', default='60607')

	args = vars(parser.parse_args())
	name = args['name']
	address = args['address']
	city = args['city']
	state = args['state']
	zipcode = args['zipcode']

	get_id(name, address, city, state, zipcode)