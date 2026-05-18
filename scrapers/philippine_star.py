from scrapers.base import RSSBaseScraper


class PhilippineStarScraper(RSSBaseScraper):
    SOURCE_NAME = "philippine_star"
    FEED_URLS = [
        "https://www.philstar.com/rss/realtime",
        "https://www.philstar.com/rss/nation",
    ]
