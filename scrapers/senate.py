from scrapers.base import RSSBaseScraper


class SenateScraper(RSSBaseScraper):
    SOURCE_NAME = "senate"
    FEED_URLS = [
        "https://news.google.com/rss/search?q=Senate+Philippines+press+release+bill&hl=en-PH&gl=PH&ceid=PH:en",
        "https://news.google.com/rss/search?q=Philippine+Senate+legislation+hearing&hl=en-PH&gl=PH&ceid=PH:en",
    ]
