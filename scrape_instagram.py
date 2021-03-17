from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from scrape_menu_items import read_menu
import json, time, random, os
from save_sentences_csv import items_in_sentence, optimize_list, read_items
from urllib.request import urlretrieve
import pandas as pd
from menu_from_db import extract_json, save_locally
from compile_to_json import compile_data
import pickle

def analyze_shared_data(sharedData):
    keyword = "window._sharedData = "
    output = []
    if(sharedData[:len(keyword)] == keyword):
        data = json.loads(sharedData[len(keyword):len(sharedData) - 1])
        data = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
        for node in data:
            # find display url
            display_url = node['node']['display_url']

            # find caption
            if node['node']['edge_media_to_caption']['edges'] != []:
                text = node['node']['edge_media_to_caption']['edges'][0]['node']['text']
            else:
                text = ""

            # find location
            if node['node']['location']:
                location = node['node']['location']
            else:
                location = ""
            output.append([text, location, display_url])
    return output

def init_info():
    output = {}
    output['Username'] = []
    output['Name'] = []
    output['URL'] = []
    output['Email'] = []
    output['Number'] = []
    output['Count'] = []
    return output

def append_info(username, name, url, email, number, count, output):
    output['Username'].append(username)
    output['Name'].append(name)
    output['URL'].append(url)
    output['Email'].append(email)
    output['Number'].append(number)
    output['Count'].append(count)
    return output

def pull_content(username):
    #Opening proper webpage
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    wiki = "https://www.instagram.com/" + username
    driver.get(wiki)

    CLICK_PAUSE_TIME = .5
    output = []
    #NOTE: We do not get location yet
    location = ""

    time.sleep(CLICK_PAUSE_TIME*5)
    driver.execute_script("window.scrollTo(0, 500)") 
    time.sleep(CLICK_PAUSE_TIME*5)

    #Click the first picture to open the pop-up
    first_pic = driver.find_element_by_xpath("//div[@class='Nnq7C weEfm']/*")
    first_pic.click()
    time.sleep(CLICK_PAUSE_TIME*5)

    #Cycle through all of the posts
    i = 0
    max_i = 100
    while i>=0 and i < max_i:
        print(i)
        #Get data

        imgs = driver.find_elements_by_xpath("//img[@class='FFVAD']")
        img = imgs[len(imgs) - 1]
        display_url = img.get_attribute("src")

        try:
            caption_frame = driver.find_element_by_xpath("//div[@class='C4VMK']/span")
            caption = caption_frame.text
            output.append([caption, location, display_url])
        except:
            # no captions
            pass

        #Click the next
        try:
            next_button = driver.find_element_by_xpath("//a[@class='HBoOv coreSpriteRightPaginationArrow']")
            next_button.click()
            #wait for next pic to load
            time.sleep(CLICK_PAUSE_TIME * 2)
            i += 1
        except:
            i = -1

    driver.close()
    return output

def pull_usernames_from_tagged_posts(instagram_id, n):
    #Opening proper webpage
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    if 'explore/' in instagram_id:
        wiki = "https://www.instagram.com/" + instagram_id
    else:
        wiki = "https://www.instagram.com/" + instagram_id + "/tagged/"
    print(wiki)
    driver.get(wiki)

    CLICK_PAUSE_TIME = .5
    output = []
    #NOTE: We do not get location yet
    location = ""


    # Nnq7C weEfm
    # Nnq7C weEfm

    time.sleep(CLICK_PAUSE_TIME*5)

    driver.execute_script("window.scrollTo(0, 500)") 

    time.sleep(CLICK_PAUSE_TIME*5)

    forms = driver.find_elements_by_xpath("//input[@class='_2hvTZ pexuQ zyHYP']")
    if(len(forms) > 0):
        username_form = forms[0]
        username = 'usesimmer'
        username_form.send_keys(username)
        username_form.send_keys(Keys.RETURN)

        password_form = forms[1]
        password = 'newfoodie2019'
        password_form.send_keys(password)
        password_form.send_keys(Keys.RETURN)

        time.sleep(CLICK_PAUSE_TIME*10)


    #Click the first picture to open the pop-up
    # Nnq7C weEfm
    # v1Nh3 kIKUG  _bz0w
    first_pic = driver.find_element_by_xpath("//div[@class='v1Nh3 kIKUG  _bz0w']/*")
    first_pic.click()
    time.sleep(CLICK_PAUSE_TIME*5)

    #Cycle through all of the posts
    i = 0
    max_i = n
    while i>=0 and i < max_i:
        #Get data
        try:
            verified = driver.find_elements_by_xpath("//span[@class='mewfM Szr5J  coreSpriteVerifiedBadgeSmall']")
            print(verified)
            if(verified == []):
                title_frame = driver.find_element_by_xpath("//a[@class='FPmhX notranslate nJAzx']")
                instagram_id = "@" + title_frame.text
                output.append(instagram_id)
                print(output)
        except:
            pass
        #Click the next
        try:
            next_button = driver.find_element_by_xpath("//a[@class='HBoOv coreSpriteRightPaginationArrow']")
            next_button.click()
            #wait for next pic to load
            time.sleep(CLICK_PAUSE_TIME * 2)
            i += 1
        except:
            i = -1

    # driver.close()
    return output

