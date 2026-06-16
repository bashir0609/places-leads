// Email extraction from business websites (ported from backend/email_scraper.py)

import type { PlaceResult } from "./types"

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))
const EMAIL_RE = /[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+/

export async function scrapeEmailsFromWebsites(
  results: PlaceResult[]
): Promise<PlaceResult[]> {
  for (const p of results) {
    const website = p.website ?? ""
    if (!website) {
      p.email = ""
      continue
    }

    try {
      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), 8000)
      const res = await fetch(website, {
        headers: {
          "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        },
        signal: controller.signal,
      })
      clearTimeout(timeout)
      const text = await res.text()
      const match = text.match(EMAIL_RE)
      p.email = match ? match[0].toLowerCase() : ""
    } catch (e) {
      p.email = ""
      console.log(`[v0] Email scrape error for ${website}: ${String(e).slice(0, 80)}`)
    }

    await sleep(500)
  }

  return results
}
