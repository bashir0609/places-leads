// URL and domain utility functions (ported from backend/utils.py)

export function getRootDomain(url: string): string {
  if (!url) return ""
  try {
    const parsed = new URL(url)
    const hostname = parsed.hostname.toLowerCase()
    return hostname.startsWith("www.") ? hostname.slice(4) : hostname
  } catch {
    return ""
  }
}

export function cleanUrl(url: string): string {
  if (!url) return ""
  try {
    const parsed = new URL(url)
    return `${parsed.protocol}//${parsed.host}/`
  } catch {
    return ""
  }
}

const NAME_NOISE = [
  " - Victoria",
  " - VIC",
  " – Victoria",
  " – VIC",
  " | Victoria",
  " - NSW",
  " - QLD",
  " - WA",
  " - SA",
  " - TAS",
  " - NT",
  " - ACT",
]

export function cleanBusinessName(rawName: string): string {
  if (!rawName) return ""
  let name = rawName.trim()
  for (const n of NAME_NOISE) {
    if (name.endsWith(n)) {
      name = name.slice(0, name.length - n.length).trim()
    }
  }
  return name
}
