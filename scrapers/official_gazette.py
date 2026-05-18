from scrapers.base import RSSBaseScraper


class OfficialGazetteScraper(RSSBaseScraper):
    SOURCE_NAME = "official_gazette"
    FEED_URLS = [
        "https://www.officialgazette.gov.ph/feed/",
    ]
