from scrapers.base import RSSBaseScraper


class SunStarScraper(RSSBaseScraper):
    SOURCE_NAME = "sun_star"
    FEED_URLS = [
        "https://news.google.com/rss/search?q=SunStar+Philippines&hl=en-PH&gl=PH&ceid=PH:en",
    ]
