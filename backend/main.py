#FastAPI app exposing backlog and recommendation endpoints.

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fetch_backlog import fetch_owned_games, filter_backlog, resolve_steam_id, STEAM_API_KEY
from enrich import enrich_backlog
from recommend import get_recommendation

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Steam Backlog AI API"}

@app.get("/backlog/{steam_id}")
def get_backlog(steam_id: str):
    try:
        resolved_id = resolve_steam_id(STEAM_API_KEY, steam_id)
        games = fetch_owned_games(STEAM_API_KEY, resolved_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Could not fetch Steam data. Check the username/ID and try again.")

    backlog = filter_backlog(games)
    enriched = enrich_backlog(backlog)
    return {"count": len(enriched), "games": enriched}


class RecommendRequest(BaseModel):
    steam_id: str
    mood: str


@app.post("/recommend")
def recommend(req: RecommendRequest):
    try:
        resolved_id = resolve_steam_id(STEAM_API_KEY, req.steam_id)
        games = fetch_owned_games(STEAM_API_KEY, resolved_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Could not fetch Steam data. Check the username/ID and try again.")

    backlog = filter_backlog(games)
    enriched = enrich_backlog(backlog)

    if not enriched:
        raise HTTPException(status_code=404, detail="No backlog games found for this user.")

    return get_recommendation(req.mood, enriched)