from scrapers.base import RSSBaseScraper


class CNNPhilippinesScraper(RSSBaseScraper):
    SOURCE_NAME = "cnn_ph"
    FEED_URLS = [
        "https://www.cnnphilippines.com/rss/cnn-philippines-top-stories.xml",
    ]
