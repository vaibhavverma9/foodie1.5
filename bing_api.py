import http.client, urllib.request, urllib.parse, urllib.error, base64
import argparse as ap
import json

headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': '077a11114930423bb4a302f3fa35e0a5',
}

def web_search(query, count):
    params = urllib.parse.urlencode({
        # Request parameters
        'q': query,
        'count': count,
        'offset': '0',
        'mkt': 'en-us',
        'safesearch': 'Moderate',
    })

    urls = []

    try:
        conn = http.client.HTTPSConnection('api.cognitive.microsoft.com')
        conn.request("GET", "/bing/v7.0/search?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    for link_value in json.loads(data)['webPages']['value']:
        urls.append(link_value['url'])
    return urls

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-q', '--query', help='Query', default='girl and the goat reviews')
    parser.add_argument('-c', '--count', help='Count', default='10')

    args = vars(parser.parse_args())
    query = args['query']
    count = args['count']
    web_search(query, count)