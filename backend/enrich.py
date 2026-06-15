#Enrich a Steam backlog with genre and description metadata, with local caching

import json
import os
import time

import requests

from fetch_backlog import fetch_owned_games, filter_backlog, STEAM_API_KEY, STEAM_USER_ID

CACHE_PATH = "cache/game_metadata.json"
STORE_API_URL = "https://store.steampowered.com/api/appdetails"


def load_cache() -> dict:
    if not os.path.exists(CACHE_PATH):
        return {}
    with open(CACHE_PATH, "r") as f:
        content = f.read().strip()
        if not content:
            return {}
        return json.loads(content)


def save_cache(cache: dict) -> None:
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


def fetch_game_details(appid: int) -> dict | None:
    try:
        params = {"appids": appid}
        response = requests.get(STORE_API_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if not data:
            return None

        entry = data.get(str(appid), {})
        if not entry.get("success"):
            return None

        details = entry["data"]
        return {
            "genres": [g["description"] for g in details.get("genres", [])],
            "description": details.get("short_description", ""),
            "appid": appid
        }
    except (requests.RequestException, ValueError) as e:
        print(f"  ⚠ Error fetching appid {appid}: {e}")
        return None


def enrich_backlog(backlog: list[dict]) -> list[dict]:
    cache = load_cache()
    enriched = []

    for i, game in enumerate(backlog, start=1):
        appid = game["appid"]
        key = str(appid)

        if key in cache:
            details = cache[key]
            status = "cached"
        else:
            details = fetch_game_details(appid)
            cache[key] = details
            save_cache(cache)
            time.sleep(1)
            status = "fetched" if details else "skipped (no data)"
            if details is None:
                time.sleep(3)  # extra cooldown after a failure, in case it was a rate limit

        print(f"[{i}/{len(backlog)}] {game['name']} ({status})")

        enriched.append({
            **game,
            "genres": details["genres"] if details else [],
            "description": details["description"] if details else "",
        })

    return enriched


def main() -> None:
    games = fetch_owned_games(STEAM_API_KEY, STEAM_USER_ID)
    backlog = filter_backlog(games)

    enriched = enrich_backlog(backlog)

    with open("cache/enriched_backlog.json", "w") as f:
        json.dump(enriched, f, indent=2)

    print(f"\nDone. Saved {len(enriched)} games to cache/enriched_backlog.json")


if __name__ == "__main__":
    main()