from scrapers.base import RSSBaseScraper


class OfficialGazetteScraper(RSSBaseScraper):
    SOURCE_NAME = "official_gazette"
    # officialgazette.gov.ph is Cloudflare-blocked on Railway IPs; use Google News RSS instead
    FEED_URLS = [
        "https://news.google.com/rss/search?q=officialgazette.gov.ph+proclamation&hl=en-PH&gl=PH&ceid=PH:en",
    ]
