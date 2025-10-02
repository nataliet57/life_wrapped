import React from "react";
import "./index.css";

function formatValue(value) {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") return value.toFixed(2);
  if (typeof value === "object" && !Array.isArray(value)) {
    const date = value.dt?.split("T")[0];
    const score = value.day_score ? value.day_score.toFixed(2) : "";
    const highlight = value.highlight ? ` - ${value.highlight}` : "";
    return `${date ?? ""} (${score})${highlight}`;
  }
  return String(value);
}

export default function ReceiptGenerator({ summary, title = "Life Receipt" }) {
  const rows = [
    ["Days Logged", "days_logged"],
    ["Average Score", "average_score"],
    ["Top Five Days", "top_five_days"],
    ["Worst Day", "worst_day"],
    ["Days Above Avg Sleep", "number_of_days_with_above_average_sleep"],
  ];

  return (
    <div className="receiptContainer" aria-labelledby="receipt-title">
      <h2 id="receipt-title">{title}</h2>
      <table className="stats">
        <thead>
          <tr>
            <th className="begin">QTY</th>
            <th>ITEM</th>
            <th className="length">AMT</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(([label, key], index) => {
            const value = summary[key];

            // special handling for top_four_days
            if ( (key === "top_four_days" || key === "worst_day") && Array.isArray(value) ) {
              return[
                <tr key={key}>
                  <td className="begin">{index+1}</td>
                  <td className="name">{label}</td>
                  <td className="length"></td>
                </tr>,

                ...value.map((day, subIndex) => (
                  <tr key={`${key}-${subIndex}`}>
                    <td className="begin"></td>
                    <td className="name" style={{ paddingLeft: "1rem" }}>
                      {day.dt} - {day.highlight}
                    </td>
                    <td className="length">{day.day_score}</td>
                  </tr>
                )),
              ]
            }

            // normal row
            return (
              <tr key={key}>
                <td className="begin">{index + 1}</td>
                <td className="name">{label}</td>
                <td className="length">{formatValue(value)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>

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
