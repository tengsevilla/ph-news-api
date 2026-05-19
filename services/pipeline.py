from datetime import datetime, timezone
from zoneinfo import ZoneInfo

_PH_TZ = ZoneInfo("Asia/Manila")

from classifier.client import classify_all
from db.connection import get_session
from db.repositories import (
    delete_topics_for_date,
    insert_politician_impact,
    insert_topic,
    upsert_digest,
    upsert_politician,
)
from scrapers import ALL_SCRAPERS


def run_pipeline(dry_run: bool = False) -> dict:
    # Use Philippine time for the date — the cron fires at midnight PHT (16:00 UTC),
    # so datetime.utcnow().date() would be one day behind the actual PH calendar date.
    today = datetime.now(_PH_TZ).date()
    scraped_at = datetime.now(timezone.utc).replace(tzinfo=None)

    # 1. Scrape
    # HTML scrapers (Senate, House) are fragile — warn when they return almost nothing
    # so broken page structure is caught in logs rather than silently disappearing.
    HTML_SCRAPER_MIN = 2
    RSS_SCRAPER_MIN = 5

    raw_articles = []
    for ScraperClass in ALL_SCRAPERS:
        try:
            articles = ScraperClass().fetch()
            raw_articles.extend(articles)
            min_expected = HTML_SCRAPER_MIN if ScraperClass.SOURCE_NAME in ("senate", "house_of_reps") else RSS_SCRAPER_MIN
            if len(articles) < min_expected:
                print(
                    f"[pipeline] WARNING: {ScraperClass.SOURCE_NAME} returned only "
                    f"{len(articles)} article(s) (expected ≥{min_expected}) — scraper may be broken."
                )
            else:
                print(f"[pipeline] {ScraperClass.SOURCE_NAME}: {len(articles)} articles")
        except Exception as e:
            print(f"[pipeline] {ScraperClass.SOURCE_NAME} scraper failed: {e}")

    # Deduplicate by URL — multiple feeds from the same outlet often overlap
    seen_urls: set[str] = set()
    deduped = []
    for a in raw_articles:
        if a.url and a.url not in seen_urls:
            seen_urls.add(a.url)
            deduped.append(a)
    raw_articles = deduped
    print(f"[pipeline] Raw articles after URL dedup: {len(raw_articles)}")

    # 2. Classify
    topics = classify_all(raw_articles)
    print(f"[pipeline] Topics after classification: {len(topics)}")

    # 3. Drop pure noise — keep topics that have citizen-sector impact OR mention politicians
    before = len(topics)
    topics = [t for t in topics if t.get("affected_sectors") or t.get("politicians")]
    dropped = before - len(topics)
    if dropped:
        print(f"[pipeline] Dropped {dropped}/{before} topics with no sector impact and no politicians")

    if dry_run:
        # raw_sources holds RawArticle objects — not JSON-serializable. Convert them.
        serializable_topics = []
        for t in topics:
            t_copy = {k: v for k, v in t.items() if k != "raw_sources"}
            t_copy["sources"] = [
                {"source": r.source, "url": r.url, "title": r.title,
                 "published_at": r.published_at.isoformat() if r.published_at else None}
                for r in t.get("raw_sources", [])
            ]
            serializable_topics.append(t_copy)
        return {
            "date": str(today),
            "scraped_at": scraped_at.isoformat() + "Z",
            "raw_article_count": len(raw_articles),
            "topic_count": len(topics),
            "dry_run": True,
            "topics": serializable_topics,
        }

    # 3. Persist
    session = get_session()
    try:
        deleted = delete_topics_for_date(session, today)
        if deleted:
            print(f"[pipeline] Cleared {deleted} stale topics from earlier run today.")
        upsert_digest(session, today, scraped_at, len(raw_articles), len(topics))

        for topic_dict in topics:
            topic_id = insert_topic(session, topic_dict, today)

            for pol_dict in topic_dict.get("politicians", []):
                pol_slug = upsert_politician(session, pol_dict)
                if pol_slug:
                    insert_politician_impact(
                        session,
                        politician_slug=pol_slug,
                        topic_id=topic_id,
                        impact=pol_dict.get("impact", "neutral"),
                        reason=pol_dict.get("reason", ""),
                        date_val=today,
                        topic_severity=topic_dict.get("severity"),
                        topic_category=topic_dict.get("category"),
                    )

        session.commit()
        print("[pipeline] Committed to database.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    return {
        "date": str(today),
        "scraped_at": scraped_at.isoformat() + "Z",
        "raw_article_count": len(raw_articles),
        "topic_count": len(topics),
        "dry_run": False,
    }
