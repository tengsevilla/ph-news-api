from fastapi import APIRouter, Query

from db.connection import get_session
from db.repositories import get_sector_topics

router = APIRouter()


@router.get("/sectors/{slug}")
def get_sector(slug: str, limit: int = Query(20, le=100)):
    session = get_session()
    try:
        return get_sector_topics(session, slug, limit=limit)
    finally:
        session.close()
