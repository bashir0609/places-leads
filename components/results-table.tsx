"use client"

import {
  Download,
  Mail,
  Loader2,
  ExternalLink,
  MapPin,
  ChevronsLeft,
  ChevronLeft,
  ChevronRight,
  ChevronsRight,
} from "lucide-react"

import type { PlaceResult } from "@/lib/places/types"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const PAGE_SIZE = 20

interface ResultsTableProps {
  results: PlaceResult[]
  onExport: () => void
  onScrapeEmails: () => void
  scraping: boolean
  page: number
  totalPages: number
  totalResults: number
  onPageChange: (page: number) => void
}

export function ResultsTable({
  results,
  onExport,
  onScrapeEmails,
  scraping,
  page,
  totalPages,
  totalResults,
  onPageChange,
}: ResultsTableProps) {
  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between gap-4 border-b border-border">
        <CardTitle className="flex items-center gap-2">
          Results
          <Badge variant="secondary">{totalResults}</Badge>
        </CardTitle>
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onScrapeEmails}
            disabled={scraping}
          >
            {scraping ? <Loader2 className="animate-spin" /> : <Mail />}
            {scraping ? "Scraping..." : "Scrape emails"}
          </Button>
          <Button type="button" variant="accent" size="sm" onClick={onExport}>
            <Download />
            Export CSV
          </Button>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        <div className="w-full overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-border bg-secondary/60 text-left text-xs uppercase tracking-wide text-muted-foreground">
                <th className="px-3 py-3 font-medium">#</th>
                <th className="px-3 py-3 font-medium">Business</th>
                <th className="px-3 py-3 font-medium">Category</th>
                <th className="px-3 py-3 font-medium">Address</th>
                <th className="px-3 py-3 font-medium">City</th>
                <th className="px-3 py-3 font-medium">State</th>
                <th className="px-3 py-3 font-medium">Postcode</th>
                <th className="px-3 py-3 font-medium">Phone</th>
                <th className="px-3 py-3 font-medium">Email</th>
                <th className="px-3 py-3 font-medium">Website</th>
                <th className="px-3 py-3 font-medium">Maps</th>
                <th className="px-3 py-3 font-medium">Domain</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r, index) => (
                <tr
                  key={`${r.id}-${index}`}
                  className="border-b border-border last:border-0 hover:bg-secondary/40"
                >
                  <td className="px-3 py-3 text-muted-foreground">
                    {(page - 1) * PAGE_SIZE + index + 1}
                  </td>
                  <td className="px-3 py-3 font-medium text-foreground">{r.name}</td>
                  <td className="px-3 py-3 text-muted-foreground">
                    {r.category || "—"}
                  </td>
                  <td className="px-3 py-3 text-muted-foreground">{r.address || "—"}</td>
                  <td className="px-3 py-3">{r.city || "—"}</td>
                  <td className="px-3 py-3">
                    {r.state ? <Badge variant="outline">{r.state}</Badge> : "—"}
                  </td>
                  <td className="px-3 py-3 font-mono text-xs">{r.postcode || "—"}</td>
                  <td className="px-3 py-3 font-mono text-xs">{r.phone || "—"}</td>
                  <td className="px-3 py-3 font-mono text-xs">{r.email || "—"}</td>
                  <td className="px-3 py-3">
                    {r.website ? (
                      <a
                        href={r.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-primary hover:underline"
                      >
                        Visit <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td className="px-3 py-3">
                    {r.maps_url ? (
                      <a
                        href={r.maps_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-primary hover:underline"
                      >
                        <MapPin className="h-3.5 w-3.5" /> Map
                      </a>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td className="px-3 py-3 font-mono text-xs text-muted-foreground">
                    {r.domain || "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-2 border-t border-border p-4">
            <Button
              variant="outline"
              size="icon"
              onClick={() => onPageChange(1)}
              disabled={page === 1}
              aria-label="First page"
            >
              <ChevronsLeft />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={() => onPageChange(page - 1)}
              disabled={page === 1}
              aria-label="Previous page"
            >
              <ChevronLeft />
            </Button>
            <span className="px-2 text-sm text-muted-foreground">
              Page {page} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="icon"
              onClick={() => onPageChange(page + 1)}
              disabled={page === totalPages}
              aria-label="Next page"
            >
              <ChevronRight />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={() => onPageChange(totalPages)}
              disabled={page === totalPages}
              aria-label="Last page"
            >
              <ChevronsRight />
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
