import React from "react";
import LOCATIONS from "../data/locations";

function SearchForm({
  query,
  setQuery,
  country,
  state,
  city,
  limit,
  onCountryChange,
  onStateChange,
  onCityChange,
  onLimitChange,
  onSubmit,
  loading,
}) {
  const countryData = LOCATIONS[country];
  const states = countryData ? Object.keys(countryData.states) : [];
  const cities = countryData?.states[state] || [];

  const handleCountryChange = (newCountry) => {
    const firstState = Object.keys(LOCATIONS[newCountry].states)[0];
    onCountryChange(newCountry, firstState, [
      LOCATIONS[newCountry].states[firstState][0],
    ]);
  };

  const handleStateChange = (newState) => {
    onStateChange(newState, [countryData.states[newState]?.[0] || ""]);
  };

  const handleCitySelect = (e) => {
    const val = e.target.value;
    if (!val) return;
    if (val === "__ALL__") {
      onCityChange(["__ALL__"]);
    } else if (
      !city.includes(val) &&
      city.length < 3 &&
      !city.includes("__ALL__")
    ) {
      onCityChange([...city, val]);
    }
    e.target.value = "";
  };

  const removeCity = (c) => {
    onCityChange(city.filter((x) => x !== c));
  };

  const availableCities = cities.filter((c) => !city.includes(c));

  return (
    <form className="search-form" onSubmit={onSubmit}>
      <div className="form-row">
        <div className="form-group">
          <label htmlFor="query">Search Query</label>
          <input
            id="query"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., equipment hire, plumbing"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="country">Country</label>
          <select
            id="country"
            value={country}
            onChange={(e) => handleCountryChange(e.target.value)}
          >
            {Object.entries(LOCATIONS).map(([code, data]) => (
              <option key={code} value={code}>
                {data.label}
              </option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="state">State</label>
          <select
            id="state"
            value={state}
            onChange={(e) => handleStateChange(e.target.value)}
          >
            {states.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="city">City (up to 3)</label>
          {!city.includes("__ALL__") && city.length > 0 && (
            <div className="city-tags">
              {city.map((c) => (
                <span
                  key={c}
                  className="city-tag"
                  onClick={() => removeCity(c)}
                >
                  {c} ✕
                </span>
              ))}
            </div>
          )}
          <select id="city" onChange={handleCitySelect} defaultValue="">
            <option value="" disabled>
              {city.includes("__ALL__")
                ? "🌍 All Cities selected"
                : city.length >= 3
                  ? "Max 3 selected"
                  : "Add a city..."}
            </option>
            {!city.includes("__ALL__") && (
              <option value="__ALL__">🌍 All Cities ({cities.length})</option>
            )}
            {availableCities.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="limit">Result Limit</label>
          <input
            id="limit"
            type="number"
            min="1"
            max="1000"
            value={limit}
            onChange={(e) => onLimitChange(e.target.value)}
          />
        </div>
      </div>
      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? "Searching..." : "🚀 Search"}
      </button>
    </form>
  );
}

export default SearchForm;
