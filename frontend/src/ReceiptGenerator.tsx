import React from 'react';
import './index.css';

const formatValue = (key, value) => {
  if (value === null || value === undefined) {
    return '—';
  }

  if (typeof value === 'object') {
    if (isDayRecord(value)) {
      return formatDayRecord(value);
    }
    return JSON.stringify(value);
  }

  if (typeof value === 'number' && key.toLowerCase().includes('score')) {
    return value.toFixed(2);
  }

  return String(value);
};

const isDayRecord = (candidate) =>
  candidate &&
  typeof candidate.dt !== 'undefined' &&
  typeof candidate.day_score !== 'undefined';

const formatDayRecord = (day) => {
  const date = formatDate(day.dt);
  const score =
    typeof day.day_score === 'number' ? day.day_score.toFixed(2) : day.day_score;
  const highlight = day.highlight ? ` - ${day.highlight}` : '';
  return `${date} (${score})${highlight}`;
};

const formatDate = (value) => {
  if (value instanceof Date) {
    return value.toISOString().split('T')[0];
  }
  if (typeof value === 'string') {
    return value.split('T')[0];
  }
  return String(value);
};

const LifeReceiptTable = ({ summary }) => {
  const entries = Object.entries(summary ?? {});

  return (
    <table className="stats">
      <thead>
        <tr>
          <th scope="col" className="begin">
            QTY
          </th>
          <th scope="col">ITEM</th>
          <th scope="col" className="length">
            AMT
          </th>
        </tr>
      </thead>
      <tbody>
        {entries.map(([key, value], index) => (
          <tr key={key}>
            <td className="begin">{index + 1}</td>
            <td className="name">{key}</td>
            <td className="length">{formatValue(key, value)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default function ReceiptGenerator({ summary, title = "Life Receipt" }) {
  return (
    <div className="receiptContainer" aria-labelledby="receipt-title">
      <h2 id="receipt-title">{title}</h2>
      <LifeReceiptTable summary={summary} />

      <figure>
        <img
          src="./assets/barcode.png"
          alt="Receipt barcode"
          width="300"
          height="70"
        />
        <figcaption>Thank you for living intentionally!</figcaption>
      </figure>
    </div>
  );
}
