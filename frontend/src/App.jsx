import React, { useState, useEffect, useMemo } from 'react';
import './index.css';
import ReceiptGenerator from './ReceiptGenerator';
import SpotifySummary from './SpotifySummary';

export default function App() {
  const [summaries, setSummaries] = useState([]);
  const [filename, setFilename] = useState('');
  const [spotifySummary, setSpotifySummary] = useState([]);
  const [heatmaps, setHeatmaps] = useState([]);
  const [uploadError, setUploadError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState('last_month');
  const API_BASE = import.meta.env.VITE_API_BASE_URL || window.location.origin;

  async function fetchSpotifySummary() {
    try {
      const res = await fetch(`${API_BASE}api/summary`, { credentials: 'include' });
      if (!res.ok) return;
      const data = await res.json();
      console.log('Fetched Spotify summary:', data);
      setSpotifySummary(
        Array.isArray(data.spotify_summary) ? data.spotify_summary : []
      );
    } catch (err) {
      console.error('Error fetching Spotify summary:', err);
    }
  }

  async function fetchLastSummary() {
    try {
      const res = await fetch(`${API_BASE}api/last-summary`, {
        credentials: 'include',
      });
      if (!res.ok) {
        if (res.status === 404) {
          setFilename('');
          setSummaries([]);
          setHeatmaps([]);
        }
        return; // no summary yet is fine
      }
      const data = await res.json();
      setFilename(data.filename || '');
      setSummaries(data.summaries || []);
      setSpotifySummary(
        Array.isArray(data.spotify_summary) ? data.spotify_summary : []
      );
      setHeatmaps(Array.isArray(data.heatmaps) ? data.heatmaps : []);
    } catch (err) {
      console.error('Error fetching last summary:', err);
    }
  }

  // --- detect redirect from Spotify callback and/or hydrate on first load
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const cameFromSpotify = params.has('spotify');
    fetchSpotifySummary();
    fetchLastSummary();

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
    window.location.href = `${API_BASE}auth/login`;
  };

  const displayedSummaries = useMemo(() => {
    if (!summaries.length) return [];
    const count = timeRange === 'last_three_months' ? 3 : 1;
    return summaries.slice(-count);
  }, [summaries, timeRange]);

  const displayedHeatmaps = useMemo(() => {
    if (!heatmaps.length || !displayedSummaries.length) return [];
    const summaryKeys = new Set(
      displayedSummaries.map(
        (summary) => `${summary.month_name}-${summary.year}`
      )
    );
    return heatmaps.filter(
      ({ month, year }) => summaryKeys.has(`${month}-${year}`)
    );
  }, [heatmaps, displayedSummaries]);

  return (
    <main>
      <header>
        <h1 className="app-title">Life Wrapped</h1>
        <p id="home_header">Your month-to-month life highlights that turns your daily life journal and Spotify listening habits into playful “receipts” and visual summaries. Upload your Excel log to see month-by-month stats, generate per-month calendar heatmaps, and connect Spotify to pull in your top tracks.
</p>
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
        {summaries.length > 0 && (
          <div className="receipt-controls">
            <label htmlFor="time-range-select">Select time range</label>
            <select
              id="time-range-select"
              value={timeRange}
              onChange={(event) => setTimeRange(event.target.value)}
            >
              <option value="last_month">Last month</option>
              <option value="last_three_months">Last 3 months</option>
            </select>
          </div>
        )}

        {displayedSummaries.length > 0 ? (
          <div className="receipt-row">
            {displayedSummaries.map((summary, i) => (
              <ReceiptGenerator
                key={`${summary.month_name}-${summary.year}-${i}`}
                summary={summary}
                title={`${summary.month_name} ${summary.year}`}
              />
            ))}
          </div>
        ) : (
          <p style={{ textAlign: 'center' }}>
            {summaries.length
              ? 'No receipts available for the selected time range.'
              : 'Upload an Excel file to generate your first receipt.'}
          </p>
        )}
      </section>

      {displayedHeatmaps.length > 0 && (
        <section>
          <h2>Monthly Calendar Heatmaps</h2>
          <div className="heatmap-grid">
            {displayedHeatmaps.map(({ month, year, image_url: imageUrl }) => (
              <figure key={`${month}-${year}`}>
                <img
                  src={imageUrl}
                  alt={`${month} ${year} calendar heatmap`}
                  loading="lazy"
                />
                <figcaption>
                  {month} {year}
                </figcaption>
              </figure>
            ))}
          </div>
        </section>
      )}

      <section>
        <h2>Most listened to music the past 3 months</h2>
        {!spotifySummary.length ? (
          <button type="button" onClick={handleSpotifyLogin}>
            Log in with Spotify
          </button>
        ) : (
          <SpotifySummary tracks={spotifySummary} />
        )}
      </section>

    </main>
  );
}