def pull_users(hashtag, n):
    #Opening proper webpage
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(options=chrome_options)
    wiki = "https://www.instagram.com/explore/tags/" + hashtag
    driver.get(wiki)

    CLICK_PAUSE_TIME = .5
    output = []
    #NOTE: We do not get location yet
    location = ""

    #Click the first picture to open the pop-up
    first_pic = driver.find_element_by_xpath("//div[@class='Nnq7C weEfm']/*")
    first_pic.click()
    time.sleep(CLICK_PAUSE_TIME*5)

    #Cycle through all of the posts
    i = 0
    max_i = 100
    while i>=0 and i < max_i:
        #Get data
        try:
            title_frame = driver.find_element_by_xpath("//a[@class='FPmhX notranslate nJAzx']")
            instagram_id = title_frame.text
            output.append(instagram_id)
        except:
            pass
        #Click the next
        try:
            next_button = driver.find_element_by_xpath("//a[@class='HBoOv coreSpriteRightPaginationArrow']")
            next_button.click()
            #wait for next pic to load
            time.sleep(CLICK_PAUSE_TIME * 2)
            i += 1
        except:
            i = -1

    driver.close()
    return output

def pull_contact_info(username):
    wiki = "https://www.instagram.com/" + username
    page = urlopen(wiki)
    soup = BeautifulSoup(page, "lxml") # BeautifulSoup produces HTML of webpage
    print(soup.find("script", attrs={"type" : "application/ld+json"}))
    info = soup.find("script", attrs={"type" : "application/ld+json"})

    if info == None:
        return ['', '', '', '', '']
    else:
        info = json.loads(info.get_text())

    name = info['name']
    try:
        url = info['url']
    except:
        url = ""
    try:
        email = info['email']
    except:
        email = ""
    try:
        number = info['telephone']
    except:
        number = ""

    meta_description = soup.find('meta', attrs={'property' : 'og:description'}).get('content').replace(',', '')
    followers =  meta_description[:meta_description.index(' Followers')]
    print(name, url, email, number, followers)
    return [name, url, email, number, followers]

def analyze_images(images_data, foodie_id, instagram_id):
    exceptions = ['a', 'an', 'of', 'the', 'is', 'with', 'or', 'and', 'to', 'from'] + foodie_id.split('-')

    script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))

    # menu_items = read_items(script_dir, foodie_id)
    json = extract_json(foodie_id)
    menu_items = save_locally(json, foodie_id)

    path = script_dir + "/csvfiles/images/" + foodie_id[:100] + instagram_id.replace('/', '-') + "-images-ig/"
    try: os.makedirs(path)
    except OSError: pass  

    # initializing
    foodie_ids = []
    items = []
    filenames = []
    captions = []
    source_ids = []

    n = 100    

    for image_data in images_data:
        caption = image_data[0]
        link = image_data[2]

        # remove sentence if it does not contain a menu item
        items_in_given_sentence = items_in_sentence(caption, menu_items, 2, foodie_id, exceptions)
        print(items_in_given_sentence)
        if(len(items_in_given_sentence) == 0):
            continue

        # choose best item out of all matched items
        optimized_items = optimize_list(items_in_given_sentence, caption.lower())
        for item in optimized_items:
                          

            try:
                filename = foodie_id + "-" + str(n) + ".jpg"
                urlretrieve(link, path + filename)

                foodie_ids.append(foodie_id)
                items.append(item)
                filenames.append(filename)
                captions.append(caption)
                source_ids.append(instagram_id)
                n += 1
                print(n)
            except:
                continue

    d = {'FoodieID' : foodie_ids, 'Item' : items, 'Filename' : filenames, 'Captions' : captions, 'InstagramID' : source_ids}
    df = pd.DataFrame(d)
    df.to_excel(path + foodie_id[:100] + instagram_id.replace('/','-') + ".xlsx", sheet_name='Sheet1', encoding="utf8", index=False)
    
    return n - 100

def save_info(hashtag, output):
    script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
    file_path = script_dir + "/csvfiles/ig_info/info-" + hashtag + ".xlsx"
    d = {'Username' : output['Username'], 'Name' : output['Name'], 'URL' : output['URL'], 'Email' : output['Email'], 'Number' : output['Number'], 'Count' : output['Count']}
    df = pd.DataFrame(d)
    df.to_excel(file_path, sheet_name='Sheet1', encoding='utf', index=False)

