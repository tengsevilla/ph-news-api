from scrapers.base import HTMLBaseScraper, RawArticle


class SenateScraper(HTMLBaseScraper):
    SOURCE_NAME = "senate"
    BASE_URL = "https://legacy.senate.gov.ph/press_release/press_releases.asp"

    def fetch(self) -> list[RawArticle]:
        articles = []
        try:
            soup = self._get(self.BASE_URL)
            for link in soup.select("td a[href]"):
                title = link.get_text(strip=True)
                href = link.get("href", "")
                if not title or len(title) < 10:
                    continue
                if not href.startswith("http"):
                    href = f"https://legacy.senate.gov.ph/press_release/{href.lstrip('/')}"
                articles.append(
                    RawArticle(source=self.SOURCE_NAME, url=href, title=title)
                )
        except Exception as e:
            print(f"[{self.SOURCE_NAME}] Failed to fetch: {e}")
        return articles
