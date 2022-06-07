#!/usr/bin/env python3
import json
import os
from sys import stderr
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import requests
import jieba

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
    api_baseurl = os.getenv("CRAWLER_API_URL", "https://sambunhi.nycu.one")
    dry_run = "CRAWLER_DRYRUN" in os.environ

    cfg_response = requests.get(urljoin(api_baseurl, "/api/v1/crawler"))
    cfg_response.raise_for_status()
    keywords = cfg_response.json()["keywords"]

    tokenizer = ChineseTokenizer()
    for word in keywords:
        tokenizer.add_keyword(word)

    tasks_response = requests.get(urljoin(api_baseurl, "/api/v1/crawler/link"))
    tasks_response.raise_for_status()
    tasks = tasks_response.json()

    for task in tasks:
        eprint(f"Fetching: {task}")
        try:
            result = tokenizer.tokenize_from_url(task)
            result = tokenizer.filter_keyword(result)
            eprint("Tokenize completed!")
        except Exception as e:
            eprint(f"Error occurred while searching: {e}")
            continue

        if not dry_run:
            try:
                r = requests.put(urljoin(api_baseurl, "/api/v1/article"), json={
                    'url': task,
                    'keywords': result,
                })
                r.raise_for_status()
                print("Upload completed!", file=stderr)
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while uploading: {e}", file=stderr)
        else:
            print("Running in dryrun mode. Skip uploading!", file=stderr)
            print(json.dumps(result, indent=2, ensure_ascii=False))

    print("Tokenize completed!", file=stderr)
