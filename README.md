# Top 5 YouTube Channels

Small Flask app that looks up and shows the top 5 YouTube channels for a given category/keyword. The app is optimized to reduce YouTube Data API quota usage by using limited `part`/`fields` parameters, caching (in-memory + file), and a fallback demo dataset when the quota is exhausted.

## Features
- JSON API: `/channels/<category>` (returns `{ category, channels, error? }`)
- HTML view: `/view/<category>` (renders `templates/channels.html`) 
- Partial resource requests (`part` + `fields`) to minimize payloads
- Caching: in-memory (fast) and file-based under `.cache/` with TTL (configurable)
- Friendly fallback: when API quota (403) occurs the app will try cached results then return a small demo dataset and a helpful message

## Prerequisites
- Python 3.10+ (project used 3.11/3.13 in dev)
- Git, optional
- A YouTube Data API v3 key (optional for demo; without it you get demo data)

## Quick start (local development)
1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill values (especially `YOUTUBE_API_KEY` if you have one):

```bash
cp .env.example .env
# edit .env and set YOUTUBE_API_KEY and SECRET_KEY
```

4. Run the app (development – hot reload enabled when `FLASK_DEBUG=1` in `.env`):

```bash
# Option A: Flask CLI (reads .env via python-dotenv)
export FLASK_APP=app.py
flask run

# Option B: run directly
python app.py
```

If `FLASK_DEBUG` is set to `1` the app runs with `debug` and the reloader enabled for hot-reload on file save.

## Endpoints / Examples
- JSON API (programmatic):

```bash
curl -sS http://127.0.0.1:5000/channels/music | jq
```

- HTML view (browser):

Open `http://127.0.0.1:5000/view/music`

Responses include a `channels` array and an `error` message when applicable (e.g., cache used, quota fallback).

## Caching & Quota behavior
- In-memory cache keyed by category and a file cache under `.cache/`.
- Cache TTL is controlled by `CACHE_TTL` in `.env` (seconds).
- On a 403/quota error the app first tries to return file-cached data (with an "age" message). If no cache is available the app returns a small demo dataset and the message: `Quota exceeded — using offline/demo data`.

## Notes & Next steps
- Do NOT run with `FLASK_DEBUG=1` in production.
- The code contains two fetching strategies: `get_top_5_channels_by_category` (per-category searches) and `get_top_5_channels_broad` (single broad search + channels.list) — the latter is more quota-efficient.
- Suggested improvements: reduce cognitive complexity in long helper functions, add unit tests (mock API responses), and optionally wire the broad-search as the default route.

## Troubleshooting
- If you see demo data: check `.env` for `YOUTUBE_API_KEY` and quota limits in Google Cloud console.
- If the server doesn't restart on file save: ensure `FLASK_DEBUG=1` (or run `python app.py`) and your editor isn't delaying file writes.

---
