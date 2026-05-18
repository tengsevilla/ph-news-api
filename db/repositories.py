import re
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import desc
from sqlalchemy.orm import Session

from db.models import (
    DailyDigest,
    Politician,
    PoliticianImpactHistory,
    Topic,
    TopicSector,
    TopicSource,
)


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ── Write helpers ──────────────────────────────────────────────────────────────

def delete_topics_for_date(session: Session, date_val: date) -> int:
    """
    Remove all topics (and their children via cascade) for a given date so that
    a re-run on the same day doesn't produce duplicates.
    Also reverses the politician impact counts that were attributed to those topics.
    Returns the number of topics deleted.
    """
    topic_ids = [
        row[0]
        for row in session.query(Topic.id).filter_by(digest_date=date_val).all()
    ]
    if not topic_ids:
        return 0

    # Reverse politician counters for the topics being deleted
    for history in (
        session.query(PoliticianImpactHistory)
        .filter(PoliticianImpactHistory.topic_id.in_(topic_ids))
        .all()
    ):
        pol = session.query(Politician).filter_by(slug=history.politician_slug).first()
        if pol:
            if history.impact == "positive":
                pol.positive_count = max(0, (pol.positive_count or 0) - 1)
            elif history.impact == "negative":
                pol.negative_count = max(0, (pol.negative_count or 0) - 1)
            else:
                pol.neutral_count = max(0, (pol.neutral_count or 0) - 1)
            pol.total_mentions = max(0, (pol.total_mentions or 0) - 1)
            total = (pol.positive_count or 0) + (pol.negative_count or 0) + (pol.neutral_count or 0)
            pol.impact_score = (
                ((pol.positive_count or 0) - (pol.negative_count or 0)) / total
                if total > 0 else 0.0
            )

    session.query(PoliticianImpactHistory).filter(
        PoliticianImpactHistory.topic_id.in_(topic_ids)
    ).delete(synchronize_session=False)
    session.query(TopicSector).filter(
        TopicSector.topic_id.in_(topic_ids)
    ).delete(synchronize_session=False)
    session.query(TopicSource).filter(
        TopicSource.topic_id.in_(topic_ids)
    ).delete(synchronize_session=False)
    session.query(Topic).filter(Topic.id.in_(topic_ids)).delete(
        synchronize_session=False
    )
    session.flush()
    return len(topic_ids)


def upsert_digest(
    session: Session,
    date_val: date,
    scraped_at: datetime,
    raw_count: int,
    topic_count: int,
) -> None:
    digest = session.query(DailyDigest).filter_by(date=date_val).first()
    if digest:
        digest.scraped_at = scraped_at
        digest.raw_article_count = raw_count
        digest.topic_count = topic_count
    else:
        digest = DailyDigest(
            date=date_val,
            scraped_at=scraped_at,
            raw_article_count=raw_count,
            topic_count=topic_count,
        )
        session.add(digest)
    session.flush()


def insert_topic(session: Session, topic_dict: dict, digest_date: date) -> str:
    raw_sources = topic_dict.get("raw_sources", [])
    topic_id = str(uuid.uuid4())

    topic = Topic(
        id=topic_id,
        digest_date=digest_date,
        # Core classification
        topic=topic_dict.get("topic", ""),
        summary=topic_dict.get("summary", ""),
        category=topic_dict.get("category", ""),
        sentiment=topic_dict.get("sentiment", ""),
        impact_level=topic_dict.get("impact_level", ""),
        event_type=topic_dict.get("event_type", ""),
        # Analytical dimensions
        urgency=topic_dict.get("urgency", ""),
        resolution_status=topic_dict.get("resolution_status", ""),
        government_response=topic_dict.get("government_response", "unknown"),
        region_primary=topic_dict.get("region_primary", ""),
        # Gamification
        severity=topic_dict.get("severity"),
        affected_population_estimate=topic_dict.get("affected_population_estimate", ""),
        civic_action=topic_dict.get("civic_action", ""),
        # Search & tagging (JSONB — stored as native Python lists)
        keywords=topic_dict.get("keywords") or [],
        policy_tags=topic_dict.get("policy_tags") or [],
        # Data quality
        confidence_score=topic_dict.get("confidence_score"),
        source_count=len(raw_sources),
        created_at=_utcnow(),
    )
    session.add(topic)

    for raw in raw_sources:
        session.add(
            TopicSource(
                topic_id=topic_id,
                source=raw.source,
                url=raw.url,
                title=raw.title,
                published_at=raw.published_at,
            )
        )

    # affected_sectors: list of {"slug": ..., "intensity": ...}
    for sector in topic_dict.get("affected_sectors", []):
        if isinstance(sector, dict):
            slug = sector.get("slug", "")
            intensity = sector.get("intensity", "medium")
        else:
            slug = sector
            intensity = "medium"
        if slug:
            session.add(TopicSector(topic_id=topic_id, sector_slug=slug, impact_intensity=intensity))

    session.flush()
    topic_dict["_topic_id"] = topic_id
    return topic_id


