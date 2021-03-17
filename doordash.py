import argparse as ap
import requests, os, json, pickle
import csv
from requests.auth import AuthBase
import json
import sys
import pandas as pd
from menu_from_db import extract_json, save_locally
from save_sentences_csv import items_in_sentence, optimize_list, read_items
import ast, cv2
from urllib.request import urlretrieve

def scrape_menu(storeId):
	name = "doordash_menu"
	url = "https://api-consumer-client.doordash.com/graphql"

	headers = {
	     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
	     'Content-Type': 'application/json',
	     'Credentials': 'include'
	}
	body = {
	    "operationName": "menu",
	    "variables": {
	        # "storeId": "360",
	        # "storeId": "2693"
	        "storeId": storeId
	        # "menuId": "223199"
	    },
	    "query":'''
	          query menu($storeId: ID!, $menuId: ID) {
	            storeInformation(storeId: $storeId) {
	              id
	              name
	              description
	              isGoodForGroupOrders
	              offersPickup
	              offersDelivery
	              deliveryFee
	              sosDeliveryFee
	              numRatings
	              averageRating
	              shouldShowStoreLogo
	              isConsumerSubscriptionEligible
	              headerImgUrl
	              coverImgUrl
	              distanceFromConsumer
	              providesExternalCourierTracking
	              fulfillsOwnDeliveries
	              isDeliverableToConsumerAddress
	              priceRange
	              business {
	                id
	                name
	                __typename
	              }
	              address {
	                street
	                printableAddress
	                lat
	                lng
	                city
	                state
	                __typename
	              }
	              status {
	                asapAvailable
	                scheduledAvailable
	                asapMinutesRange
	                asapPickupMinutesRange
	                __typename
	              }
	              merchantPromotions {
	                id
	                minimumOrderCartSubtotal
	                newStoreCustomersOnly
	                deliveryFee
	                __typename
	              }
	              storeDisclaimers {
	                id
	                disclaimerDetailsLink
	                disclaimerLinkSubstring
	                disclaimerText
	                displayTreatment
	                __typename
	              }
	              __typename
	            }
	            storeMenus(storeId: $storeId, menuId: $menuId) {
	              allMenus {
	                id
	                name
	                subtitle
	                isBusinessEnabled
	                timesOpen
	                __typename
	              }
	              currentMenu {
	                id
	                timesOpen
	                hoursToOrderInAdvance
	                isCatering
	                minOrderSize
	                menuCategories {
	                  ...StoreMenuCategoryFragment
	                  items {
	                    ...StoreMenuListItemFragment
	                    __typename
	                  }
	                  __typename
	                }
	                __typename
	              }
	              __typename
	            }
	            storeCrossLinks(storeId: $storeId) {
	              trendingStores {
	                ...StoreCrossLinkItemFragment
	                __typename
	              }
	              trendingCategories {
	                ...StoreCrossLinkItemFragment
	                __typename
	              }
	              topCuisinesNearMe {
	                ...StoreCrossLinkItemFragment
	                __typename
	              }
	              nearbyCities {
	                ...StoreCrossLinkItemFragment
	                __typename
	              }
	              __typename
	            }
	          }

	        fragment StoreMenuCategoryFragment on StoreMenuCategory {
	          id
	          subtitle
	          title
	          __typename
	        }

	        fragment StoreMenuListItemFragment on StoreMenuListItem {
	          id
	          description
	          isTempDeactivated
	          price
	          imageUrl
	          name
	          __typename
	        }

	        fragment StoreCrossLinkItemFragment on StoreCrossLinkItem {
	          name
	          url
	          __typename
	        }

	    '''
	}
	response = requests.post(url, cookies={'X-CSRFToken': 'MKp9Os0ao3HiPO9ybnSFdDy7HrrodcxiFOWVhuhjaHEybo28kCAfBwMOWp6b78BU'}, data = json.dumps(body), headers = headers)
	print("Response", response)
	print("Response JSON", response.json())
	allMenus = response.json()['data']['storeMenus']['allMenus']

	menu_items = {}
	# items = [['Item', 'Price', 'Description', 'Categories', 'Menu']]
	for menu in allMenus:
		menu_name = menu['subtitle']
		menu_items[menu_name] = []

	# self.body['variables']['menuId'] = menu['id']
		# print(menu['id'])
		body['variables']['menuId'] = menu['id']
		response = requests.post(url, cookies={'X-CSRFToken': 'MKp9Os0ao3HiPO9ybnSFdDy7HrrodcxiFOWVhuhjaHEybo28kCAfBwMOWp6b78BU'}, data = json.dumps(body), headers = headers)
		for category in response.json()['data']['storeMenus']['currentMenu']['menuCategories']:
			for item in category['items']:
				menu_items[menu_name].append([item['name'], item['description'], float(item['price']) / 100, category['title'], menu['subtitle'], ''])

	return menu_items


