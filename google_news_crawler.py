#!/usr/bin/env python3
import json
import os
import sys
from sys import stderr
from time import localtime, strftime
from requests.exceptions import RequestException
from requests_html import HTMLSession
from bs4 import BeautifulSoup

def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)

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
    from api import SambunhiAPI

    source_name = os.getenv("CRAWLER_SOURCE_NAME", "Google")
    dry_run = "CRAWLER_DRYRUN" in os.environ

    api = SambunhiAPI()

    api_baseurl = os.environ.get("CRAWLER_API_URL")
    if api_baseurl is not None:
        api.set_base_url(api_baseurl)

    api_token = os.environ.get("CRAWLER_TOKEN")
    if api_token is not None:
        api.set_authorization_token(api_token)

    google_source_id = api.get_source_id_from_name(source_name)
    if google_source_id is None:
        eprint(f"Source list doesn't contain {source_name}.")
        eprint("GoogleNews Crawler is disabled. Exit now...")
        sys.exit()

    crawler = GoogleNewsCrawler()
    for k in api.get_keywords():
        print(f"Searching: {k}", file=stderr)
        try:
            results = crawler.google_search(k, num=50, timeline='qdr:d')
            eprint(f"Found {len(results)} results")
        except Exception as e:
            eprint(f"Error occurred while searching: {e}")
            continue

        for r in results:
            r['source_id'] = google_source_id
            r['published_at'] = strftime("%Y-%m-%d", localtime())

        if not dry_run:
            try:
                api.upload_articles(results)
                eprint("Upload completed!")
            except RequestException as e:
                eprint(f"Error occurred while uploading: {e}")
        else:
            eprint("Running in dryrun mode. Skip uploading!")
            print(json.dumps(results, indent=2, ensure_ascii=False))

    eprint("Google News Crawler completed!")
