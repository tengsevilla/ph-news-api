from fastapi import APIRouter, Query

from db.connection import get_session
from db.repositories import get_topics, get_daily_digest

router = APIRouter()


@router.get("/topics")
def list_topics(
    date: str = None,
    category: str = None,
    limit: int = Query(50, le=200),
):
    session = get_session()
    try:
        return get_topics(session, date=date, category=category, limit=limit)
    finally:
        session.close()


@router.get("/topics/{date}")
def get_digest(date: str):
    session = get_session()
    try:
        return get_daily_digest(session, date)
    finally:
        session.close()