def scrape_images(storeId, foodie_id):
	name = "doordash_menu"
	url = "https://api-consumer-client.doordash.com/graphql"

	headers = {
	     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
	     'Content-Type': 'application/json',
	     'Credentials': 'include'
	}
	body = {
	    "operationName": "menu",
	    "variables": {
	        # "storeId": "360",
	        # "storeId": "2693"
	        "storeId": storeId
	        # "menuId": "223199"
	    },
	    "query":'''
	          query menu($storeId: ID!, $menuId: ID) {
	            storeInformation(storeId: $storeId) {
	              id
	              name
	              description
	              isGoodForGroupOrders
	              offersPickup
	              offersDelivery
	              deliveryFee
	              sosDeliveryFee
	              numRatings
	              averageRating
	              shouldShowStoreLogo
	              isConsumerSubscriptionEligible
	              headerImgUrl
	              coverImgUrl
	              distanceFromConsumer
	              providesExternalCourierTracking
	              fulfillsOwnDeliveries
	              isDeliverableToConsumerAddress
	              priceRange
	              business {
	                id
	                name
	                __typename
	              }
	              address {
	                street
	                printableAddress
	                lat
	                lng
	                city
	                state
	                __typename
	              }
	              status {
	                asapAvailable
	                scheduledAvailable
	                asapMinutesRange
	                asapPickupMinutesRange
	                __typename
	              }
	              merchantPromotions {
	                id
	                minimumOrderCartSubtotal
	                newStoreCustomersOnly
	                deliveryFee
	                __typename
	              }
	              storeDisclaimers {
	                id
	                disclaimerDetailsLink
	                disclaimerLinkSubstring
	                disclaimerText
	                displayTreatment
	                __typename
	              }
	              __typename
	            }
	            storeMenus(storeId: $storeId, menuId: $menuId) {
	              allMenus {
	                id
	                name
	                subtitle
	                isBusinessEnabled
	                timesOpen
	                __typename
	              }
	              currentMenu {
	                id
	                timesOpen
	                hoursToOrderInAdvance
	                isCatering
	                minOrderSize
	                menuCategories {
	                  ...StoreMenuCategoryFragment
	                  items {
	                    ...StoreMenuListItemFragment
	                    __typename
	                  }
	                  __typename
	                }
	                __typename
	              }
	              __typename
	            }
	            storeCrossLinks(storeId: $storeId) {
	              trendingStores {
	                ...StoreCrossLinkItemFragment
	                __typename
	              }
	              trendingCategories {
	                ...StoreCrossLinkItemFragment
	                __typename
	              }
	              topCuisinesNearMe {
	                ...StoreCrossLinkItemFragment
	                __typename
	              }
	              nearbyCities {
	                ...StoreCrossLinkItemFragment
	                __typename
	              }
	              __typename
	            }
	          }

	        fragment StoreMenuCategoryFragment on StoreMenuCategory {
	          id
	          subtitle
	          title
	          __typename
	        }

	        fragment StoreMenuListItemFragment on StoreMenuListItem {
	          id
	          description
	          isTempDeactivated
	          price
	          imageUrl
	          name
	          __typename
	        }

	        fragment StoreCrossLinkItemFragment on StoreCrossLinkItem {
	          name
	          url
	          __typename
	        }

	    '''
	}
	response = requests.post(url, cookies={'X-CSRFToken': 'MKp9Os0ao3HiPO9ybnSFdDy7HrrodcxiFOWVhuhjaHEybo28kCAfBwMOWp6b78BU'}, data = json.dumps(body), headers = headers)
	print(response)
	allMenus = response.json()['data']['storeMenus']['allMenus']

	#Logistics
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	path = script_dir + "/csvfiles/images/" + foodie_id + "-images-doordash/"
	exceptions = ['a', 'an', 'of', 'the', 'is', 'with', 'or', 'and', 'to', 'from'] + foodie_id.split('-')

	# menu_items = read_items(script_dir, foodie_id)
	json_t = extract_json(foodie_id)
	if(json_t['Items'] == []):
		return 'Could not pull images from database. Potential FoodieID mismatch.'
	menu_items = save_locally(json_t, foodie_id)
	
	foodie_ids = []
	source_ids = []
	items = []
	filenames = []
	matches = []
	n = 0

	for menu in allMenus:
		menu_name = menu['subtitle']
		
		# self.body['variables']['menuId'] = menu['id']
		# print(menu['id'])
		body['variables']['menuId'] = menu['id']
		response = requests.post(url, cookies={'X-CSRFToken': 'MKp9Os0ao3HiPO9ybnSFdDy7HrrodcxiFOWVhuhjaHEybo28kCAfBwMOWp6b78BU'}, data = json.dumps(body), headers = headers)
		for category in response.json()['data']['storeMenus']['currentMenu']['menuCategories']:
			for item in category['items']:
				if(item['imageUrl']):
					item_name = item['name']
					img_url = item['imageUrl']

					matched_items = items_in_sentence(item_name, menu_items, 2, foodie_id, exceptions)
					if(len(matched_items) == 0):
						continue     

					optimized_items = optimize_list(matched_items, item_name.lower())
					for item in optimized_items:
						if n == 0:
							try: os.makedirs(path)
							except OSError: pass

						filename = foodie_id + "-" + str(n) + ".jpg"
						urlretrieve(img_url, path + filename)

						img = cv2.imread(path + filename, cv2.IMREAD_UNCHANGED)

						# get dimensions of image
						dimensions = img.shape

						# height, width, number of channels in image
						height = img.shape[0]
						width = img.shape[1]
						if(height > 300 and width > 450):
							print(height, width)
							foodie_ids.append(foodie_id)
							items.append(item)
							filenames.append(filename)

							matches.append(item_name)
							n += 1
							print(n)

	if n > 0:
		d = {'FoodieID' : foodie_ids, 'Item' : items, 'Filename' : filenames, 'Matches' : matches}
		df = pd.DataFrame(d)
		df.to_excel(path + foodie_id + ".xlsx", sheet_name='Sheet1', encoding="utf8", index=False)
		return 'Added Doordash Imgs'
	else:
		return 'Zero Doordash Imgs Scraped'


