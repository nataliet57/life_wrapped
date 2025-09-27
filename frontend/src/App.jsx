import React, { useState } from 'react';
import './index.css';
import ReceiptGenerator from './ReceiptGenerator';

export default function App() {
  const [receipts, setReceipts] = useState(null);

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
      });
      console.log("status", res.status);
      const data = await res.json();
      console.log("data", data);
    } catch (err) {
      console.error("fetch failed", err);
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

      {receipts && (
        <section>
          {receipts.map((summary, i) => (
            <ReceiptGenerator
              key={i}
              summary={summary}
              title={`${summary.month_name} ${summary.year}`}
            />
          ))}
        </section>
      )}
    </main>
  );
}
