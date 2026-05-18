from scrapers.base import RSSBaseScraper


class RapplerScraper(RSSBaseScraper):
    SOURCE_NAME = "rappler"
    FEED_URLS = [
        "https://www.rappler.com/nation/feed/",
        "https://www.rappler.com/business/feed/",
        "https://www.rappler.com/moveph/feed/",
    ]
