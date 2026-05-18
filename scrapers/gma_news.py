from scrapers.base import RSSBaseScraper


class GMANewsScraper(RSSBaseScraper):
    SOURCE_NAME = "gma_news"
    FEED_URLS = [
        "https://www.gmanetwork.com/news/rss/topstories.htm",
        "https://www.gmanetwork.com/news/rss/nation.htm",
        "https://www.gmanetwork.com/news/rss/money.htm",
    ]
