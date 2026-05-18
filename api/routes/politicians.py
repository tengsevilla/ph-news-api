from fastapi import APIRouter, HTTPException

from db.connection import get_session
from db.repositories import list_politicians, get_politician_profile

router = APIRouter()


@router.get("/politicians")
def list_all():
    session = get_session()
    try:
        return list_politicians(session)
    finally:
        session.close()


@router.get("/politicians/{slug}")
def get_politician(slug: str):
    session = get_session()
    try:
        result = get_politician_profile(session, slug)
        if not result:
            raise HTTPException(status_code=404, detail="Politician not found")
        return result
    finally:
        session.close()
