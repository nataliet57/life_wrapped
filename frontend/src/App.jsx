import React, { useState, useEffect } from 'react';
import './index.css';
import ReceiptGenerator from './ReceiptGenerator';

export default function App() {
  const [summaries, setSummaries] = useState([]);
  const [filename, setFilename] = useState('');
  const [uploadError, setUploadError] = useState(null);
  const [loading, setLoading] = useState(false);
  const API_BASE = import.meta.env.VITE_API_BASE_URL || window.location.origin;

  async function fetchLastSummary() {
    try {
      const res = await fetch(`${API_BASE}/api/last-summary`, {
        credentials: 'include',
      });
      if (!res.ok) return; // no summary yet is fine
      const data = await res.json();
      setFilename(data.filename || '');
      setSummaries(data.summaries || []);
    } catch (err) {
      console.error('Error fetching last summary:', err);
    }
  }

  useEffect(() => {
    fetchLastSummary();
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

      const uploadRes = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });

      if (!uploadRes.ok) {
        throw new Error(`Upload failed: ${uploadRes.status}`);
      }

      const payload = await uploadRes.json();
      setFilename(payload.filename || '');
      setSummaries(payload.summaries || []);
    } catch (err) {
      console.error('Upload error:', err);
      setUploadError(err.message);
    } finally {
      setLoading(false);
    }
  }

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
