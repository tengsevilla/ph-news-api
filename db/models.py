from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class DailyDigest(Base):
    __tablename__ = "daily_digests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, unique=True, nullable=False)
    scraped_at = Column(DateTime, nullable=False)
    raw_article_count = Column(Integer, nullable=False)
    topic_count = Column(Integer, nullable=False)


class Topic(Base):
    __tablename__ = "topics"

    id = Column(String(36), primary_key=True)
    digest_date = Column(Date, ForeignKey("daily_digests.date"), nullable=False)

    # Core classification
    topic = Column(Text, nullable=False)
    summary = Column(Text)
    category = Column(String(50))           # politics|economy|health|...
    sentiment = Column(String(20))          # positive|negative|neutral
    impact_level = Column(String(20))       # national|regional|local
    event_type = Column(String(50))         # legislation|corruption|calamity|...

    # Analytical dimensions
    urgency = Column(String(20))            # immediate|short_term|ongoing|chronic
    resolution_status = Column(String(20))  # developing|ongoing|resolved|escalating
    government_response = Column(String(20))# yes|no|partial|unknown
    region_primary = Column(String(60))     # NCR|CALABARZON|National|...

    # Gamification
    severity = Column(Integer)              # 1–5
    affected_population_estimate = Column(Text)
    civic_action = Column(Text)             # suggested citizen action

    # Search & tagging
    keywords = Column(JSONB)               # ["keyword1", "keyword2", ...]
    policy_tags = Column(JSONB)            # ["agricultural_subsidy", "land_reform", ...]

    # Data quality
    confidence_score = Column(Float)        # 0.0–1.0, AI self-assessed
    source_count = Column(Integer)          # how many raw articles formed this topic

    created_at = Column(DateTime)

    sources = relationship("TopicSource", back_populates="topic_ref", lazy="joined")
    sector_links = relationship("TopicSector", back_populates="topic_ref", lazy="joined")


class TopicSource(Base):
    __tablename__ = "topic_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(String(36), ForeignKey("topics.id"), nullable=False)
    source = Column(String(50))
    url = Column(Text)
    title = Column(Text)
    published_at = Column(DateTime)

    topic_ref = relationship("Topic", back_populates="sources")


class TopicSector(Base):
    __tablename__ = "topic_sectors"

    topic_id = Column(String(36), ForeignKey("topics.id"), primary_key=True)
    sector_slug = Column(String(50), primary_key=True)
    impact_intensity = Column(String(10), default="medium")  # high|medium|low

    topic_ref = relationship("Topic", back_populates="sector_links")


class Politician(Base):
    __tablename__ = "politicians"

    slug = Column(String(100), primary_key=True)
    name = Column(String(200))
    position = Column(String(100))
    party = Column(String(100))
    branch = Column(String(30))             # legislative|executive|local
    province = Column(String(100))          # region/province they represent

    # Running impact counters
    positive_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    total_mentions = Column(Integer, default=0)  # pos + neg + neutral

    # Scores
    impact_score = Column(Float, default=0.0)    # (pos − neg) / total, −1.0 to +1.0

    last_updated = Column(DateTime)

    impact_history = relationship("PoliticianImpactHistory", back_populates="politician")


class PoliticianImpactHistory(Base):
    __tablename__ = "politician_impact_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    politician_slug = Column(String(100), ForeignKey("politicians.slug"), nullable=False)
    topic_id = Column(String(36), ForeignKey("topics.id"), nullable=False)
    impact = Column(String(20))             # positive|negative|neutral
    reason = Column(Text)
    date = Column(Date)

    # Denormalized from topic for fast filtered/weighted queries
    topic_severity = Column(Integer)        # 1–5, copied from topic at insert time
    topic_category = Column(String(50))     # e.g. "economy", for per-domain analysis

    politician = relationship("Politician", back_populates="impact_history")
