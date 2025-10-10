import React, { useState, useEffect } from 'react';
import './index.css';
import ReceiptGenerator from './ReceiptGenerator';

export default function App() {
  const [summaries, setSummaries] = useState([]);
  const [filename, setFilename] = useState('');
  const [spotifySummary, setSpotifySummary] = useState({});
  const [uploadError, setUploadError] = useState(null);
  const [loading, setLoading] = useState(false);
  const API_BASE = import.meta.env.VITE_API_BASE_URL || window.location.origin;

  async function fetchLastSummary() {
    try {
      const res = await fetch(`${API_BASE}api/last-summary`, {
        credentials: 'include',
      });
      if (!res.ok) return; // no summary yet is fine
      const data = await res.json();
      setFilename(data.filename || '');
      setSummaries(data.summaries || []);
      setSpotifySummary(data.spotify_summary || {});
    } catch (err) {
      console.error('Error fetching last summary:', err);
    }
  }

  // --- detect redirect from Spotify callback and/or hydrate on first load
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const cameFromSpotify = params.has('spotify');
    fetchLastSummary(); // hydrate regardless (works if user already uploaded/logged in)

    // clean the URL if we had the spotify flag
    if (cameFromSpotify) {
      params.delete('spotify');
      const search = params.toString();
      const clean = `${window.location.pathname}${search ? `?${search}` : ''}`;
      window.history.replaceState({}, '', clean);
    }
  }, []);

  // handle upload → saves into Flask session, then re-hydrate
  async function handleUpload(e) {
    e.preventDefault();
    const fileInput = e.target.elements.file;
    if (!fileInput.files?.length) return;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
      setLoading(true);
      setUploadError(null);

      const uploadRes = await fetch(`${API_BASE}upload`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });

      if (!uploadRes.ok) {
        throw new Error(`Upload failed: ${uploadRes.status}`);
      }

      // after upload, pull the combined state (filename+summaries+spotify_summary)
      await fetchLastSummary();
    } catch (err) {
      console.error('Upload error:', err);
      setUploadError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // send the user into the OAuth flow; Flask will redirect back to /?spotify=1
  const handleSpotifyLogin = () => {
    window.location.href = `${API_BASE}/auth/login`;
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
          <button type="submit" disabled={loading}>
            {loading ? 'Uploading…' : 'Generate Receipts'}
          </button>
        </form>
        {uploadError && <p style={{ color: 'red' }}>Error: {uploadError}</p>}
      </section>

      {filename && <p>Uploaded file: {filename}</p>}

      <section>
        <h2>Spotify Listening Summary</h2>
        {!Object.keys(spotifySummary).length ? (
          <button type="button" onClick={handleSpotifyLogin}>
            Log in with Spotify
          </button>
        ) : (
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
