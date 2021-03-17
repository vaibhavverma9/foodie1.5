from bs4 import BeautifulSoup
import argparse as ap
import requests, os, pickle, json


def pull_ubereats_html(ubereats_code):
    url = "https://www.ubereats.com/en-US/" + ubereats_code
    r = requests.get(url)
    encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(r.content, "lxml") # BeautifulSoup produces HTML of webpage
    return(soup)

def pull_items(soup):
    json_data = json.loads(soup.find_all('script')[1].contents[0].split('\n')[2].strip().split('=',1)[1].strip()[:-1])
    storekey = list(json_data['eaterStores']['eaterStores'].keys())[0]
    store_data = json_data['eaterStores']['eaterStores'][storekey]['data']['store']
    menukeys = list(store_data['sectionEntitiesMap'].keys())
    itemsDict = {}
    for key in menukeys:
        itemsDict.update(store_data['sectionEntitiesMap'][key]['itemsMap'])
    output = []
    for key, section in store_data['subsectionsMap'].items():
        section_name = (section['title'])
        for itemID in section['itemUuids']:
            itemInfo = itemsDict[itemID]
            item_name = itemInfo['title']
            description = itemInfo['itemDescription']
            price = str(itemInfo['price']/100.0)
            output.append([item_name, description, price.strip(), section_name, ""])
    return(output)


###NEED TO ADJUST FOR GOOGLE SEARCH INTEGRATION
def write_menu(menu_items, foodie_id):
    foodie_id = foodie_id.replace('/', '-')
    script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
    print("Saving menu items at " + script_dir + "/output_menu_items/foodie/" + foodie_id + ".txt")
    with open(script_dir + "/output_menu_items/foodie/" + foodie_id + ".txt", 'wb') as f:
        pickle.dump(menu_items, f)

def scrape_ubereats_menus(ubereats_code, foodie_id):
    soup = pull_ubereats_html(ubereats_code)
    output = {}
    output['Food'] = pull_items(soup)
    write_menu(output, foodie_id)

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-u', '--ubereats_code', help='UberEats Code', default='chicago/food-delivery/hiro-sushi-bar/fHXSm9TLRS2bET6RCZmpaA')

    args = vars(parser.parse_args())
    ubereats_code = args['ubereats_code']
    scrape_ubereats_menus(ubereats_code, ubereats_code)
