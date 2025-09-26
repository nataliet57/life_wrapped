import React, { useState } from 'react';
import './index.css';
import ReceiptGenerator from './ReceiptGenerator';

export default function App() {
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(false);

  async function handleUpload(e) {
    e.preventDefault();
    const fileInput = e.target.elements.file;
    if (!fileInput.files?.length) return;

    setLoading(true);
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
      const res = await fetch("/upload", { method: "POST", body: formData });
      if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
      const data = await res.json();
      setSummaries(data);  // should be a list of monthly summaries
    } catch (err) {
      console.error(err);
      alert("Something went wrong uploading the file.");
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
          <button type="submit">Generate Receipts</button>
        </form>
      </section>

      {loading && <p>Loading...</p>}

      {summaries.length > 0 && (
        <section>
          {summaries.map((s, i) => (
            <ReceiptGenerator
              key={i}
              summary={s}
              title={`${s.month_name} ${s.year}`}
            />
          ))}
        </section>
      )}
    </main>
  );
}
