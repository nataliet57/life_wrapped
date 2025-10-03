import React, { useState } from 'react';
import './index.css';
import ReceiptGenerator from './ReceiptGenerator';

export default function App() {
  const [summaries, setSummaries] = useState([]);
  const [filename, setFilename] = useState('');
  const [spotifySummary, setSpotifySummary] = useState(null);
  const [spotifyStatus, setSpotifyStatus] = useState('idle');
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  async function fetchAll(e) {
    e.preventDefault();
    const fileInput = e.target.elements.file;
    if (!fileInput.files?.length) return;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
      const [uploadRes, spotifyRes] = await Promise.all([
        fetch('http://127.0.0.1:5000/upload', {
          method: 'POST',
          body: formData,
          credentials: 'include',
        }),
        fetch('http://127.0.0.1:5000/api/summary', {
          credentials: 'include',
        }),
      ]);

      // handle upload result
      if (!uploadRes.ok) {
        console.log(uploadRes.status);
        throw new Error('failed upload');
      }
      const uploadData = await uploadRes.json();
      setFilename(uploadData.filename);
      setSummaries(uploadData.summaries);

      // handle spotify result
      if (spotifyRes.status === 401) {
        setSpotifyStatus('unauthenticated');
        setSpotifySummary(null);
        return;
      }
      if (!spotifyRes.ok) {
        setSpotifyStatus('error');
        return;
      }
      const spotifyData = await spotifyRes.json();
      setSpotifySummary(spotifyData.spotify_summary || {});
      setSpotifyStatus('authenticated');
    } catch (err) {
      console.error('failed to fetch', err);
      setUploadError(err.message);
    }
  }

  const handleSpotifyLogin = () => {
    window.location.href = 'http://127.0.0.1:5000/auth/login';
  };

  return (
    <main>
      <header>
        <h1>Life Wrapped</h1>
        <p id="home_header">Your month-to-month life highlights</p>
      </header>

      <section>
        <button type="button" onClick={handleSpotifyLogin}>
          Log in with Spotify
        </button>

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

      <section className="customize" aria-labelledby="customize-title">
        <h2 id="customize-title" className="customize-header">
          Upload Excel
        </h2>
        <form onSubmit={fetchAll}>
          <input type="file" name="file" accept=".xlsx" />
          <button type="submit">Generate Receipts</button>
        </form>
      </section>

      {filename && <p>Uploaded file: {filename}</p>}
      {uploadError && <p style={{ color: 'red' }}>Error: {uploadError}</p>}

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
        <ul>
          {/* {Object.entries(spotifySummary).map(([month, info]) => (
            <li key={month}>
              {month}: {info.track} ({info.plays} plays)
            </li>
          ))} */}
        </ul>

      </section>
    </main>
  );
}
