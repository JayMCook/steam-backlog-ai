# Steam Backlog Recommender

An AI-powered tool that looks at your Steam backlog — the games you own but haven't really played — and recommends what to play next based on your current mood.

## How it works

1. **Fetch** — Pulls your owned games library from the Steam Web API using your SteamID or Steam username.
2. **Filter** — Identifies your "backlog": games with under 2 hours of playtime.
3. **Enrich** — Fetches genre and description metadata for each backlog game from the Steam Store API, with local caching to avoid redundant requests.
4. **Recommend** — Sends your backlog (trimmed to relevant fields) and your mood description to Claude, which returns a top recommendation plus two runner-ups, each with reasoning, as structured JSON.

```
React frontend → FastAPI backend → Steam Web API (library)
                                  → Steam Store API (genres/descriptions, cached)
                                  → Anthropic API (recommendation reasoning)
```

## Tech stack

- **Backend:** Python, FastAPI
- **Frontend:** React (Vite)
- **LLM:** Anthropic Claude API
- **Data sources:** Steam Web API, Steam Store API

## Running locally

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:

```
STEAM_API_KEY=your_steam_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

Run the server:

```bash
uvicorn main:app --reload
```

API docs available at `http://127.0.0.1:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`.

## Usage

Enter your Steam username (if your profile has a custom URL) or your SteamID64, describe what you're in the mood to play, and get a recommendation pulled from games already sitting in your library.

**Note:** Your Steam profile's "Game details" privacy setting must be set to **Public** (Steam → Edit Profile → Privacy Settings) for the app to read your library.

## Design notes

**Why filter by playtime instead of a manual "backlog" list?** Most people don't maintain a curated backlog — their library *is* their backlog. Using `playtime_forever < 120 minutes` as a heuristic captures "owned but never really played" without requiring any extra input from the user.

**Why cache Store API metadata?** The Steam Store API is unofficial, rate-limited, and game metadata (genres, descriptions) never changes. Caching by app ID means the first lookup for any game is the only slow one — ever, across all users — and repeat requests are near-instant.

**Why structured JSON output from the LLM?** Asking Claude to return `{"recommendation": {...}, "runner_ups": [...]}` rather than free-form text means the response can be rendered directly into UI components (cards, images via Steam's header CDN) without additional parsing logic.

## Known limitations & future improvements

- **File-based cache** — game metadata is cached to a local JSON file rather than a database. This is simple and effective for a project at this scale, but doesn't persist across redeploys on most hosting platforms. A natural next step would be Postgres or Redis for persistent, shared caching.
- **Synchronous enrichment** — on a cold cache, fetching metadata for an uncached backlog happens sequentially with rate-limit delays, so first-time requests for large libraries can take up to a minute. Async/concurrent fetching with a bounded worker pool would speed this up significantly.
- **Steam privacy requirement** — the app can only read libraries where "Game details" is set to Public. This is a Steam API constraint, not something the app can work around.
- **Vanity URL dependency** — usernames only resolve if the user has set a custom Steam profile URL. Users without one must use their SteamID64.

## Project structure

```
backend/
  main.py            # FastAPI app and routes
  fetch_backlog.py   # Steam Web API integration, ID resolution, backlog filtering
  enrich.py          # Steam Store API integration with caching
  recommend.py       # LLM prompt construction and recommendation logic
  cache/             # Local metadata cache (gitignored)
frontend/
  src/App.jsx        # Main UI component
  src/App.css        # Styling
```