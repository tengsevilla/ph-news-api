# ph-news-api

Philippine news scraper and civic impact classifier deployed on Railway as a FastAPI service with a PostgreSQL database.

## What It Does

1. **Scrapes** today's articles from 9 Philippine news and government sources
2. **Classifies** each article using OpenAI `gpt-4.1-mini` — category, sentiment, affected citizen archetypes, and politician impact ratings
3. **Persists** structured data to a PostgreSQL database (topics, politicians, sectors)
4. **Exposes** FastAPI endpoints to trigger scraping and query results

The output powers a gamified civic awareness system where every news event maps to citizen archetypes (Farmer, OFW, Driver, etc.) and tracks whether politicians are helping or hurting ordinary Filipinos over time.

---

## Project Structure

```
ph-news-api/
├── main.py                  # FastAPI app entry point
├── api/
│   ├── routes/
│   │   ├── scrape.py        # POST /scrape endpoint
│   │   ├── topics.py        # GET /topics, /topics/{date}
│   │   ├── politicians.py   # GET /politicians, /politicians/{slug}
│   │   └── sectors.py       # GET /sectors/{slug}
├── scrapers/
│   ├── __init__.py          # ALL_SCRAPERS registry
│   ├── base.py              # RSSBaseScraper, HTMLBaseScraper, RawArticle
│   ├── gma_news.py
│   ├── abs_cbn.py
│   ├── cnn_ph.py
│   ├── inquirer.py
│   ├── philippine_star.py
│   ├── manila_bulletin.py
│   ├── rappler.py
│   ├── senate.py
│   ├── house_of_reps.py
│   └── official_gazette.py
├── classifier/
│   ├── __init__.py
│   ├── client.py            # OpenAI client wrapper
│   └── prompts.py           # Classification prompt templates
├── db/
│   ├── __init__.py
│   ├── connection.py        # SQLAlchemy engine + session
│   ├── models.py            # ORM models
│   └── repositories.py     # DB read/write helpers
├── services/
│   └── pipeline.py          # Orchestrates scrape → classify → persist
├── requirements.txt
├── Procfile                 # web: uvicorn main:app --host 0.0.0.0 --port $PORT
├── railway.toml
└── .env.example
```

---

## Running Locally

```bash
pip install -r requirements.txt

# Copy and fill in env vars
cp .env.example .env

# Start the API server
uvicorn main:app --reload --port 8000

# Trigger a scrape via curl
curl -X POST http://localhost:8000/scrape

# Dry-run (classifies but does not write to DB)
curl -X POST "http://localhost:8000/scrape?dry_run=true"
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/scrape` | Run full pipeline: scrape → classify → persist |
| `POST` | `/scrape?dry_run=true` | Run pipeline, return JSON, skip DB writes |
| `GET` | `/topics` | List topics (query params: `date`, `category`, `limit`) |
| `GET` | `/topics/{date}` | Full daily digest for a given date (`YYYY-MM-DD`) |
| `GET` | `/politicians` | List all politicians ordered by impact score |
| `GET` | `/politicians/{slug}` | Politician profile + full impact history |
| `GET` | `/sectors/{slug}` | Recent articles for a citizen archetype |
| `GET` | `/health` | Health check — returns `{"status": "ok"}` |

### POST /scrape response shape

```json
{
  "date": "2026-05-17",
  "scraped_at": "2026-05-17T16:00:00Z",
  "raw_article_count": 87,
  "topic_count": 34,
  "dry_run": false
}
```

---

## Credentials / Environment Variables

Set these in the Railway dashboard (or `.env` for local dev):

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `DATABASE_URL` | PostgreSQL connection string — Railway injects this automatically when a Postgres plugin is attached |
| `SCRAPE_SECRET` | Optional bearer token to protect `POST /scrape` from unauthorized calls |

`.env.example`:
```
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname
SCRAPE_SECRET=your-secret-token
```

Railway sets `DATABASE_URL` automatically when you add a Postgres plugin to the project. Use `postgresql+psycopg2://` as the SQLAlchemy driver prefix.

---

## Database Schema

Use SQLAlchemy ORM models. Run `db/init_db.py` once to create all tables (or use Alembic for migrations).

