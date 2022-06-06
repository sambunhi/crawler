import requests
from requests_html import HTML, HTMLSession
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class GoogleCrawler():

    def __init__(self):
        self.url = 'https://www.google.com/search?q='

    #  URL 萃取 From Google Search上 , using 第三方套件
    #  https://python-googlesearch.readthedocs.io/en/latest/
    def google_url_search_byOpenSource(query, tbs='qdr:m', num=10):
        array_url = [url for url in search('tsmc', tbs='qdr:m', num=10)]
        return array_url

    # 網路擷取器
    def get_source(self, url):
        try:
            session = HTMLSession()
            response = session.get(url)
            return response
        except requests.exceptions.RequestException as e:
            print(e)

    # URL 萃取 From Google Search上
    def scrape_google(self, query):
        response = self.get_source(self.url + query)
        links = list(response.html.absolute_links)
        google_domains = (
            'https://www.google.',
            'https://google.',
            'https://webcache.googleusercontent.',
            'http://webcache.googleusercontent.',
            'https://policies.google.',
            'https://support.google.',
            'https://maps.google.',
        )

        for url in links[:]:
            if url.startswith(google_domains):
                links.remove(url)
        return links

    # URL萃取器，有link之外，也有標題
    #     qdr:h (past hour)
    #     qdr:d (past day)
    #     qdr:w (past week)
    #     qdr:m (past month)
    #     qdr:y (past year)
    def google_search(self, query, timeline='', page='0'):
        url = self.url + query + '&tbs={timeline}&start={page}'.format(timeline=timeline,page=page)
        print('[Check][URL] URL: {url}'.format(url=url))
        response = self.get_source(url)
        return self.parse_googleResults(response)

    # Google Search Result Parsing
    def parse_googleResults(self, response):
        css_identifier_result = "tF2Cxc"
        css_identifier_title = "h3"
        css_identifier_link = "yuRUbf"
        css_identifier_text = "VwiC3b"
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.findAll("div", {"class": css_identifier_result})
        output = []
        for result in results:
            item = {
                'title': result.find(css_identifier_title).get_text(),
                'link': result.find("div", {"class": css_identifier_link}).find(href=True)['href'],
                'text': result.find("div", {"class": css_identifier_text}).get_text()
            }
            output.append(item)
        return output

    # 解析後，取<p>文字
    def html_getText(self, htmlText):
        orignal_text = ''
        soup = BeautifulSoup(htmlText, 'html.parser')
        for el in soup.find_all('p'):
            orignal_text += ''.join(el.find_all(text=True))
        return orignal_text

    def word_count(self, text):
        counts = dict()
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text)
        #words = text.replace(',','').split()
        for word in words:
            if word not in stop_words:
                if word in counts:
                    counts[word] += 1
                else:
                    counts[word] = 1
        return counts

    def get_wordcount_json(self, whitelist, dict_data):
        data_array = []
        for i in whitelist:
            json_data = {
                'Date' : 'Week1',
                'Company' : i,
                'Count' : dict_data.get(i, 0)
            }
            data_array.append(json_data)
        return data_array

if __name__ == "__main__":
    query = "TSMC ASML"
    path = '/var/log/history/'

    crawler = GoogleCrawler()
    results = crawler.google_search(query, 'qdr:w', '10')
    print("Print 5 Google search results")
    print(results[:5])

    whitelist = ['ASML', 'Intel']
    for result in results:
        response = crawler.get_source(result['link'])
        orignal_text = crawler.html_getText(response.text)
        print("Print html text")
        print(orignal_text[:100])

        result_wordcount = crawler.word_count(orignal_text)
        end_result = crawler.get_wordcount_json(whitelist, result_wordcount)
        print(end_result)
