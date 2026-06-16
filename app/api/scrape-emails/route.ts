import { NextResponse } from "next/server"

import { scrapeEmailsFromWebsites } from "@/lib/places/email-scraper"
import type { PlaceResult } from "@/lib/places/types"

export const runtime = "nodejs"
export const maxDuration = 300

export async function POST(request: Request) {
  try {
    const data = (await request.json()) as { results?: PlaceResult[] }
    const results = data.results ?? []
    if (results.length === 0) {
      return NextResponse.json({ error: "No results provided" }, { status: 400 })
    }
    await scrapeEmailsFromWebsites(results)
    return NextResponse.json({
      success: true,
      count: results.length,
      results,
    })
  } catch (e) {
    const message = e instanceof Error ? e.message : "Email scraping failed"
    return NextResponse.json({ error: message }, { status: 500 })
  }
}
