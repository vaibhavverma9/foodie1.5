from bs4 import BeautifulSoup
import argparse as ap
import requests, os, pickle

# Pull PostMates HTML
def pull_postmates_html(postmates_code):
	url = "https://postmates.com/merchant/" + postmates_code
	r = requests.get(url)
	encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
	soup = BeautifulSoup(r.content, from_encoding=encoding) # BeautifulSoup produces HTML of webpage
	return soup

def pull_items(soup):
	output = []
	items = soup.find_all('h3', attrs={'class' : 'product-name css-1vuygjh e1tw3vxs3'})
	for item in items:
		category = item.parent.parent.parent.parent.parent.find('h2', attrs={'class' : 'css-sqkt8s e1u06svg0'}).get_text()
		
		# remove popular items because they're repeats 
		if "Popular Items" in category:
			continue

		name = item.get_text()
		description = item.parent.find('div', attrs={'class' : 'product-description css-1cwo7kl e1tw3vxs5'}).get_text()
		price = item.parent.parent.find('div', attrs={'class' : 'css-1ju2yr7 e1tw3vxs4'}).find('span').get_text()
		output.append([name, description, price, category, ""])
	return output

# Save menu_items as a file using pickle library (not necessarily human readable)
def write_menu(menu_items, postmates_code):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	print("Saving menu items at " + script_dir + "/output_menu_items/postmates/" + postmates_code + ".txt")
	with open(script_dir + "/output_menu_items/postmates/" + postmates_code + ".txt", 'wb') as f:
		pickle.dump(menu_items, f)

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-p', '--postmates_code', help='Postmates Restaurant Code', default='ej-sushi-chicago')

	args = vars(parser.parse_args())
	postmates_code = args['postmates_code']
	soup = pull_postmates_html(postmates_code)
	output = pull_items(soup)
	write_menu(output, postmates_code)