import json
import os
import re

import requests
from bs4 import BeautifulSoup


def _baidu_search(query: str, num_results=8):
    '''
    Perform a Baidu search and return the results as a JSON string.
    '''
    engine_cookie = os.getenv("BAIDU_COOKIE", None)
    if not engine_cookie:
        raise ValueError(f"Current search engine is baidu, please configure cookie information in .env ")

    headers = {
        'Cookie': engine_cookie,
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0"
    }
    url = f'https://www.baidu.com/s?wd={query}&rn={num_results}'
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    search_results = []

    for result in soup.find_all('div', class_=re.compile('^result c-container ')):
        title = result.find('h3', class_='t').get_text()
        link = result.find('a', href=True)['href']
        snippet = result.find('span', class_=re.compile('^content-right_8Zs40'))
        if snippet:
            snippet = snippet.get_text()
        else:
            snippet = ''
        search_results.append({
            'title': title,
            'href': link,
            'snippet': snippet
        })

    return search_to_view(search_results)
    # return json.dumps(search_results, ensure_ascii=False, indent=4)


def search_to_view(results):
    view: str = ""
    for item in results:
        view = view + f"### [{item['title']}]({item['href']}) \n"
        view = view + f"{item['snippet']} \n"
    return view


