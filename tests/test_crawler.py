import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


from sample_crawler import GoogleCrawler

def test_google_search():
    crawler = GoogleCrawler()
    query = "TSMC Ingas"
    results = crawler.google_search(query)
    assert len(results) > 0

def test_get_source():
    crawler = GoogleCrawler()
    target_url = 'https://www.reuters.com/technology/exclusive-ukraine-halts-half-worlds-neon-output-chips-clouding-outlook-2022-03-11/'
    response = crawler.get_source(target_url)
    assert response.status_code == 200

def test_scrape_google():
    query = 'https://www.google.com/search?q='+"TSMC Ingas"
    crawler = GoogleCrawler()
    results = crawler.scrape_google(query)
    assert len(results) > 0


def test_html_getText():
    crawler = GoogleCrawler()
    target_url = 'https://www.reuters.com/technology/exclusive-ukraine-halts-half-worlds-neon-output-chips-clouding-outlook-2022-03-11/'
    response = crawler.get_source(target_url)
    orignal_text = crawler.html_getText(response.text)
    assert len(orignal_text) > 0




