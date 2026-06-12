import React from "react";

function ResultsTable({
  results,
  onExport,
  onScrapeEmails,
  scraping,
  page,
  totalPages,
  totalResults,
  onPageChange,
}) {
  return (
    <div className="results-section">
      <div className="results-header">
        <h2>Results ({totalResults})</h2>
        <div style={{ display: "flex", gap: "10px" }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onScrapeEmails}
            disabled={scraping}
          >
            {scraping ? "📧 Scraping..." : "📧 Scrape Emails"}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onExport}
          >
            ⬇ Export CSV
          </button>
        </div>
      </div>

      <div className="table-wrapper">
        <table className="results-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Business Name</th>
              <th>Category</th>
              <th>Address</th>
              <th>City</th>
              <th>State</th>
              <th>Postcode</th>
              <th>Phone</th>
              <th>Email</th>
              <th>Website</th>
              <th>Maps</th>
              <th>Domain</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r, index) => (
              <tr key={index}>
                <td className="index-cell">{(page - 1) * 20 + index + 1}</td>
                <td className="name-cell">{r.name}</td>
                <td className="category-cell">{r.category || "—"}</td>
                <td className="address-cell">{r.address}</td>
                <td>{r.city}</td>
                <td>
                  <span className="state-badge">{r.state}</span>
                </td>
                <td>{r.postcode}</td>
                <td className="phone-cell">{r.phone || "—"}</td>
                <td className="email-cell">{r.email || "—"}</td>
                <td className="website-cell">
                  {r.website ? (
                    <a
                      href={r.website}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Visit
                    </a>
                  ) : (
                    "—"
                  )}
                </td>
                <td className="website-cell">
                  {r.maps_url ? (
                    <a
                      href={r.maps_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      📍 Map
                    </a>
                  ) : (
                    "—"
                  )}
                </td>
                <td className="domain-cell">{r.domain || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button onClick={() => onPageChange(1)} disabled={page === 1}>
            ««
          </button>
          <button onClick={() => onPageChange(page - 1)} disabled={page === 1}>
            « Prev
          </button>
          <span className="page-info">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page === totalPages}
          >
            Next »
          </button>
          <button
            onClick={() => onPageChange(totalPages)}
            disabled={page === totalPages}
          >
            »»
          </button>
        </div>
      )}
    </div>
  );
}

export default ResultsTable;
