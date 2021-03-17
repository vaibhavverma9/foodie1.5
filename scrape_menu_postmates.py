from bs4 import BeautifulSoup
import argparse as ap
import requests, os, pickle, json


def pull_postmates_html(postmates_code):
    url = "https://postmates.com/merchant/" + postmates_code
    r = requests.get(url)
    encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(r.content, "lxml") # BeautifulSoup produces HTML of webpage
    return(soup)

def pull_items(soup):
    menu_json = json.loads(soup.find_all('script', attrs={'type' : 'application/ld+json'})[3].get_text())['hasMenuSection']
    output = []
    for section in menu_json:
        section_name = section['name']
        for item in section['hasMenuItem']:
            item_name = item['name']
            try:
                description = item['description']
            except:
                description = ""
            price = item['offers']['price']
            output.append([item_name, description, price.strip(), section_name, ""])
    return(output)

def write_menu(menu_items, postmates_code):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	print("Saving menu items at " + script_dir + "/output_menu_items/postmates/" + postmates_code + ".txt")
	with open(script_dir + "/output_menu_items/postmates/" + postmates_code + ".txt", 'wb') as f:
		pickle.dump(menu_items, f)

def scrape_postmates_menus(postmates_code, foodie_id):
    soup = pull_postmates_html(postmates_code)
    output = {}
    output['Food'] = pull_items(soup)
    write_menu(output, foodie_id)

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-s', '--postmates_code', help='Postmates Restaurant Code', default='chicago-raw-chicago')

    args = vars(parser.parse_args())
    postmates_code = args['postmates_code']
    scrape_postmates_menus(postmates_code, foodie_id)
