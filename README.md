# Sambunhi Crawler 三文魚爬蟲

The crawler is used to provide news information for Sambunhi. The crawler has three components.
Each component is an independent application.

## google_news_crawler
- This crawler uses configured keywords to search Google News and parse the search results into JSON.
- Then upload the url to the server.

## rss_crawler
- This crawler fetchs configured RSS sources and convert the results to JSON.
- Then upload the url to the server.

## tokenizer
- The component fetch all not yet tokenized articles.
- It uses jieba library to tokenize the article.
- Finally, it calculates the frequency of the wanted keywords and upload to the server.

# Deployment
- All the dockerfiles are placed under containers/ directory.
- Each image can be run directly.

## Environment Variables
- `CRAWLER_API_URL`: The base url of the server
    - Default: `https://sambunhi.nycu.one`
- `CRAWLER_SOURCE_NAME`: The source name of this crawler, the crawler use this to get its source id
    - Used by:
        - google_news_crawler
            - Default: `Google`
- `CRAWLER_DRYRUN`: If this variable is defined, the application will print the result instead of upload it to the server.
- `CRAWLER_TOKEN`: The crawler use the value of this variable as the API token.
    - Optional


# Unit tests
- The unit tests is located under tests/ directory
- To execute the tests, run this command:

    ```bash
    python -m pytest . tests --doctest-modules --junitxml=test-results.xml --cov-config=.coveragerc --cov=. --cov-report=html
    ```

- The coverage would be placed in htmlcov/ directory.
