import requests 
from lxml.html import fromstring
from itertools import cycle
from random import shuffle

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = []
    for i in parser.xpath('//tbody/tr')[:200]:
        if i.xpath('.//td[7][contains(text(),"yes")]') and i.xpath('.//td[5][contains(text(),"elite proxy")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.append(proxy)
    shuffle(proxies)
    return proxies

def rotate_proxies(r, url):
    print("Recommend changing VPN. Rotating proxies in the meantime.")
    print(url)
    while(str(r.status_code) != '200'):
        proxies = get_proxies()
        for proxy in proxies:
            r = requests.get(url, proxies={"http": proxy, "https": proxy})
            print(proxy, r.status_code)
            if(str(r.status_code) == "200"):
                break
    return r