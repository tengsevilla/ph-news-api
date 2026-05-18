from scrapers.base import RSSBaseScraper


class ABSCBNScraper(RSSBaseScraper):
    SOURCE_NAME = "abs_cbn"
    FEED_URLS = [
        "https://news.abs-cbn.com/rss/headlines",
    ]
