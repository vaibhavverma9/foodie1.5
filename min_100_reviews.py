import argparse as ap
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from urllib.request import urlopen

# Python functions in scraping_scripts folder
from save_sentences_csv import items_in_sentence_spacy
from run import scrape_data

# 1. Go through each link on Google and extract text 
# 2. For each link, only keep sentence if there is a match

# Gather links from Google
def scrape_reviews(name, city):
	links = []

	#Opening proper webpage
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument("--incognito")
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--disable-gpu')
	driver = webdriver.Chrome(options=chrome_options)
	wiki = "https://www.google.com"
	driver.get(wiki)

	#Locate TripAdvisor webpage
	#First google search
	elem = driver.find_element_by_name("q")
	elem.clear()
	search_string = name + " " + city + " " + zipcode + " reviews"
	elem.send_keys(search_string)
	elem.send_keys(Keys.RETURN)

	#Now click the proper web link
	links += gather_links(driver)

	#Find next pages for Google
	google_pg_links = google_page_links(driver)
	print(len(google_pg_links))
	for google_pg_link in google_pg_links:
		print(google_pg_link)
		driver.get(google_pg_link)
		links += gather_links(driver)

	return links

def gather_links(driver):
	links = []
	elems = driver.find_elements_by_xpath("//h3[@class='LC20lb']")
	for elem in elems:
		parent = elem.find_element_by_xpath("..")
		google_url = parent.get_attribute("href")
		links.append(google_url)
	return links

def google_page_links(driver):
	page_links = []
	elems_pages = driver.find_elements_by_xpath("//a[@class='fl']")
	for elem_page in elems_pages:
		url = elem_page.get_attribute('href')
		if "google.com/search" in url and "start=" in url:
			page_links.append(url)
	return page_links

def extract_text(link):
	texts = []
	try: 
		r = requests.get(link)
		encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
		soup = BeautifulSoup(r.content, "lxml")
		for p in soup.find_all('p'):
			texts.append(p.getText())
		for q in soup.find_all('q'):
			texts.append(q.getText())
		for script_text in soup.find_all("script", attrs={"type" : "application/ld+json"}):
			texts.append(script_text.getText())
	except:
		pass
	return texts

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-r', '--restaurant_name', help='Restaurant name', default='Pizzeria Delfina')
	parser.add_argument('-c', '--city', help='City', default='San Francisco')
	parser.add_argument('-z', '--zipcode', help='Zipcode', default='94115')

	args = vars(parser.parse_args())
	name = args['restaurant_name']
	city = args['city']
	zipcode = args['zipcode']
	links = scrape_reviews(name, city)
	texts = []
	for link in links:
		print("Link: ", link)
		texts += extract_text(link)
	print(len(texts))
