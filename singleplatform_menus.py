import base64, hashlib, hmac
from urllib.parse import urlencode
import requests, json

hostnames = {'matching' : 'http://matching-api.singleplatform.com', 'publishing' : 'http://publishing-api.singleplatform.com'} 
CLIENT_ID = 'cdkrtwn8sr1czoqhfwlg9rlzx'
apikey = 'kspac24g6tksdwta3952ik5gp'
CLIENT_SECRET = b'nm-znOxrr-Lb9DC5w3T1Dgi6K9iwsQzZG_kvOpyvcQk'

def generate_signature(path):
	 return base64.b64encode(hmac.new(CLIENT_SECRET, path.encode('utf-8'), hashlib.sha1).digest())
	
def normalize_path(path):
	# make sure the path ends and begins with a slash
	if not path.startswith('/'):
		path = '/' + path
	
	if not path.endswith('/'):
		path += '/'
	
	return path
		
def generate_url(path, api_type):
	# path = normalize_path(path)
	
	# TODO: add any other parameters, like 'width' and 'height'
	params  = dict()
	params['client'] = CLIENT_ID

	# form path before signing
	pathToSign = '{path}?{params}'.format(path=path, params=urlencode(params))

	# generate the signature for the preliminary path
	signature = generate_signature(pathToSign)
	
	# add signature to parameters
	params['signature'] = signature
	
	# form final URL
	path = '{base_url}{path}?{params}'.format(base_url=hostnames[api_type], path=path, params=urlencode(params))

	return path

def get_location_url(location_id):
	api_type ='publishing'
	return generate_url('/locations/{id}'.format(id=location_id), api_type)

def get_menu_url(location_id):
	api_type ='publishing'
	return generate_url('/locations/{id}/menus'.format(id=location_id), api_type)

def get_photos_url(location_id):
	api_type ='publishing'
	return generate_url('/locations/{id}/photos'.format(id=location_id), api_type)

def get_location_match_url():
	api_type ='matching'
	return generate_url('/location-match', api_type)

if __name__ == '__main__':
	URL = get_location_match_url()
	headers = {'Content-type': 'application/json'}
	data = {
	   "matching_criteria" : "NAME_ADDRESS",
	   "locations" : [
	      {
	         "name" : "High Five Ramen",
	         "address" : "112 N Green St Chicago, IL 60607"
	      }
	   ]
	}

	r = requests.post(URL, json=data,headers=headers)
	data = r.json()
	print(data)
	for restaurant in data['response']:
		spv2id = restaurant['spv2id']
		URL = get_menu_url(spv2id)
		print(URL)
			
