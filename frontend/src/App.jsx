import React, { useEffect, useState } from 'react';
import './index.css';
import ReceiptGenerator from './ReceiptGenerator';

export default function App() {
  const [summaries, setSummaries] = useState([]);
  const [filename, setFilename] = useState("");
  const [spotifySummary, setSpotifySummary] = useState(null);
  const [spotifyStatus, setSpotifyStatus] = useState('idle');

  async function handleUpload(e) {
    e.preventDefault();
    const fileInput = e.target.elements.file;
    if (!fileInput.files?.length) return;

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
      const res = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
        credentials: 'include',
      });
      console.log("status", res.status);
      const json = await res.json();
      console.log(json)
      setFilename(json.filename);
      setSummaries(json.summaries);
    } catch (err) {
      console.error("fetch failed", err);
    }
  }
  
  useEffect(() => {
    async function fetchSpotifySummary() {
      setSpotifyStatus('loading');
      try {
        const res = await fetch('http://127.0.0.1:5000/api/summary', {
          credentials: 'include',
        });

        if (res.status === 401) {
          setSpotifyStatus('unauthenticated');
          setSpotifySummary(null);
          return;
        }

        if (!res.ok) {
          setSpotifyStatus('error');
          return;
        }

        const data = await res.json();
        setSpotifySummary(data.spotify_summary || {});
        setSpotifyStatus('authenticated');
      } catch (error) {
        console.error('Failed to load Spotify summary', error);
        setSpotifyStatus('error');
      }
    }

    fetchSpotifySummary();
  }, []);

  const handleSpotifyLogin = () => {
    window.location.href = 'http://127.0.0.1:5000/auth/login';
  };

  return (
    <main>
      <header>
        <h1>Life Wrapped</h1>
        <p id="home_header">Your month-to-month life highlights</p>
      </header>

      <section className="customize" aria-labelledby="customize-title">
        <h2 id="customize-title" className="customize-header">
          Upload Excel
        </h2>
        <form onSubmit={handleUpload}>
          <input type="file" name="file" accept=".xlsx" />
          <button type="submit">Generate Receipts</button>
        </form>
      </section>

      {filename && <p>Uploaded file: {filename}</p>}

      <section>
        <h2>Spotify Listening Summary</h2>
        {spotifyStatus === 'loading' && <p>Loading Spotify data…</p>}
        {spotifyStatus === 'unauthenticated' && (
          <button type="button" onClick={handleSpotifyLogin}>
            Sign in with Spotify
          </button>
        )}
        {spotifyStatus === 'error' && (
          <p>Could not load Spotify data. Try again later.</p>
        )}
        {spotifyStatus === 'authenticated' && spotifySummary && (
          <ul>
            {Object.entries(spotifySummary).map(([month, info]) => (
              <li key={month}>
                {month}: {info.track} ({info.plays} plays)
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
      {summaries.map((summary, i) => (
        <ReceiptGenerator
          key={i}
          summary={summary}
          title={`${summary.month_name} ${summary.year}`}
        />
      ))}
    </section>
    </main>
  );
}
