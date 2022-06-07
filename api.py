import requests
from requests import Session, Request
from urllib.parse import urljoin

class SambunhiAPI:
    def __init__(self):
        self.crawler_cfg = None
        self.token = None
        self.base_url = "https://sambunhi.nycu.one"

    def set_base_url(self, url):
        if url is not None:
            self.base_url = url

    def set_authorization_token(self, token):
        self.token = token

    def send_request(self, method, path, **kwargs):
        req = Request(method, urljoin(self.base_url, path), **kwargs)
        prepreq = req.prepare()
        if self.token is not None:
            prepreq.headers["Authorization"] = f"Bearer {self.token}"

        s = requests.Session()
        return s.send(prepreq, timeout=5)

    def fetch_crawler_config(self):
        r = self.send_request("GET", "/api/v1/crawler")
        r.raise_for_status()
        self.crawler_cfg = r.json()

    def get_keywords(self):
        if self.crawler_cfg is None:
            self.fetch_crawler_config()

        return self.crawler_cfg["keywords"]

    def get_sources(self):
        if self.crawler_cfg is None:
            self.fetch_crawler_config()

        return self.crawler_cfg["sources"]

    def get_source_id_from_name(self, name):
        sources = self.get_sources()
        for src in sources:
            if src["name"] == name:
                return src["id"]

        return None

    def get_untokenized_links(self):
        r = self.send_request("GET", "/api/v1/crawler/link")
        r.raise_for_status()
        return r.json()

    def upload_articles(self, articles):
        r = self.send_request("POST", "/api/v1/article", json=articles)
        r.raise_for_status()

    def update_article_keywords(self, article_url, keywords):
        r = self.send_request("PUT", "/api/v1/article", json={
            'url': article_url,
            'keywords': keywords,
        })
        r.raise_for_status()
