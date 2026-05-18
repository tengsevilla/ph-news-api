import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from api.routes import scrape, topics, politicians, sectors

_REQUIRED_ENV = ["OPENAI_API_KEY", "DATABASE_URL"]
_missing = [v for v in _REQUIRED_ENV if not os.environ.get(v)]
if _missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(_missing)}")

app = FastAPI(title="ph-news-api", description="Philippine news scraper and civic impact classifier")

app.include_router(scrape.router)
app.include_router(topics.router)
app.include_router(politicians.router)
app.include_router(sectors.router)


@app.get("/health")
def health():
    return {"status": "ok"}
