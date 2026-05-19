from scrapers.base import RSSBaseScraper


class HouseOfRepsScraper(RSSBaseScraper):
    SOURCE_NAME = "house_of_reps"
    FEED_URLS = [
        "https://news.google.com/rss/search?q=House+of+Representatives+Philippines+Congress+bill&hl=en-PH&gl=PH&ceid=PH:en",
        "https://news.google.com/rss/search?q=Philippine+Congress+legislation+Kamara&hl=en-PH&gl=PH&ceid=PH:en",
    ]
