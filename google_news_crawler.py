#!/usr/bin/env python3
import json
from urllib.parse import urljoin
import os
from sys import stderr
import requests
from requests_html import HTML, HTMLSession
from bs4 import BeautifulSoup

class GoogleNewsCrawler:
    def __init__(self):
        self.base_url = 'https://www.google.com/search'

    # 網路擷取器
    def search_request(self, keyword, **kwargs):
        session = HTMLSession()
        search_params = {k: v for k, v in kwargs.items() if v is not None}
        search_params['q'] = keyword
        search_params['tbm'] = 'nws'

        response = session.get(self.base_url,
            params=search_params,
        )
        return response

    # Google Search Result Parsing
    def parse_google_results(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        rso = soup.find(id="rso")
        results = rso.findAll("a")
        output = []
        for a in results:
            title = a.find("div", {"role": "heading"})
            item = {
                'title': title.get_text(),
                'url': a['href'],
                #'text': title.find_next_sibling("div").get_text()
            }
            output.append(item)
        return output

    # URL萃取器，有link之外，也有標題
    #     qdr:h (past hour)
    #     qdr:d (past day)
    #     qdr:w (past week)
    #     qdr:m (past month)
    #     qdr:y (past year)
    def google_search(self, keyword, start=0, num=None, timeline=None):
        response = self.search_request(keyword,
            start=start,
            num=num,
            tbm=timeline,
        )
        #return self.parse_google_results(response)
        r = self.parse_google_results(response)
        if len(r) == 0:
            print(response.text)
        return r

if __name__ == "__main__":
    api_baseurl = os.getenv("CRAWLER_API_URL", "https://sambunhi.nycu.one")
    dry_run = "CRAWLER_DRYRUN" in os.environ

    response = requests.get(urljoin(api_baseurl, "/api/v1/crawler"))
    response.raise_for_status()
    keywords = response.json()["keywords"]

    crawler = GoogleNewsCrawler()
    for k in keywords:
        print(f"Searching: {k}", file=stderr)
        try:
            results = crawler.google_search(k, num=50, timeline='qdr:d')
            print(f"Found {len(results)} results", file=stderr)
        except Exception as e:
            print(f"Error occurred while searching: {e}", file=stderr)
            continue

        if not dry_run:
            try:
                r = requests.put(urljoin(api_baseurl, "/api/v1/article"), json=results)
                r.raise_for_status()
                print("Upload completed!", file=stderr)
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while uploading: {e}", file=stderr)
        else:
            print("Running in dryrun mode. Skip uploading!", file=stderr)
            print(json.dumps(results, indent=2, ensure_ascii=False))

    print("Google News Crawler completed!", file=stderr)
