#!/usr/bin/env python3
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
        results = soup.findAll("g-card")
        output = []
        for card in results:
            a = card.find("a")
            title = a.find("div", {"role": "heading"})
            item = {
                'title': title.get_text(),
                'link': a['href'],
                'text': title.find_next_sibling("div").get_text()
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
        return self.parse_google_results(response)

if __name__ == "__main__":
    query = "TSMC ASML"

    crawler = GoogleNewsCrawler()
    results = crawler.google_search(query, num=10, timeline='qdr:d')
    print(results)
