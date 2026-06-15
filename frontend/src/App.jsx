import { useState } from 'react'
import steamLogo from './assets/steamlogo.png'

import './App.css'

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [count, setCount] = useState(0)
  const [steamId, setSteamId] = useState("");
  const [mood, setMood] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ steam_id: steamId, mood: mood }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Something went wrong");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <h1>Steam Backlog Recommender</h1>

      <p>Before using this app, make sure your Steam profile's 'Game details' privacy setting is Public. If your steam account lacks a custom URL, use your SteamID64 instead, which is the number at the end of your Steam profile URL.</p>

      <form onSubmit={handleSubmit}>
        <input
          value={steamId}
          onChange={(e) => setSteamId(e.target.value)}
          placeholder="Enter Steam Account Name or ID"
        />
        <textarea
          value={mood}
          onChange={(e) => setMood(e.target.value)}
          onInput={(e) => {
            e.target.style.height = "auto";
            e.target.style.height = e.target.scrollHeight + "px";
          }}
          placeholder="What are you in the mood for?"
          rows={1}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Thinking..." : "Show Me What to Play!"}
        </button>
        <p hidden={!loading} className="loading-indicator">Fetching your backlog and game details — this can take up to a minute the first time, since we're pulling fresh data from Steam for each game.</p>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result">
          <div className="recommendation-card">
            <img
              src={`https://cdn.akamai.steamstatic.com/steam/apps/${result.recommendation.appid}/header.jpg`}
              alt={result.recommendation.name}
            />
            <div className="recommendation-text">
              <h2>{result.recommendation.name}</h2>
              <p>{result.recommendation.reasoning}</p>
            </div>
          </div>
          <div className="runner-ups">
            {result.runner_ups.map((game) => (
              <div className="recommendation-card" key={game.appid}>
                <img
                  src={`https://cdn.akamai.steamstatic.com/steam/apps/${game.appid}/header.jpg`}
                  alt={game.name}
                />
                <div className="recommendation-text">
                  <h2>{game.name}</h2>
                  <p>{game.reasoning}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App