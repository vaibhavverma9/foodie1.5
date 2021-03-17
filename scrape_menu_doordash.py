from bs4 import BeautifulSoup
import argparse as ap
import requests, os, pickle, json


def pull_doordash_html(doordash_code):
    url = 'https://www.doordash.com/store/' + doordash_code
    r = requests.get(url)
    encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(r.content, "lxml") # BeautifulSoup produces HTML of webpage
    return(soup)

def pull_items(soup):
    output = []
    clean_soup = soup.find_all('script')[7].get_text().split("\"")[1]
    json_data = json.loads(clean_soup.replace("\\u0022","\"").replace("\\u002D", "-"))
    categorized_menu = json_data['current_menu']['menu_categories']
    for category in categorized_menu:
        section_name = category['title']
        for item in category['items']:
            item_name = item['name']
            description = item['description']
            price = str(int(item['price'])/100.0)
            #print(item_name, description, price)
            output.append([item_name, description, price.strip(), section_name, ""])
    return(output)

###NEED TO ADJUST FOR GOOGLE SEARCH INTEGRATION
def write_menu(menu_items, foodie_id):
    script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
    foodie_id = foodie_id.replace('/', '-')
    foodie_id = foodie_id.replace(',', '')
    print("Saving menu items at " + script_dir + "/output_menu_items/foodie/" + foodie_id + ".txt")
    with open(script_dir + "/output_menu_items/foodie/" + foodie_id + ".txt", 'wb') as f:
        pickle.dump(menu_items, f)

def scrape_doordash_menus(doordash_code, foodie_id):
    soup = pull_doordash_html(doordash_code)
    output = {}
    output['Food'] = pull_items(soup)
    write_menu(output, foodie_id)
    return True

def scrape_doordash_images(doordash_code, foodie_id):
    soup = pull_doordash_html(doordash_code)
    
if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-d', '--doordash_code', help='DoorDash Code', default='de-rice-asian-cuisine-chicago-7980')
    parser.add_argument('-f', '--foodie_id', help='Foodie Code', default="de-rice-asia-n-chicago")

    args = vars(parser.parse_args())
    doordash_code = args['doordash_code']
    foodie_id = args['foodie_id']
    scrape_doordash_menus(doordash_code, foodie_id)
