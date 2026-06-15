#Fetch a Steam user's game library and filter it down to their backlog

import os

import requests
from dotenv import load_dotenv

load_dotenv()  # reads .env in the project root

STEAM_API_KEY = os.getenv("STEAM_API_KEY")
STEAM_USER_ID = os.getenv("STEAM_USER_ID")  # your 17-digit SteamID64

BACKLOG_THRESHOLD_MINUTES = 120  # under 2 hours played = backlog

API_URL = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"


def fetch_owned_games(api_key: str, steam_id: str) -> list[dict]:
    #Return the user's owned games, or raise a helpful error
    params = {
        "key": api_key,
        "steamid": steam_id,
        "include_appinfo": 1,        # include game names, not just app IDs
        "include_played_free_games": 1,
    }
    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()

    data = response.json().get("response", {})

    # An empty response usually means the profile is private
    if "games" not in data:
        raise ValueError(
            "No games returned. Check that your profile's 'Game details' "
            "privacy setting is Public and your SteamID64 is correct."
        )
    return data["games"]


def filter_backlog(games: list[dict], threshold: int = BACKLOG_THRESHOLD_MINUTES) -> list[dict]:
    #Keep only games with playtime under the threshold (in minutes)
    return [g for g in games if g.get("playtime_forever", 0) < threshold]


def main() -> None:
    if not STEAM_API_KEY or not STEAM_USER_ID:
        raise SystemExit("Missing STEAM_API_KEY or STEAM_USER_ID in your .env file.")

    games = fetch_owned_games(STEAM_API_KEY, STEAM_USER_ID)
    backlog = filter_backlog(games)

    # Sort by playtime so 'never touched' games appear first
    backlog.sort(key=lambda g: g.get("playtime_forever", 0))

    print(f"Total games owned: {len(games)}")
    print(f"Backlog (< {BACKLOG_THRESHOLD_MINUTES} min played): {len(backlog)}\n")

    for game in backlog:
        minutes = game.get("playtime_forever", 0)
        print(f"  {game['name']:<50} {minutes:>5} min")


if __name__ == "__main__":
    main()