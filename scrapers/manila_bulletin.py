from scrapers.base import RSSBaseScraper


class ManilaBulletinScraper(RSSBaseScraper):
    SOURCE_NAME = "manila_bulletin"
    # mb.com.ph direct feed is Cloudflare-blocked on Railway IPs; use Google News RSS instead
    FEED_URLS = [
        "https://news.google.com/rss/search?q=site:mb.com.ph&hl=en-PH&gl=PH&ceid=PH:en",
    ]
