from scrapers.base import RSSBaseScraper


class BusinessWorldScraper(RSSBaseScraper):
    SOURCE_NAME = "business_world"
    FEED_URLS = [
        "https://www.bworldonline.com/feed/",
    ]
