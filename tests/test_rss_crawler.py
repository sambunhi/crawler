import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from rss_crawler import RssCrawler

def test_rss_crawler():
    crawler = RssCrawler()
    results = crawler.fetch("https://theme.udn.com/rss/news/1004/6772/6775?ch=theme")
    assert len(results) > 0
