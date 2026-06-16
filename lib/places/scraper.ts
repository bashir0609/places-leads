// Google Places API scraping logic (ported from backend/scraper.py)

import { parseAddress } from "./address-parser"
import { cleanBusinessName, cleanUrl, getRootDomain } from "./url-utils"
import type { PlaceResult } from "./types"

const MAX_PER_PAGE = 20
const MAX_PER_QUERY = 60

const QUERY_EXPANSIONS = [
  "{q}",
  "best {q}",
  "top {q}",
  "{q} near me",
  "{q} services",
  "{q} company",
  "affordable {q}",
  "professional {q}",
  "local {q}",
  "trusted {q}",
  "{q} experts",
  "{q} specialists",
  "{q} providers",
  "{q} contractors",
  "reliable {q}",
  "quality {q}",
  "premium {q}",
  "{q} solutions",
]

const SEARCH_FIELDS =
  "places.id,places.displayName,places.formattedAddress," +
  "places.primaryType,places.primaryTypeDisplayName,places.types,nextPageToken"

const DETAILS_FIELDS =
  "id,displayName,formattedAddress,websiteUri,nationalPhoneNumber,googleMapsUri"

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

interface GooglePlace {
  id?: string
  displayName?: { text?: string }
  formattedAddress?: string
  websiteUri?: string
  nationalPhoneNumber?: string
  primaryType?: string
  primaryTypeDisplayName?: { text?: string }
}

async function fetchPlaceDetails(
  apiKey: string,
  placeId: string
): Promise<GooglePlace> {
  const url = `https://places.googleapis.com/v1/places/${placeId}`
  try {
    const res = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": apiKey,
        "X-Goog-FieldMask": DETAILS_FIELDS,
      },
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return (await res.json()) as GooglePlace
  } catch (e) {
    console.log(`[v0] Details failed for ${placeId}: ${String(e).slice(0, 80)}`)
    return {}
  }
}

function parsePlace(place: GooglePlace): PlaceResult {
  const address = place.formattedAddress ?? ""
  const rawName = place.displayName?.text ?? ""
  const cleanName = cleanBusinessName(rawName)
  const { address_line, city, state, postcode } = parseAddress(address)
  const website = cleanUrl(place.websiteUri ?? "")
  const phone = place.nationalPhoneNumber ?? ""

  let category = place.primaryType ?? ""
  if (place.primaryTypeDisplayName?.text) {
    category = place.primaryTypeDisplayName.text
  }

  return {
    id: place.id ?? "",
    name: cleanName,
    address: address_line,
    city,
    state,
    postcode,
    phone,
    website,
    domain: getRootDomain(website),
    maps_url: `https://www.google.com/maps/place/?q=place_id:${place.id ?? ""}`,
    category,
  }
}

async function runSingleQuery(
  apiKey: string,
  query: string,
  location: string,
  maxResults: number
): Promise<PlaceResult[]> {
  const url = "https://places.googleapis.com/v1/places:searchText"
  const results: PlaceResult[] = []
  const seenIds = new Set<string>()
  let pageToken: string | undefined

  while (results.length < maxResults) {
    const payload: Record<string, unknown> = {
      textQuery: `${query} in ${location}`,
      maxResultCount: Math.min(MAX_PER_PAGE, maxResults - results.length),
    }
    if (pageToken) payload.pageToken = pageToken

    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": apiKey,
        "X-Goog-FieldMask": SEARCH_FIELDS,
      },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const text = await res.text()
      throw new Error(`Places search failed (HTTP ${res.status}): ${text.slice(0, 200)}`)
    }
    const data = (await res.json()) as {
      places?: GooglePlace[]
      nextPageToken?: string
    }

    for (const place of data.places ?? []) {
      const pid = place.id ?? ""
      if (seenIds.has(pid)) continue
      seenIds.add(pid)
      results.push(parsePlace(place))
    }

    pageToken = data.nextPageToken
    if (!pageToken) break
    await sleep(500)
  }

  return results
}

async function searchWithExpansions(
  apiKey: string,
  query: string,
  location: string,
  limit: number,
  seenIds: Set<string>,
  outResults: PlaceResult[]
): Promise<PlaceResult[]> {
  const start = outResults.length
  for (const template of QUERY_EXPANSIONS) {
    if (outResults.length - start >= limit) break
    const q = template.replace("{q}", query)
    const remaining = Math.min(MAX_PER_QUERY, limit - (outResults.length - start))
    const batch = await runSingleQuery(apiKey, q, location, remaining)
    let added = 0
    for (const place of batch) {
      const key = place.domain || place.id
      if (seenIds.has(key)) continue
      seenIds.add(key)
      outResults.push(place)
      added += 1
    }
    if (added === 0 && outResults.length > start) break
    if (outResults.length - start >= limit) break
    await sleep(1000)
  }
  return outResults
}

async function enrichResultsWithDetails(
  apiKey: string,
  results: PlaceResult[]
): Promise<PlaceResult[]> {
  const enriched: PlaceResult[] = []
  for (const place of results) {
    const pid = place.id
    if (!pid) continue

    const details = await fetchPlaceDetails(apiKey, pid)
    if (details && Object.keys(details).length > 0) {
      const website = cleanUrl(details.websiteUri ?? "")
      place.website = website || place.website || ""
      place.domain = getRootDomain(place.website) || place.domain || ""
      place.phone = details.nationalPhoneNumber || place.phone || ""
    }

    if (place.website) {
      enriched.push(place)
    }

    await sleep(200)
  }
  return enriched
}

function stateFromLocation(location: string): string {
  return location.split(/\s+/)[0]
}

export async function searchPlaces(
  apiKey: string,
  query: string,
  location: string,
  limit = 50,
  cities?: string[] | null,
  stateCode?: string
): Promise<PlaceResult[]> {
  const keywords = query
    .split(",")
    .map((k) => k.trim())
    .filter(Boolean)
  const cityList = cities && cities.length ? cities : [location.split(/\s+/)[0]]
  const st = stateCode || stateFromLocation(location)

  // Step 1: Search for places
  if (keywords.length > 1 || cityList.length > 1) {
    const allResults: PlaceResult[] = []
    const seenIds = new Set<string>()
    const total = keywords.length * cityList.length
    const perCombo = Math.max(5, Math.floor(limit / total))

    for (const kw of keywords) {
      if (allResults.length >= limit) break
      for (const c of cityList) {
        if (allResults.length >= limit) break
        const cityLoc = `${c} ${st}`
        await searchWithExpansions(
          apiKey,
          kw,
          cityLoc,
          perCombo * 2,
          seenIds,
          allResults
        )
        if (allResults.length >= limit) break
        await sleep(500)
      }
    }

    const enriched = await enrichResultsWithDetails(apiKey, allResults)
    return enriched.slice(0, limit)
  }

  // Single keyword, single city
  const seen = new Set<string>()
  const basicResults: PlaceResult[] = []
  await searchWithExpansions(apiKey, keywords[0], location, limit, seen, basicResults)
  const enriched = await enrichResultsWithDetails(apiKey, basicResults)
  return enriched.slice(0, limit)
}
