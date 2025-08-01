import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [searchTerm, setSearchTerm] = useState("");
  const [animeList, setAnimeList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState("default");
  const [selectedAnime, setSelectedAnime] = useState(null); // <-- detail page state

  useEffect(() => {
    if (!searchTerm) return;

    async function fetchAnime() {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `http://localhost:4000/api/anime?q=${encodeURIComponent(searchTerm)}`
        );
        if (!response.ok) throw new Error("Network response was not ok");
        const data = await response.json();

        let results = data.data;
        if (sortBy === "rank") {
          results = [...results].sort(
            (a, b) => (a.node.rank || 99999) - (b.node.rank || 99999)
          );
        } else if (sortBy === "year") {
          results = [...results].sort((a, b) => {
            const yearA = new Date(a.node.start_date || "1900").getFullYear();
            const yearB = new Date(b.node.start_date || "1900").getFullYear();
            return yearB - yearA;
          });
        }

        setAnimeList(results);
      } catch (err) {
        setError("Error fetching data");
      } finally {
        setLoading(false);
      }
    }

    fetchAnime();
  }, [searchTerm, sortBy]);

  // Show detail page if selectedAnime is set
  if (selectedAnime) {
    const node = selectedAnime.node;
    return (
      <div className="app-container">
        <button
          onClick={() => setSelectedAnime(null)}
          style={{
            marginBottom: 20,
            padding: "10px 15px",
            backgroundColor: "#e50914",
            color: "white",
            border: "none",
            borderRadius: 5,
            cursor: "pointer",
          }}
        >
          ← Back to results
        </button>

        <div className="detail-container">
          <h2>{node.title}</h2>
          {node.main_picture && (
            <img
              src={node.main_picture.large}
              alt={node.title}
              className="detail-image"
            />
          )}

          <p><strong>Rank:</strong> {node.rank || "N/A"}</p>
          <p>
            <strong>Year:</strong>{" "}
            {node.start_date ? new Date(node.start_date).getFullYear() : "N/A"}
          </p>
          <p>
            <strong>Genres:</strong>{" "}
            {(node.genres || [])
              .map((g) => (typeof g === "string" ? g : g.name))
              .join(", ")}
          </p>
          <p><strong>Description:</strong></p>
          <p>{node.synopsis || "No description available."}</p>
        </div>
      </div>
    );
  }

  // Default list view
  return (
    <div className="app-container">
      <h1>🎬 AnimeFlix</h1>

      <div className="controls" style={{ marginBottom: "30px" }}>
        <input
          type="text"
          placeholder="Search anime..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ padding: "12px", fontSize: "16px", width: "320px" }}
        />
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          style={{ marginLeft: "12px", padding: "12px", fontSize: "16px" }}
        >
          <option value="default">Sort by</option>
          <option value="rank">Top Rank</option>
          <option value="year">Release Year</option>
        </select>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      <div className="anime-list">
        {animeList?.map(({ node }) => (
          <div
            key={node.id}
            className="anime-card"
            onClick={() => setSelectedAnime({ node })}
            style={{ cursor: "pointer" }}
          >
            {node.main_picture && (
              <img
                src={node.main_picture.large}
                alt={node.title}
                className="anime-image"
              />
            )}

            <div className="anime-overlay">
              <h3 className="anime-title">{node.title}</h3>
              {node.rank && <p>🏆 Rank: {node.rank}</p>}
              {node.start_date && (
                <p>📅 Year: {new Date(node.start_date).getFullYear()}</p>
              )}
              <div className="anime-genres">
                {(node.genres || []).slice(0, 3).map((genre, i) => (
                  <span key={i} className="genre-tag">
                    {typeof genre === "string" ? genre : genre.name}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
