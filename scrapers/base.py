from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import feedparser
import requests
from bs4 import BeautifulSoup


@dataclass
class RawArticle:
    source: str
    url: str
    title: str
    published_at: Optional[datetime] = None
    summary: Optional[str] = None


class RSSBaseScraper:
    SOURCE_NAME: str = ""
    FEED_URLS: list = field(default_factory=list)

    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    def fetch(self) -> list[RawArticle]:
        articles = []
        for feed_url in self.FEED_URLS:
            try:
                resp = requests.get(feed_url, headers=self._HEADERS, timeout=15)
                resp.raise_for_status()
                feed = feedparser.parse(resp.text)
                for entry in feed.entries:
                    published_at = None
                    if getattr(entry, "published_parsed", None):
                        published_at = datetime(*entry.published_parsed[:6])
                    articles.append(
                        RawArticle(
                            source=self.SOURCE_NAME,
                            url=entry.get("link", ""),
                            title=entry.get("title", ""),
                            published_at=published_at,
                            summary=entry.get("summary") or entry.get("description", ""),
                        )
                    )
            except Exception as e:
                print(f"[{self.SOURCE_NAME}] Failed to fetch {feed_url}: {e}")
        return articles


class HTMLBaseScraper:
    SOURCE_NAME: str = ""

    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    def _get(self, url: str) -> BeautifulSoup:
        resp = requests.get(url, headers=self._HEADERS, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")

    def fetch(self) -> list[RawArticle]:
        raise NotImplementedError
