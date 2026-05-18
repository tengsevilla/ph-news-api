import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

_engine = None
_SessionLocal = None


def _normalize_db_url(url: str) -> str:
    # Railway injects "postgres://" (old Heroku style) — SQLAlchemy requires "postgresql+psycopg2://"
    if url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url


def get_engine():
    global _engine
    if _engine is None:
        url = _normalize_db_url(os.environ["DATABASE_URL"])
        _engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_size=3,
            max_overflow=5,
        )
    return _engine


def get_session() -> Session:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _SessionLocal()
