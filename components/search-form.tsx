"use client"

import { Search, X, Loader2, Globe } from "lucide-react"

import LOCATIONS from "@/lib/locations"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Card, CardContent } from "@/components/ui/card"

export const ALL_CITIES = "__ALL__"

interface SearchFormProps {
  query: string
  setQuery: (q: string) => void
  country: string
  state: string
  city: string[]
  limit: number
  onCountryChange: (country: string, state: string, city: string[]) => void
  onStateChange: (state: string, city: string[]) => void
  onCityChange: (city: string[]) => void
  onLimitChange: (limit: number) => void
  onSubmit: () => void
  loading: boolean
}

export function SearchForm({
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
}: SearchFormProps) {
  const countryData = LOCATIONS[country]
  const states = countryData ? Object.keys(countryData.states) : []
  const cities = countryData?.states[state] ?? []
  const isAll = city.includes(ALL_CITIES)
  const availableCities = cities.filter((c) => !city.includes(c))

  const handleCountryChange = (newCountry: string) => {
    const firstState = Object.keys(LOCATIONS[newCountry].states)[0]
    onCountryChange(newCountry, firstState, [
      LOCATIONS[newCountry].states[firstState][0],
    ])
  }

  const handleStateChange = (newState: string) => {
    onStateChange(newState, [countryData.states[newState]?.[0] ?? ""])
  }

  const handleCitySelect = (val: string) => {
    if (!val) return
    if (val === ALL_CITIES) {
      onCityChange([ALL_CITIES])
    } else if (!city.includes(val) && city.length < 3 && !isAll) {
      onCityChange([...city, val])
    }
  }

  const removeCity = (c: string) => {
    onCityChange(city.filter((x) => x !== c))
  }

  return (
    <Card>
      <CardContent className="p-6">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            onSubmit()
          }}
          className="flex flex-col gap-5"
        >
          <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
            <div className="flex flex-col gap-2 lg:col-span-3">
              <Label htmlFor="query">Search query</Label>
              <Input
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g. equipment hire, plumbing (comma-separated keywords)"
                required
              />
              <p className="text-xs text-muted-foreground">
                Separate multiple keywords with commas to broaden the search.
              </p>
            </div>

            <div className="flex flex-col gap-2">
              <Label>Country</Label>
              <Select value={country} onValueChange={handleCountryChange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(LOCATIONS).map(([code, data]) => (
                    <SelectItem key={code} value={code}>
                      {data.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-2">
              <Label>State / Region</Label>
              <Select value={state} onValueChange={handleStateChange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {states.map((s) => (
                    <SelectItem key={s} value={s}>
                      {s}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-2">
              <Label htmlFor="limit">Result limit</Label>
              <Input
                id="limit"
                type="number"
                min={1}
                max={5000}
                value={limit}
                onChange={(e) => onLimitChange(Number(e.target.value))}
              />
            </div>

            <div className="flex flex-col gap-2 lg:col-span-3">
              <Label>Cities (up to 3, or all)</Label>
              <Select value="" onValueChange={handleCitySelect}>
                <SelectTrigger>
                  <SelectValue
                    placeholder={
                      isAll
                        ? "All cities selected"
                        : city.length >= 3
                          ? "Maximum of 3 cities selected"
                          : "Add a city..."
                    }
                  />
                </SelectTrigger>
                <SelectContent>
                  {!isAll && (
                    <SelectItem value={ALL_CITIES}>
                      All cities ({cities.length})
                    </SelectItem>
                  )}
                  {availableCities.map((c) => (
                    <SelectItem key={c} value={c}>
                      {c}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {city.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-1">
                  {isAll ? (
                    <button
                      type="button"
                      onClick={() => onCityChange([])}
                      className="inline-flex items-center gap-1.5 rounded-md bg-accent px-2.5 py-1 text-xs font-medium text-accent-foreground transition-opacity hover:opacity-90"
                    >
                      <Globe className="h-3.5 w-3.5" />
                      All cities
                      <X className="h-3.5 w-3.5" />
                    </button>
                  ) : (
                    city.map((c) => (
                      <button
                        key={c}
                        type="button"
                        onClick={() => removeCity(c)}
                        className="inline-flex items-center gap-1.5 rounded-md bg-secondary px-2.5 py-1 text-xs font-medium text-secondary-foreground transition-colors hover:bg-border"
                      >
                        {c}
                        <X className="h-3.5 w-3.5" />
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>

          <div>
            <Button type="submit" size="lg" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search />
                  Search leads
                </>
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