def verify_ig_id(instagramid):
    if('explore' not in instagramid and '/' in instagramid):
        instagramid = instagramid[:instagramid.index('/')]
    return instagramid

def run_ig_img_scraper(instagramid, foodieid): 
    instagramid = verify_ig_id(instagramid)
    output = pull_content(instagramid)
    n = analyze_images(output, foodieid, instagramid)
    
    return instagramid, n

def run_ig_info_scraper(hashtag, n):
    output = init_info()
    usernames = pull_users(hashtag, n)
    for username in usernames:
        try:
            name, url, email, number, count = pull_contact_info(username)
            output = append_info(username, name, url, email, number, count, output)
        except:
            continue
    save_info(hashtag, output)

def read_usernames():
    script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
    with open(script_dir + "/output_user/users_dmed.txt", 'rb') as f:
        users_dmed = pickle.load(f)
    return users_dmed

def save_usernames_master(users_dmed):
    script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
    with open(script_dir + "/output_user/users_dmed.txt", 'wb') as f:
        pickle.dump(users_dmed, f, protocol=pickle.HIGHEST_PROTOCOL)

def save_usernames_to_dm(f_usernames, restaurant, city):
    script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
    path = script_dir + "/csvfiles/automated_dms/" + restaurant + "-" + city + ".xlsx"
    
    restaurants = []
    cities = []
    usernames = []
    counts = []
    bios = []
    for i in range(len(f_usernames)):
        usernames.append(f_usernames[i][0])
        counts.append(f_usernames[i][1])
        bios.append(f_usernames[i][2])
        restaurants.append(restaurant)
        cities.append(city)

    d = {'Username' : usernames, 'Counts' : counts, 'Bios' : bios, 'Restaurant' : restaurants, 'City' : cities}
    df = pd.DataFrame(d)
    df.to_excel(path, sheet_name='Sheet1', encoding='utf', index=False)


def isUsernameInDictionary(username, dictionary):
    temp_dictionary = dictionary
    characters = list(username)
    for c in characters:
        if c not in temp_dictionary:
            temp_dictionary[c] = {}
        temp_dictionary = temp_dictionary[c]
    if '' in temp_dictionary:
        return True, dictionary
    else:
        temp_dictionary[''] = username
        return False, dictionary

def usernames_for_automated_dms(instagram_id, n, restaurant, city):    
    details = False
    users_dmed = read_usernames()

    usernames = pull_usernames_from_tagged_posts(instagram_id, n)
    f_usernames = []
    for username in usernames:
        # username = username
        alreadySent, users_dmed = isUsernameInDictionary(username, users_dmed)
        if not alreadySent:
            if(details):
                try:
                    count, bio = username_info(username[1:])
                except:
                    count, bio = '', ''
            else:
                count, bio = '', ''
            f_usernames.append([username, count, bio])

    save_usernames_to_dm(f_usernames, restaurant, city)

# returns bio and follower count
def username_info(username):
    #Opening proper webpage
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    wiki = "https://www.instagram.com/" + username
    print(wiki)
    driver.get(wiki)

    count = -1
    bio = ''

    stats = driver.find_elements_by_xpath("//a[@class='-nal3 ']")
    for stat in stats:
        if('follower' in stat.text):
            count = stat.find_element_by_xpath(".//span[@class='g47SY ']").text

    profile_box = driver.find_element_by_xpath("//div[@class='-vDIg']")
    bio = profile_box.find_element_by_xpath(".//span").text

    return count, bio


if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-u', '--username', help='username', default='girl.and.the.goat')
    parser.add_argument('-f', '--foodie_id', help="FoodieID", default='girl--the-goat-chicago-807')
    parser.add_argument('-t', '--hashtag', help="hashtag", default='ramensan')
    parser.add_argument('-n', '--n', help="posts", default='100')
    # parser.add_argument('-l', '--location_id', help="location", default='55177')
    parser.add_argument('-c', '--city', help='city', default='Chicago')
    parser.add_argument('-r', '--restaurant', help='restaurant', default="Girl and the Goat")
    parser.add_argument('-d', '--details', help='restaurant', default="True")

    args = vars(parser.parse_args())
    instagram_id = args['username']
    foodie_id = args['foodie_id']
    hashtag = args['hashtag']
    n = int(args['n'])
    # location_id = args['location_id']
    city = args['city']
    restaurant = args['restaurant']   
    details = args['details']
    if(details == "True"):
        details = True 
    else: 
        details = False

    usernames_for_automated_dms(instagram_id, n, restaurant, city)
