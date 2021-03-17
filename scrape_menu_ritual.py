from bs4 import BeautifulSoup
import argparse as ap
import requests, os, pickle, json, sys


def pull_ritual_html(ritual_code):
    url = "https://order.ritual.co/menu/" + ritual_code
    r = requests.get(url)
    encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(r.content, "lxml") # BeautifulSoup produces HTML of webpage
    return(soup)

def pull_items(soup):
    output = []
    for menu in soup.find_all('div', attrs={'class':'menu-group'}):
        section_name = menu.h4.contents[0]
        if(section_name == 'MOST POPULAR'):
            continue
        for item in menu.ul.find_all('li'):
            item = item.a
            item_name = item.div.find("h2").contents[0]
            price = item.div.find("span").span.next[1:] + item.div.find("span").sup.next
            try:
                description = item.p.contents[0]
            except:
                description = ""
            output.append([str(item_name), str(description), str(price.strip()), str(section_name), ""])
    return(output)

def write_menu(menu_items, foodie_id):
    foodie_id = foodie_id.replace('/', '-')
    script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
    print("Saving menu items at " + script_dir + "/output_menu_items/foodie/" + foodie_id + ".txt")
    with open(script_dir + "/output_menu_items/foodie/" + foodie_id + ".txt", 'wb') as f:
        pickle.dump(menu_items, f)

def scrape_menu_ritual(ritual_code, foodie_id):
    soup = pull_ritual_html(ritual_code)
    output = {}
    output['Food'] = pull_items(soup)
    write_menu(output, foodie_id)

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-r', '--ritual_code', help='Ritual Code', default='tokyo-lunch-box-catering-wells-calhoun-chicago/81dd')

    args = vars(parser.parse_args())
    ritual_code = args['ritual_code']
    scrape_menu_ritual(ritual_code, ritual_code)
