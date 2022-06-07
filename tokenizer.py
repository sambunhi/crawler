#!/usr/bin/env python3
import json
import os
from sys import stderr
from bs4 import BeautifulSoup
import jieba
from requests_html import HTMLSession
from requests.exceptions import RequestException

def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)

class ChineseTokenizer:
    def __init__(self):
        self.jt = jieba.Tokenizer()
        self.jt.initialize()
        self.keywords = []

    def add_keyword(self, word: str):
        self.jt.add_word(word)
        self.keywords.append(word)

    def filter_keyword(self, result):
        filtered_result = { k: v for k, v in result.items() if k in self.keywords }
        return filtered_result

    def tokenize(self, text: str):
        result = {}
        for word in self.jt.cut(text):
            result[word] = result.get(word, 0) + 1
        return result

    def tokenize_from_url(self, url):
        session = HTMLSession()
        response = session.get(url)

        orignal_text = ''
        soup = BeautifulSoup(response.text, 'html.parser')
        for el in soup.find_all('p'):
            orignal_text += ''.join(el.find_all(text=True))

        return self.tokenize(orignal_text)

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

    tokenizer = ChineseTokenizer()

    keywords = api.get_keywords()
    for word in keywords:
        tokenizer.add_keyword(word)

    tasks = api.get_untokenized_links()
    for url in tasks:
        eprint(f"Fetching: {url}")
        try:
            result = tokenizer.tokenize_from_url(url)
            result = tokenizer.filter_keyword(result)
            eprint("Tokenize completed!")
        except Exception as e:
            eprint(f"Error occurred while searching: {e}")
            continue

        if not dry_run:
            try:
                api.update_article_keywords(url, result)
                print("Upload completed!", file=stderr)
            except RequestException as e:
                print(f"Error occurred while uploading: {e}", file=stderr)
        else:
            print("Running in dryrun mode. Skip uploading!", file=stderr)
            print(json.dumps(result, indent=2, ensure_ascii=False))

    print("Tokenize completed!", file=stderr)
