import { NextResponse } from "next/server"

import { searchPlaces } from "@/lib/places/scraper"
import type { SearchRequestBody } from "@/lib/places/types"

export const runtime = "nodejs"
export const maxDuration = 300

export async function POST(request: Request) {
  try {
    const apiKey = process.env.GOOGLE_PLACES_API_KEY
    if (!apiKey) {
      return NextResponse.json(
        { error: "API key not configured. Set GOOGLE_PLACES_API_KEY." },
        { status: 500 }
      )
    }

    const data = (await request.json()) as SearchRequestBody
    const query = data.query?.trim() || "equipment hire"
    const location = data.location?.trim() || "Sydney NSW"
    const limit = Math.min(Number(data.limit) || 50, 5000)

    const results = await searchPlaces(
      apiKey,
      query,
      location,
      limit,
      data.cities,
      data.state
    )

    return NextResponse.json({
      success: true,
      count: results.length,
      query,
      location,
      results,
    })
  } catch (e) {
    const message = e instanceof Error ? e.message : "Search failed"
    return NextResponse.json({ error: message }, { status: 500 })
  }
}
