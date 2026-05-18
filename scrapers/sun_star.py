from scrapers.base import RSSBaseScraper


class SunStarScraper(RSSBaseScraper):
    SOURCE_NAME = "sun_star"
    FEED_URLS = [
        "https://www.sunstar.com.ph/feed/",
    ]
