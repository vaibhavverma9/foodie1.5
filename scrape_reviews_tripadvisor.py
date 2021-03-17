import ast, json, string, operator, re, os, time, pickle, requests
import argparse as ap
from bs4 import BeautifulSoup
from urllib.request import urlopen
from scrape_comments import read_user
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

#Note that Girl and the Goat with about 2.5k reviews takes about 8 min
def scrape_tripadvisor_data(search_query, max_count):
    #Open browser in incognito
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("http://www.google.com")

    #Locate TripAdvisor webpage
    #First google search
    elem = driver.find_element_by_name("q")
    elem.clear()
    search_string = "tripadvisor " + search_query.replace("-"," ")
    elem.send_keys(search_string)
    elem.send_keys(Keys.RETURN)
    #Now click the proper web link
    elem1 = driver.find_element_by_xpath("//h3[@class='LC20lb']")
    parent = elem1.find_element_by_xpath("..")
    parent.get_attribute("outerHTML")
    parent.get_attribute("href")
    assert "tripadvisor" in parent.get_attribute("href")
    elem1.click()

    #Now harvest reviews
    n = 1
    count = 0
    output = []

    #Get first page of reviews
    reviews = driver.find_elements_by_xpath("//div[@class='prw_rup prw_reviews_text_summary_hsx']")
    try:
        more_toggle = reviews[0].find_element_by_xpath(".//span")
        if "More" in more_toggle.text:
            more_toggle.click()
            time.sleep(2)
            reviews = driver.find_elements_by_xpath("//div[@class='prw_rup prw_reviews_text_summary_hsx']")
    except:
        pass
    for i in range(0,len(reviews)):
        parent = reviews[i].find_element_by_xpath("..")
        if parent.get_attribute('class') == 'mgrRspnInline':
            continue
        sub_review = reviews[i].find_element_by_xpath(".//p[@class='partial_entry']")
        #print(sub_review.text)
        count += 1 
        output.append(sub_review.text)

    while(True and count < max_count):
        #Move to next page
        n += 1
        xpath = "//a[@data-page-number='"+str(n)+"']"
        try:
            new_page = driver.find_element_by_xpath(xpath)
            new_page.click()
            time.sleep(.8)

            #Extract reviews from current page
            reviews = driver.find_elements_by_xpath("//div[@class='prw_rup prw_reviews_text_summary_hsx']")
            try:
                #Clicking the "more" option
                #Doesn't work on occasion for some reason; maybe not waiting long enough?
                more_toggle = reviews[0].find_element_by_xpath(".//span")
                if "More" in more_toggle.text:
                    more_toggle.click()
                    time.sleep(2)
                    reviews = driver.find_elements_by_xpath("//div[@class='prw_rup prw_reviews_text_summary_hsx']")
            except:
                pass
            for i in range(0,len(reviews)):
                parent = reviews[i].find_element_by_xpath("..")
                if parent.get_attribute('class') == 'mgrRspnInline':
                    continue
                sub_review = reviews[i].find_element_by_xpath(".//p[@class='partial_entry']")
                #print(sub_review.text)
                count += 1 
                output.append(sub_review.text)

        except Exception as e:
            if "Unable to locate element" in str(e):
                break
            else:
                n = n-1
                #print(e)
    driver.close()
    return(output)

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-s', '--search_query', help='Search Query', default='girl-and-the-goat-chicago')
    parser.add_argument('-n', '--n', help='Max Count', default='100')

    args = vars(parser.parse_args())
    search_query = args['search_query']
    n = int(args['n'])
    print(scrape_tripadvisor_data(search_query, n))