### `daily_digests`
| Column | Type | Notes |
|--------|------|-------|
| `id` | INT PK | |
| `date` | DATE UNIQUE | |
| `scraped_at` | DATETIME | |
| `raw_article_count` | INT | |
| `topic_count` | INT | |

### `topics`
| Column | Type | Notes |
|--------|------|-------|
| `id` | VARCHAR(36) PK | UUID |
| `digest_date` | DATE FK → daily_digests.date | |
| `topic` | TEXT | Deduplicated headline |
| `summary` | TEXT | |
| `category` | VARCHAR(50) | |
| `sentiment` | VARCHAR(20) | positive/negative/neutral |
| `impact_level` | VARCHAR(20) | national/regional/local |
| `event_type` | VARCHAR(50) | |
| `severity` | TINYINT | 1–5 |
| `affected_population_estimate` | VARCHAR(30) | |
| `created_at` | DATETIME | |

### `topic_sources`
| Column | Type | Notes |
|--------|------|-------|
| `id` | INT PK | |
| `topic_id` | VARCHAR(36) FK → topics.id | |
| `source` | VARCHAR(50) | e.g. `gma_news` |
| `url` | TEXT | |
| `title` | TEXT | |
| `published_at` | DATETIME | |

### `topic_sectors`
| Column | Type | Notes |
|--------|------|-------|
| `topic_id` | VARCHAR(36) FK | |
| `sector_slug` | VARCHAR(50) | |
| PK | composite (topic_id, sector_slug) | |

### `politicians`
| Column | Type | Notes |
|--------|------|-------|
| `slug` | VARCHAR(100) PK | kebab-case name |
| `name` | VARCHAR(200) | |
| `position` | VARCHAR(100) | |
| `party` | VARCHAR(100) | |
| `branch` | VARCHAR(30) | legislative/executive/local |
| `positive_count` | INT | |
| `negative_count` | INT | |
| `neutral_count` | INT | |
| `impact_score` | FLOAT | (positive − negative) / total |
| `last_updated` | DATETIME | |

### `politician_impact_history`
| Column | Type | Notes |
|--------|------|-------|
| `id` | INT PK | |
| `politician_slug` | VARCHAR(100) FK → politicians.slug | |
| `topic_id` | VARCHAR(36) FK → topics.id | |
| `impact` | VARCHAR(20) | positive/negative/neutral |
| `reason` | TEXT | |
| `date` | DATE | |

---

## Classifier

Articles are classified in batches of 10 using **OpenAI `gpt-4.1-mini`**.

Use `response_format={"type": "json_object"}` for reliable structured output.