def upsert_politician(session: Session, pol_dict: dict) -> str | None:
    name = (pol_dict.get("name") or "").strip()
    if not name:
        return None

    slug = _slugify(name)
    impact = pol_dict.get("impact", "neutral")

    pol = session.query(Politician).filter_by(slug=slug).first()
    if not pol:
        pol = Politician(
            slug=slug,
            name=name,
            position=pol_dict.get("position", ""),
            party=pol_dict.get("party", ""),
            branch=pol_dict.get("branch", ""),
            province=pol_dict.get("province", ""),
            positive_count=0,
            negative_count=0,
            neutral_count=0,
            total_mentions=0,
            impact_score=0.0,
        )
        session.add(pol)

    if impact == "positive":
        pol.positive_count = (pol.positive_count or 0) + 1
    elif impact == "negative":
        pol.negative_count = (pol.negative_count or 0) + 1
    else:
        pol.neutral_count = (pol.neutral_count or 0) + 1

    pol.total_mentions = (pol.total_mentions or 0) + 1

    total = (pol.positive_count or 0) + (pol.negative_count or 0) + (pol.neutral_count or 0)
    if total > 0:
        pol.impact_score = ((pol.positive_count or 0) - (pol.negative_count or 0)) / total

    pol.last_updated = _utcnow()
    session.flush()
    return slug


def insert_politician_impact(
    session: Session,
    politician_slug: str,
    topic_id: str,
    impact: str,
    reason: str,
    date_val: date,
    topic_severity: int | None = None,
    topic_category: str | None = None,
) -> None:
    session.add(
        PoliticianImpactHistory(
            politician_slug=politician_slug,
            topic_id=topic_id,
            impact=impact,
            reason=reason,
            date=date_val,
            topic_severity=topic_severity,
            topic_category=topic_category,
        )
    )
    session.flush()


# ── Read helpers ───────────────────────────────────────────────────────────────

def get_topics(
    session: Session,
    date: str | None = None,
    category: str | None = None,
    limit: int = 50,
) -> list[dict]:
    q = session.query(Topic)
    if date:
        q = q.filter(Topic.digest_date == date)
    if category:
        q = q.filter(Topic.category == category)
    topics = q.order_by(desc(Topic.created_at)).limit(limit).all()
    return [_topic_to_dict(t) for t in topics]


def get_daily_digest(session: Session, date: str) -> dict:
    digest = session.query(DailyDigest).filter_by(date=date).first()
    topics = session.query(Topic).filter_by(digest_date=date).all()
    return {
        "date": date,
        "digest": {
            "scraped_at": digest.scraped_at.isoformat() if digest else None,
            "raw_article_count": digest.raw_article_count if digest else 0,
            "topic_count": digest.topic_count if digest else 0,
        },
        "topics": [_topic_to_dict(t) for t in topics],
    }


def list_politicians(session: Session) -> list[dict]:
    pols = session.query(Politician).order_by(desc(Politician.impact_score)).all()
    return [_pol_to_dict(p) for p in pols]


def get_politician_profile(session: Session, slug: str) -> dict | None:
    pol = session.query(Politician).filter_by(slug=slug).first()
    if not pol:
        return None

    rows = (
        session.query(PoliticianImpactHistory, Topic)
        .join(Topic, PoliticianImpactHistory.topic_id == Topic.id)
        .filter(PoliticianImpactHistory.politician_slug == slug)
        .order_by(desc(PoliticianImpactHistory.date))
        .all()
    )

    return {
        **_pol_to_dict(pol),
        "impact_history": [
            {
                "topic_id": h.topic_id,
                "topic": t.topic,
                "impact": h.impact,
                "reason": h.reason,
                "date": str(h.date),
                "topic_severity": h.topic_severity,
                "topic_category": h.topic_category,
            }
            for h, t in rows
        ],
    }


def get_sector_topics(session: Session, slug: str, limit: int = 20) -> dict:
    topics = (
        session.query(Topic)
        .join(TopicSector, Topic.id == TopicSector.topic_id)
        .filter(TopicSector.sector_slug == slug)
        .order_by(desc(Topic.created_at))
        .limit(limit)
        .all()
    )
    return {"sector": slug, "topics": [_topic_to_dict(t) for t in topics]}


# ── Serialisers ────────────────────────────────────────────────────────────────

def _topic_to_dict(t: Topic) -> dict:
    return {
        "id": t.id,
        # Core
        "topic": t.topic,
        "summary": t.summary,
        "category": t.category,
        "sentiment": t.sentiment,
        "impact_level": t.impact_level,
        "event_type": t.event_type,
        # Analytical
        "urgency": t.urgency,
        "resolution_status": t.resolution_status,
        "government_response": t.government_response,
        "region_primary": t.region_primary,
        # Gamification
        "severity": t.severity,
        "affected_population_estimate": t.affected_population_estimate,
        "civic_action": t.civic_action,
        # Search & tagging (JSONB returns native Python list)
        "keywords": t.keywords or [],
        "policy_tags": t.policy_tags or [],
        # Data quality
        "confidence_score": t.confidence_score,
        "source_count": t.source_count,
        # Meta
        "digest_date": str(t.digest_date),
        "created_at": t.created_at.isoformat() if t.created_at else None,
        # Relations
        "affected_sectors": [
            {"slug": ts.sector_slug, "intensity": ts.impact_intensity}
            for ts in t.sector_links
        ],
        "sources": [
            {
                "source": s.source,
                "url": s.url,
                "title": s.title,
                "published_at": s.published_at.isoformat() if s.published_at else None,
            }
            for s in t.sources
        ],
    }


def _pol_to_dict(p: Politician) -> dict:
    return {
        "slug": p.slug,
        "name": p.name,
        "position": p.position,
        "party": p.party,
        "branch": p.branch,
        "province": p.province,
        "positive_count": p.positive_count,
        "negative_count": p.negative_count,
        "neutral_count": p.neutral_count,
        "total_mentions": p.total_mentions,
        "impact_score": p.impact_score,
        "last_updated": p.last_updated.isoformat() if p.last_updated else None,
    }
