#!/usr/bin/env python3
import json
import os
from sys import stderr
import time
from requests.exceptions import RequestException
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
    from api import SambunhiAPI

    dry_run = "CRAWLER_DRYRUN" in os.environ

    api = SambunhiAPI()

    api_baseurl = os.environ.get("CRAWLER_API_URL")
    if api_baseurl is not None:
        api.set_base_url(api_baseurl)

    api_token = os.environ.get("CRAWLER_TOKEN")
    if api_token is not None:
        api.set_authorization_token(api_token)

    crawler = RssCrawler()
    for src in api.get_sources():
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
                api.upload_articles(results)
                print("Upload completed!", file=stderr)
            except RequestException as e:
                print(f"Error occurred while uploading: {e}", file=stderr)
        else:
            print("Running in dryrun mode. Skip uploading!", file=stderr)
            print(json.dumps(results, indent=2, ensure_ascii=False))

    print("RSS Feed Crawler completed!", file=stderr)
