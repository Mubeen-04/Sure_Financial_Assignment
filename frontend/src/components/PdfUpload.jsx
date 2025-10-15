import React, { useState } from "react";
import "./PdfUpload.css";

export default function PdfUpload() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Upload & parse PDF
  const upload = async () => {
    if (!file) return alert("Choose a PDF first");
    setLoading(true);

    const fd = new FormData();
    fd.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/parse", {
        method: "POST",
        body: fd,
      });
      const data = await res.json();
      setResult(data);
    } catch (e) {
      alert("Error: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  // Drag & drop
  const handleDrop = (e) => {
    e.preventDefault();
    setFile(e.dataTransfer.files[0]);
  };

  return (
    <div className="container">
      <div className="parser-card">
        <h2>Credit Card PDF Parser</h2>

        {/* Drag & Drop */}
        <div
          className={`dropzone ${file ? "active" : ""}`}
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => document.getElementById("fileInput").click()}
        >
          {file ? file.name : "Drag & drop PDF here or click to select"}
        </div>

        <input
          id="fileInput"
          type="file"
          accept="application/pdf"
          style={{ display: "none" }}
          onChange={(e) => setFile(e.target.files[0])}
        />

        {/* Upload Button */}
        <button
          className="upload-btn"
          onClick={upload}
          disabled={loading}
        >
          {loading ? "Parsing..." : "Upload & Parse"}
        </button>

        {/* Key Fields */}
        {result && (
          <div className="results">
            <div className="key-fields">
              {[
                ["Issuer", "issuer"],
                ["Card No", "cardNo"],
                ["Card Variant", "cardVariant"],
                ["Statement Period", "statementPeriod"],
                ["Payment Due Date", "paymentDueDate"],
                ["Total Amount Due", "totalAmountDue"],
                ["Minimum Amount Due", "minimumAmountDue"],
              ].map(([label, key]) => (
                <div key={key} className={`field ${result[key] ? "" : "missing"}`}>
                  <strong>{label}:</strong> {result[key] || "N/A"}
                </div>
              ))}
            </div>

            {/* Transactions Table */}
            {result.transactions && result.transactions.length > 0 && (
              <div className="transactions-table">
                <table>
                  <thead>
                    <tr>
                      {["Date", "Type", "Description", "Debit", "Credit"].map((col) => (
                        <th key={col}>{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.transactions.map((tx, idx) => (
                      <tr key={idx} className={idx % 2 === 0 ? "even" : "odd"}>
                        <td>{tx.date || "N/A"}</td>
                        <td>{tx.type || "N/A"}</td>
                        <td>{tx.description || "N/A"}</td>
                        <td>{tx.debit || "-"}</td>
                        <td>{tx.credit || "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
