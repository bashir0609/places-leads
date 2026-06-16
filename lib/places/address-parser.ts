// Address parsing for international formats (AU, US, UK, SA, and more)
// Ported from backend/address_parser.py

const STATE_CODES = new Set([
  "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
  "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
  "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
  "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
  "WI", "WY", "VIC", "NSW", "QLD", "SA", "TAS", "NT", "ACT",
])

const COUNTRIES = new Set([
  "Australia", "USA", "United States", "UK", "United Kingdom",
  "Saudi Arabia", "Canada", "India", "UAE", "Germany", "France",
])

function isPostcode(token: string): boolean {
  return /^\d+$/.test(token) && token.length >= 4
}

export interface ParsedAddress {
  address_line: string
  city: string
  state: string
  postcode: string
}

export function parseAddress(formattedAddress: string): ParsedAddress {
  if (!formattedAddress) {
    return { address_line: "", city: "", state: "", postcode: "" }
  }

  const parts = formattedAddress.split(",").map((p) => p.trim())
  let state = ""
  let city = ""
  let postcode = ""
  let addressLine = ""
  let statePartIdx: number | null = null

  // Step 1: Try to find a recognized state code
  for (let i = 0; i < parts.length; i++) {
    const tokens = parts[i].trim().split(/\s+/).filter(Boolean)
    let matched = false
    for (const token of tokens) {
      if (STATE_CODES.has(token)) {
        state = token
        statePartIdx = i
        for (let t = tokens.length - 1; t >= 0; t--) {
          if (isPostcode(tokens[t])) {
            postcode = tokens[t]
            break
          }
        }
        const samePartCity = tokens
          .filter((t) => t !== token && !isPostcode(t))
          .join(" ")
        if (samePartCity) {
          city = samePartCity
        } else if (i > 0) {
          city = parts[i - 1]
        }
        matched = true
        break
      }
    }
    if (matched) break
  }

  // Step 2: Fallback — no state code found (e.g. Saudi Arabia, UK, etc.)
  if (statePartIdx === null && parts.length >= 2) {
    let lastIdx = parts.length - 1
    if (COUNTRIES.has(parts[lastIdx].trim())) {
      lastIdx -= 1
    }

    for (let i = lastIdx; i > 0; i--) {
      const tokens = parts[i].trim().split(/\s+/).filter(Boolean)
      let foundPostcode: string | null = null
      for (let t = tokens.length - 1; t >= 0; t--) {
        if (isPostcode(tokens[t])) {
          foundPostcode = tokens[t]
          break
        }
      }
      if (foundPostcode) {
        postcode = foundPostcode
        city = tokens.filter((t) => t !== foundPostcode).join(" ")
        statePartIdx = i
        break
      }
    }

    if (statePartIdx === null) {
      for (let i = lastIdx; i > 0; i--) {
        const tokens = parts[i].trim().split(/\s+/).filter(Boolean)
        const allNum = tokens.length > 0 && tokens.every((t) => /^\d+$/.test(t))
        if (!allNum && tokens.length > 0) {
          city = parts[i]
          statePartIdx = i
          break
        }
      }
    }
  }

  if (statePartIdx !== null && statePartIdx > 0) {
    addressLine = parts.slice(0, statePartIdx).join(", ")
  }

  return { address_line: addressLine, city, state, postcode }
}
