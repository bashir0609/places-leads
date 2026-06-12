import React, { useState } from "react";
import axios from "axios";
import "./App.css";
import SearchForm from "./components/SearchForm";
import ResultsTable from "./components/ResultsTable";
import LOCATIONS from "./data/locations";

function App() {
  const [query, setQuery] = useState("equipment hire");
  const [country, setCountry] = useState("AU");
  const [state, setState] = useState("NSW");
  const [city, setCity] = useState(["Sydney"]);
  const [limit, setLimit] = useState(50);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [scraping, setScraping] = useState(false);
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

  const handleCountryChange = (newCountry, newState, newCity) => {
    setCountry(newCountry);
    setState(newState);
    setCity(newCity);
  };

  const handleStateChange = (newState, newCity) => {
    setState(newState);
    setCity(newCity);
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setPage(1);
    setError(null);
    try {
      const isAll = city.length === 1 && city[0] === "__ALL__";
      const location = isAll
        ? `${state} (all cities)`
        : `${city.join(", ")} ${state}`;
      const citiesList = isAll
        ? LOCATIONS[country].states[state]
        : city.length > 1 || !isAll
          ? city
          : null;

      const response = await axios.post(`${API_URL}/api/search`, {
        query,
        location,
        limit: parseInt(limit),
        cities: citiesList,
        state,
      });
      setResults(response.data.results || []);
    } catch (err) {
      setError(err.response?.data?.error || err.message || "Search failed");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleScrapeEmails = async () => {
    if (results.length === 0) return;
    setScraping(true);
    try {
      const response = await axios.post(`${API_URL}/api/scrape-emails`, {
        results,
      });
      setResults(response.data.results || []);
    } catch (err) {
      setError(
        "Email scraping failed: " + (err.response?.data?.error || err.message),
      );
    } finally {
      setScraping(false);
    }
  };

  const handleExport = () => {
    if (results.length === 0) {
      alert("No results to export");
      return;
    }
    const headers = [
      "Business Name",
      "Website",
      "Domain",
      "Address",
      "City",
      "State",
      "Zip",
      "Phone",
      "Google Maps Category",
      "Google Maps url",
    ];
    const rows = results.map((r) => [
      r.name,
      r.website || "",
      r.domain || "",
      r.address,
      r.city,
      r.state,
      r.postcode,
      r.phone || "",
      r.category || "",
      r.maps_url || "",
    ]);
    const csv = [headers, ...rows]
      .map((row) =>
        row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(","),
      )
      .join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    const today = new Date().toISOString().slice(0, 10);
    const safeQuery = query.replace(/[^a-zA-Z0-9]/g, "-").slice(0, 30);
    const cityStr = Array.isArray(city) ? city.slice(0, 2).join("-") : city;
    link.download = `${today}_${safeQuery}_${cityStr.replace(/[^a-zA-Z0-9-]/g, "")}.csv`;
    link.click();
  };

  const totalPages = Math.ceil(results.length / pageSize);
  const paginatedResults = results.slice(
    (page - 1) * pageSize,
    page * pageSize,
  );

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>🔍 Google Places Scraper</h1>
          <p className="subtitle">Extract business leads from Google Maps</p>
        </div>
      </header>

      <main className="main">
        <SearchForm
          query={query}
          setQuery={setQuery}
          country={country}
          state={state}
          city={city}
          limit={limit}
          onCountryChange={handleCountryChange}
          onStateChange={handleStateChange}
          onCityChange={setCity}
          onLimitChange={setLimit}
          onSubmit={handleSearch}
          loading={loading}
        />

        {error && <div className="error-message">{error}</div>}

        {results.length > 0 && (
          <ResultsTable
            results={paginatedResults}
            onExport={handleExport}
            onScrapeEmails={handleScrapeEmails}
            scraping={scraping}
            page={page}
            totalPages={totalPages}
            totalResults={results.length}
            onPageChange={setPage}
          />
        )}

        {!loading && results.length === 0 && !error && (
          <div className="empty-state">
            <p>Enter your search criteria and click Search to get started</p>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>&copy; 2024 Google Places Scraper. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;
