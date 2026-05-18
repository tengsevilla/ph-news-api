"""Run once to create all database tables."""
from dotenv import load_dotenv

load_dotenv()

from db.connection import get_engine
from db.models import Base


def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("All tables created.")


if __name__ == "__main__":
    init_db()
