from scrapers.base import RSSBaseScraper


class GMANewsScraper(RSSBaseScraper):
    SOURCE_NAME = "gma_news"
    FEED_URLS = [
        "https://data.gmanetwork.com/gno/rss/news/feed.xml",
        "https://data.gmanetwork.com/gno/rss/news/nation/feed.xml",
        "https://data.gmanetwork.com/gno/rss/money/feed.xml",
    ]
