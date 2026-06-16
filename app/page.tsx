"use client"

import { useMemo, useState } from "react"
import { MapPinned, AlertCircle } from "lucide-react"

import LOCATIONS from "@/lib/locations"
import type { PlaceResult } from "@/lib/places/types"
import { SearchForm, ALL_CITIES } from "@/components/search-form"
import { ResultsTable } from "@/components/results-table"

const PAGE_SIZE = 20

export default function Page() {
  const [query, setQuery] = useState("equipment hire")
  const [country, setCountry] = useState("AU")
  const [state, setState] = useState("NSW")
  const [city, setCity] = useState<string[]>(["Sydney"])
  const [limit, setLimit] = useState(50)
  const [results, setResults] = useState<PlaceResult[]>([])
  const [loading, setLoading] = useState(false)
  const [scraping, setScraping] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)

  const handleCountryChange = (newCountry: string, newState: string, newCity: string[]) => {
    setCountry(newCountry)
    setState(newState)
    setCity(newCity)
  }

  const handleStateChange = (newState: string, newCity: string[]) => {
    setState(newState)
    setCity(newCity)
  }

  const handleSearch = async () => {
    setLoading(true)
    setPage(1)
    setError(null)
    try {
      const isAll = city.length === 1 && city[0] === ALL_CITIES
      const location = isAll ? `${state} (all cities)` : `${city.join(", ")} ${state}`
      const citiesList = isAll ? LOCATIONS[country].states[state] : city

      const res = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          location,
          limit: Number(limit),
          cities: citiesList,
          state,
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || "Search failed")
      setResults(data.results ?? [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed")
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const handleScrapeEmails = async () => {
    if (results.length === 0) return
    setScraping(true)
    setError(null)
    try {
      const res = await fetch("/api/scrape-emails", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ results }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || "Email scraping failed")
      setResults(data.results ?? [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Email scraping failed")
    } finally {
      setScraping(false)
    }
  }

  const handleExport = () => {
    if (results.length === 0) return
    const headers = [
      "Business Name",
      "Website",
      "Domain",
      "Email",
      "Address",
      "City",
      "State",
      "Zip",
      "Phone",
      "Google Maps Category",
      "Google Maps url",
    ]
    const rows = results.map((r) => [
      r.name,
      r.website ?? "",
      r.domain ?? "",
      r.email ?? "",
      r.address,
      r.city,
      r.state,
      r.postcode,
      r.phone ?? "",
      r.category ?? "",
      r.maps_url ?? "",
    ])
    const csv = [headers, ...rows]
      .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(","))
      .join("\n")
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" })
    const link = document.createElement("a")
    link.href = URL.createObjectURL(blob)
    const today = new Date().toISOString().slice(0, 10)
    const safeQuery = query.replace(/[^a-zA-Z0-9]/g, "-").slice(0, 30)
    const cityStr = city.slice(0, 2).join("-")
    link.download = `${today}_${safeQuery}_${cityStr.replace(/[^a-zA-Z0-9-]/g, "")}.csv`
    link.click()
  }

  const totalPages = Math.max(1, Math.ceil(results.length / PAGE_SIZE))
  const paginatedResults = useMemo(
    () => results.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE),
    [results, page]
  )

  return (
    <div className="min-h-screen">
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex max-w-7xl items-center gap-3 px-4 py-5 sm:px-6 lg:px-8">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <MapPinned className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-lg font-semibold leading-tight text-foreground">
              Places Leads
            </h1>
            <p className="text-sm text-muted-foreground">
              Extract business leads from Google Maps
            </p>
          </div>
        </div>
      </header>

      <main className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8">
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

        {error && (
          <div
            role="alert"
            className="flex items-start gap-3 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
          >
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

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
          <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border bg-card/50 px-6 py-16 text-center">
            <MapPinned className="h-8 w-8 text-muted-foreground" />
            <p className="text-sm font-medium text-foreground">No results yet</p>
            <p className="text-sm text-muted-foreground">
              Enter your search criteria above and run a search to get started.
            </p>
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-border bg-card px-6 py-16 text-center">
            <p className="text-sm font-medium text-foreground">Searching Google Places…</p>
            <p className="text-sm text-muted-foreground">
              This can take a while for multi-city searches with website enrichment.
            </p>
          </div>
        )}
      </main>

      <footer className="border-t border-border py-6">
        <p className="text-center text-xs text-muted-foreground">
          Places Leads — Google Places lead scraper
        </p>
      </footer>
    </div>
  )
}