# Save menu_items as a file using pickle library (not necessarily human readable)
def write_menu(menu_items, restaurant_tag):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	print(menu_items)
	with open(script_dir + "/output_menu_items/foodie/" + restaurant_tag + ".txt", 'wb') as f:
		pickle.dump(menu_items, f)

def strip_store_id(doordash_id):
	id_arr = doordash_id.split('-')
	store_id = id_arr[len(id_arr) - 1]
	print(store_id)
	return store_id

def scrape_doordash_menu(doordash_id, foodie_id):
	print(doordash_id)
	store_id = strip_store_id(doordash_id)
	print(store_id)
	menu_items = scrape_menu(store_id)
	write_menu(menu_items, foodie_id)

def scrape_doordash_images(doordash_id, foodie_id):
	store_id = strip_store_id(doordash_id)
	return scrape_images(store_id, foodie_id)

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-s', '--store_id', help='Store ID', default='59870')
	parser.add_argument('-f', '--foodie_id', help='Foodie ID', default='eureka!-mountain-view-191')
	parser.add_argument('-d', '--doordash_id', help='DoorDash ID', default='eureka-mountain-view-59870')

	args = vars(parser.parse_args())
	# store_id = args['store_id']
	foodie_id = args['foodie_id']
	doordash_id = args['doordash_id']	
	scrape_doordash_images(doordash_id, foodie_id)	