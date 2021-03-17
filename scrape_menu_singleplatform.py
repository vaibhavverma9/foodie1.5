from bs4 import BeautifulSoup
import argparse as ap
import requests, os, pickle, json

# Pull SinglePlatform HTML
def pull_singleplatform_html(singleplatform_code):
	url = "http://places.singleplatform.com/" + singleplatform_code + "/menu"
	r = requests.get(url)
	encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
	soup = BeautifulSoup(r.content, "lxml") # BeautifulSoup produces HTML of webpage
	return soup

def pull_items(soup):
	soup_json = json.loads(soup.find('script', attrs={'type' : 'application/ld+json'}).get_text())
	
	menu_dict = {}
	for menu_json in soup_json['hasOfferCatalog']['itemListElement']:
		menu = menu_json['name']
		for category_json in menu_json['itemListElement']:
			for item_json in category_json['itemListElement']:
				item = item_json['itemOffered']['name']
				menu_dict[item] = menu

	items = soup.find_all('h4', attrs={'class' : 'item-title'})
	output = []
	for item in items:		
		description = ""
		name = item.get_text().strip()

		details_parent = item.parent.parent
		category_parent = item.parent.parent.parent.parent

		if details_parent.find('div', attrs={'class' : 'description text'}) != None:
			description = details_parent.find('div', attrs={'class' : 'description text'}).get_text().strip()
		prices = details_parent.find_all('span', attrs={'class' : 'price'})
		category = category_parent.find('h3').get_text()

		menu = menu_dict[name]

		if prices == []:
			output.append([name, description, "", category, menu])

		for price in prices:
			output.append([name, description, price.get_text().strip(), category, menu])

	return output

# Save menu_items as a file using pickle library (not necessarily human readable)
def write_menu(menu_items, foodie_id):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	with open(script_dir + "/output_menu_items/foodie/" + foodie_id + ".txt", 'wb') as f:
		pickle.dump(menu_items, f)

def scrape_singleplatform_menus(singleplatform_code, foodie_id):
	try:
		soup = pull_singleplatform_html(singleplatform_code)
		output = {}
		output['Food'] = pull_items(soup)
		write_menu(output, foodie_id)
		return True
	except:
		return False

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-s', '--singleplatform_code', help='SinglePlatform Restaurant Code', default='girl--the-goat')

	args = vars(parser.parse_args())
	singleplatform_code = args['singleplatform_code']
	

