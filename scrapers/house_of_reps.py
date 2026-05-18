from scrapers.base import HTMLBaseScraper, RawArticle


class HouseOfRepsScraper(HTMLBaseScraper):
    SOURCE_NAME = "house_of_reps"
    BASE_URL = "https://www.congress.gov.ph/news/"

    def fetch(self) -> list[RawArticle]:
        articles = []
        try:
            soup = self._get(self.BASE_URL)
            # Congress site lists news items in <article> or .entry-title elements
            for heading in soup.select("h2.entry-title, h3.entry-title, .news-title, article h2, article h3"):
                link = heading.find("a")
                if not link:
                    continue
                title = link.get_text(strip=True)
                href = link.get("href", "")
                if not title:
                    continue
                articles.append(
                    RawArticle(source=self.SOURCE_NAME, url=href, title=title)
                )
        except Exception as e:
            print(f"[{self.SOURCE_NAME}] Failed to fetch: {e}")
        return articles