Each classification returns:
- `category` — politics, economy, health, weather, crime, education, environment, disaster, international, sports, technology, or social
- `sentiment` — positive / negative / neutral (from Filipino citizens' perspective)
- `impact_level` — national / regional / local
- `affected_sectors` — list of sector slugs from the 35-archetype list
- `politicians` — list of mentioned politicians with impact rating and one-sentence reason
- `gamification` — event type, severity (1–5), and affected population estimate

---

## Citizen Archetypes (Sector Slugs)

These are the 35 citizen base classes used in gamification. Each news event can affect one or more.

### Agriculture & Natural Resources
| Slug | Label |
|------|-------|
| `farmer` | Farmer |
| `fisherman` | Fisherman |
| `miner` | Miner |
| `forest_worker` | Forest Worker |

### Health & Social Services
| Slug | Label |
|------|-------|
| `health_worker` | Health Worker |
| `social_worker` | Social Worker |
| `senior_citizen` | Senior Citizen |
| `pwd` | Person with Disability |

### Education
| Slug | Label |
|------|-------|
| `teacher` | Teacher |
| `student` | Student |

### Labor & Employment
| Slug | Label |
|------|-------|
| `labor_worker` | Labor Worker |
| `kasambahay` | Kasambahay |
| `security_guard` | Security Guard |
| `bpo_worker` | BPO / Call Center Worker |
| `retail_worker` | Retail Worker |
| `hospitality_worker` | Hospitality Worker |

### Transport & Logistics
| Slug | Label |
|------|-------|
| `driver` | Driver |
| `seafarer` | Seafarer |
| `delivery_rider` | Delivery Rider |

### Business & Economy
| Slug | Label |
|------|-------|
| `business_owner` | Business Owner |
| `vendor` | Vendor / Tindera |
| `freelancer` | Freelancer |

### Overseas Workers
| Slug | Label |
|------|-------|
| `ofw` | OFW |

### Government & Public Service
| Slug | Label |
|------|-------|
| `government_employee` | Gov't Employee |
| `barangay_official` | Barangay Official |
| `military_police` | Military / Police |

### Professionals
| Slug | Label |
|------|-------|
| `engineer_architect` | Engineer / Architect |
| `lawyer` | Lawyer |
| `journalist` | Journalist |
| `it_tech_worker` | IT / Tech Worker |
| `artist_creative` | Artist / Creative |

### Vulnerable & Marginalized Groups
| Slug | Label |
|------|-------|
| `solo_parent` | Solo Parent |
| `informal_settler` | Informal Settler |
| `indigenous_people` | Indigenous People |
| `youth` | Youth / NEET |
| `lgbtq` | LGBTQ+ |
| `prisoner_returnee` | Prisoner / Returnee |

---

## News Sources

| Source | Type | What Is Scraped |
|--------|------|-----------------|
| GMA News | RSS | Top stories, nation, economy |
| ABS-CBN News | RSS | News headlines |
| CNN Philippines | RSS | Headlines |
| Philippine Daily Inquirer | RSS | Top stories, news |
| Philippine Star | RSS | Headlines, nation |
| Manila Bulletin | RSS | Latest headlines |
| Rappler | RSS | Nation, business, accountability journalism |
| Senate of the Philippines | HTML | Press releases, bills filed |
| House of Representatives | HTML | News releases |
| Official Gazette | RSS | Executive orders, proclamations |

---

## Adding a New Scraper

### RSS source (preferred)

1. Create `scrapers/your_source.py`:

```python
from scrapers.base import RSSBaseScraper

class YourSourceScraper(RSSBaseScraper):
    SOURCE_NAME = "your_source"
    FEED_URLS = [
        "https://yoursource.com/feed/",
        "https://yoursource.com/category/news/feed/",
    ]
```

2. Register in `scrapers/__init__.py`:

```python
from .your_source import YourSourceScraper

ALL_SCRAPERS = [..., YourSourceScraper]
```

### HTML source

Extend `HTMLBaseScraper` and implement `fetch()`. Use `self._get(url)` which returns a `BeautifulSoup` object. Return a list of `RawArticle` objects.

---

## Railway Deployment

### railway.toml

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
```

### Daily Cron Trigger

Railway does not have a native cron scheduler. Use one of:

1. **Railway Cron plugin** (if available in your plan) — set cron to `0 16 * * *` (midnight PHT = 16:00 UTC), calling `POST /scrape`.
2. **External cron service** (e.g., cron-job.org, Render Cron) — hit `POST /scrape` with the `Authorization: Bearer <SCRAPE_SECRET>` header.

The `SCRAPE_SECRET` env var guards the endpoint so only the cron caller can trigger a run.

---

## Politician Profiles

Each politician mentioned across all articles accumulates an impact history in the `politicians` and `politician_impact_history` tables.

`impact_score` = (positive − negative) / total, ranging from −1.0 to +1.0.

`GET /politicians/{slug}` response shape:

```json
{
  "slug": "juan-dela-cruz",
  "name": "Juan Dela Cruz",
  "position": "Senator",
  "party": "PDP-Laban",
  "branch": "legislative",
  "positive_count": 12,
  "negative_count": 5,
  "neutral_count": 3,
  "impact_score": 0.35,
  "last_updated": "2026-05-17T16:00:00Z",
  "impact_history": [
    {
      "topic_id": "uuid",
      "topic": "Senate Passes Anti-ENDO Bill",
      "impact": "positive",
      "reason": "Authored and championed the security of tenure bill for workers.",
      "date": "2026-05-17"
    }
  ]
}
```

---

## Schedule

Daily scrape runs at **midnight Philippine time (UTC+8 = 16:00 UTC)** via an external cron service calling `POST /scrape`.

Reference cron expression: `0 16 * * *`
