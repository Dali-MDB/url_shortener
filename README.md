# URL shortener API

FastAPI service that stores long URLs, issues short codes, redirects visitors, and records per-visit metadata (including GeoIP city/country when a MaxMind GeoLite2 database is present).

## Stack

- Python 3.12+, FastAPI, Uvicorn  
- SQLAlchemy 2.x + PostgreSQL (connection string compatible with Supabase)  
- GeoIP2 (optional at runtime; requires local `.mmdb` file)

## Prerequisites

- **PostgreSQL** database and a connection URI (`SUPABASE_DB_URL` is just the variable name; any Postgres URL works).  
- **GeoLite2-City** (`.mmdb`): [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) — place `GeoLite2-City.mmdb` under `app/` (see `app/utils.py`) or the app will error when resolving IP location on visits.

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

pip install -r requirements.txt
copy .env.example .env          # then edit .env with your real DATABASE URL
```

Tables are created on startup via SQLAlchemy (`Base.metadata.create_all`).

## Run

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API base: `http://127.0.0.1:8000`  
- Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Docker

```bash
docker build -t url-shortener .
docker run --rm -p 8000:8000 --env-file .env url-shortener
```

Ensure `.env` (or `-e SUPABASE_DB_URL=...`) is supplied so the container can reach Postgres.

## API (quick reference)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/` | JSON body: `{ "url": "https://...", "description": "optional" }` — returns `201` with `code` and `detail`. |
| `GET` | `/links` | List all stored links. |
| `GET` | `/short_codes/?url=...` | List links matching an original URL. |
| `GET` | `/{short_code}` | Redirect to the original URL; records a visit in the background. |
| `GET` | `/stats/shortened/?shortened_url=...` | Stats and visit breakdown for a short code. |
| `DELETE` | `/delete/{shortened_url}` | Delete one short code. |
| `DELETE` | `/delete/original_url/?org_url=...` | Delete all rows for an original URL. |

### curl examples

Default base URL below is `http://127.0.0.1:8000`; replace `YOUR_SHORT_CODE` after creating a link.

**PowerShell**

```powershell
curl.exe -s -X POST "http://127.0.0.1:8000/" -H "Content-Type: application/json" -d '{"url":"https://example.com/page","description":"demo"}'
curl.exe -s "http://127.0.0.1:8000/links"
curl.exe -sI "http://127.0.0.1:8000/YOUR_SHORT_CODE"
curl.exe -s "http://127.0.0.1:8000/stats/shortened/?shortened_url=YOUR_SHORT_CODE"
curl.exe -s -X DELETE "http://127.0.0.1:8000/delete/YOUR_SHORT_CODE"
```

**bash**

```bash
curl -s -X POST "http://127.0.0.1:8000/" -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/page","description":"demo"}'
curl -s "http://127.0.0.1:8000/links"
curl -sI "http://127.0.0.1:8000/YOUR_SHORT_CODE"
curl -s "http://127.0.0.1:8000/stats/shortened/?shortened_url=YOUR_SHORT_CODE"
curl -s -X DELETE "http://127.0.0.1:8000/delete/YOUR_SHORT_CODE"
```

## Environment variables

See `.env.example`. The only required variable for the database layer is **`SUPABASE_DB_URL`** (PostgreSQL URI).

## License / data

GeoLite2 databases are subject to MaxMind’s license; do not commit proprietary `.mmdb` files to a public repo unless your policy allows it.
