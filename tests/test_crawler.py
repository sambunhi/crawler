import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from google_news_crawler import GoogleNewsCrawler

def test_google_search():
    crawler = GoogleNewsCrawler()
    query = "TSMC Ingas"
    results = crawler.google_search(query)
    assert len(results) > 0

