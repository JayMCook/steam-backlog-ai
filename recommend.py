#Generate a game recommendation from the enriched backlog using an LLM

import json
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a game recommendation assistant. You will be given a 
user's backlog of unplayed Steam games and a description of what they're in the 
mood for. Recommend ONE game as the top pick, plus two runner-ups.

Respond with ONLY valid JSON in this exact format, no other text:
{
  "recommendation": {"appid": 12345, "name": "Game Name", "reasoning": "1-2 sentence explanation of why this game fulfills the user's mood"},
  "runner_ups": [
    {"appid": 12345, "name": "Game Name", "reasoning": "..."},
    {"appid": 12345, "name": "Game Name", "reasoning": "..."}
  ]
}"""


def load_enriched_backlog() -> list[dict]:
    with open("cache/enriched_backlog.json", "r") as f:
        return json.load(f)


def build_game_summary(backlog: list[dict]) -> list[dict]:
    #Trim each game down to just what the LLM needs
    return [
        {
            "name": g["name"],
            "appid": g["appid"],
            "genres": g.get("genres", []),
            "description": g.get("description", ""),
        }
        for g in backlog
    ]


def get_recommendation(mood: str, backlog: list[dict]) -> dict:
    games_summary = build_game_summary(backlog)

    user_message = (
        f"My mood: {mood}\n\n"
        f"My backlog:\n{json.dumps(games_summary, indent=2)}"
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = response.content[0].text.strip()

    # Strip markdown code fences if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]  # remove first line (```json)
        raw_text = raw_text.rsplit("```", 1)[0]  # remove trailing ```
        raw_text = raw_text.strip()

    return json.loads(raw_text)


def main() -> None:
    backlog = load_enriched_backlog()

    mood = input("What are you in the mood for? ")

    result = get_recommendation(mood, backlog)

    print("\n--- Recommendation ---")
    print(f"{result['recommendation']['name']}")
    print(f"  {result['recommendation']['reasoning']}\n")

    print("Runner-ups:")
    for ru in result["runner_ups"]:
        print(f"  {ru['name']} — {ru['reasoning']}")


if __name__ == "__main__":
    main()