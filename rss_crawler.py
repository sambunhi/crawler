#!/usr/bin/env python3
import json
import os
from sys import stderr
import time
from urllib.parse import urljoin
import requests
import feedparser

def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)

class RssCrawler:
    def fetch(self, url):
        feed = feedparser.parse(url)
        output = []
        for entry in feed.entries:
            output.append({
                'title': entry.title,
                'url': entry.link,
                'published_at': time.strftime("%Y-%m-%d", entry.published_parsed),
            })

        return output

if __name__ == "__main__":
    api_baseurl = os.getenv("CRAWLER_API_URL", "https://sambunhi.nycu.one")
    dry_run = "CRAWLER_DRYRUN" in os.environ

    response = requests.get(urljoin(api_baseurl, "/api/v1/crawler"))
    response.raise_for_status()
    sources = response.json()["sources"]

    crawler = RssCrawler()
    for src in sources:
        eprint(f"Fetching: {src['name']} ({src['url']})")
        try:
            results = crawler.fetch(src['url'])
            eprint(f"Found {len(results)} results")
        except Exception as e:
            eprint(f"Error occurred while searching: {e}")
            continue

        for r in results:
            r['source_id'] = src['id']

        if not dry_run:
            try:
                r = requests.post(urljoin(api_baseurl, "/api/v1/article"), json=results)
                r.raise_for_status()
                print("Upload completed!", file=stderr)
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while uploading: {e}", file=stderr)
        else:
            print("Running in dryrun mode. Skip uploading!", file=stderr)
            print(json.dumps(results, indent=2, ensure_ascii=False))

    print("RSS Feed Crawler completed!", file=stderr)
