"""Google Places API scraping logic"""

import time

import requests
from address_parser import parse_address
from utils import clean_business_name, clean_url, get_root_domain

# Google Places API max per query
MAX_PER_PAGE = 20
MAX_PER_QUERY = 60

# Related keyword variations for generating extra queries
QUERY_EXPANSIONS = [
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

# Fields available from searchText (websiteUri and nationalPhoneNumber are NOT)
SEARCH_FIELDS = (
    "places.id,places.displayName,places.formattedAddress,"
    "places.primaryType,places.primaryTypeDisplayName,places.types,nextPageToken"
)

# Fields to fetch from Place Details
DETAILS_FIELDS = (
    "id,displayName,formattedAddress,websiteUri,nationalPhoneNumber,googleMapsUri"
)


def _fetch_place_details(api_key, place_id):
    """Fetch detailed info (website, phone) for a single place via Place Details."""
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": DETAILS_FIELDS,
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"      ⚠️  Details failed for {place_id}: {str(e)[:80]}")
        return {}


def _parse_place(place):
    """Parse a place object (from search or details) into our result dict."""
    address = place.get("formattedAddress", "")
    raw_name = place.get("displayName", {}).get("text", "")
    clean_name = clean_business_name(raw_name)
    address_line, city, state, postcode = parse_address(address)
    website = clean_url(place.get("websiteUri", ""))
    phone = place.get("nationalPhoneNumber", "")
    # Use human-readable display name (e.g., "Coffee shop" vs "coffee_shop")
    category = place.get("primaryType", "")
    display = place.get("primaryTypeDisplayName", {})
    if display and display.get("text"):
        category = display["text"]

    return {
        "id": place.get("id"),
        "name": clean_name,
        "address": address_line,
        "city": city,
        "state": state,
        "postcode": postcode,
        "phone": phone,
        "website": website,
        "domain": get_root_domain(website),
        "maps_url": f"https://www.google.com/maps/place/?q=place_id:{place.get('id', '')}",
        "category": category,
    }


def _run_single_query(api_key, query, location, max_results):
    """Run a single text query with pagination. Returns basic results (no website/phone)."""
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": SEARCH_FIELDS,
    }

    results = []
    seen_ids = set()
    page_token = None

    while len(results) < max_results:
        payload = {
            "textQuery": f"{query} in {location}",
            "maxResultCount": min(MAX_PER_PAGE, max_results - len(results)),
        }
        if page_token:
            payload["pageToken"] = page_token

        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        for place in data.get("places", []):
            pid = place.get("id")
            if pid in seen_ids:
                continue
            seen_ids.add(pid)
            results.append(_parse_place(place))

        page_token = data.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.5)

    return results


def _enrich_results_with_details(api_key, results):
    """Fetch Place Details for each result to get website and phone.
    Updates results in-place and returns only those with a website."""
    enriched = []
    for i, place in enumerate(results):
        pid = place.get("id")
        if not pid:
            continue

        print(
            f"      [{i + 1}/{len(results)}] Fetching details for {place['name'][:40]}..."
        )
        details = _fetch_place_details(api_key, pid)
        if details:
            # Merge detail fields into the existing result
            website = clean_url(details.get("websiteUri", ""))
            place["website"] = website or place.get("website", "")
            place["domain"] = get_root_domain(place["website"]) or place.get(
                "domain", ""
            )
            place["phone"] = details.get("nationalPhoneNumber") or place.get(
                "phone", ""
            )

        if place.get("website"):
            enriched.append(place)
        else:
            print("        ⛔ No website — skipped")

        time.sleep(0.2)  # Gentle rate limiting for Place Details calls

    return enriched


def search_places(api_key, query, location, limit=50, cities=None, state_code=None):
    """Search with multiple keywords, multi-city, and query expansions.
    Enriches results with Place Details (website + phone) after search."""
    keywords = [k.strip() for k in query.split(",") if k.strip()]
    city_list = cities if cities else [location.split()[0]]
    st = state_code or state_from_location(location)

    # --- Step 1: Search for places ---
    if len(keywords) > 1 or len(city_list) > 1:
        all_results = []
        seen_ids = set()
        total = len(keywords) * len(city_list)
        per_combo = max(5, limit // total)
        print(
            f"🔍 {len(keywords)} keywords × {len(city_list)} cities, ~{per_combo} each"
        )

        for kw in keywords:
            for ci, c in enumerate(city_list):
                if len(all_results) >= limit:
                    break
                city_loc = f"{c} {st}"
                before = len(all_results)
                _search_with_expansions(
                    api_key, kw, city_loc, per_combo * 2, seen_ids, all_results
                )
                added = len(all_results) - before
                if added:
                    print(f'  "{kw}" in {c}: +{added} → {len(all_results)} total')
                if len(all_results) >= limit:
                    break
                time.sleep(0.5)
            if len(all_results) >= limit:
                break

        print(f"✅ Step 1 done: {len(all_results)} places found")

        # --- Step 2: Enrich with Place Details ---
        print(
            f"🔎 Step 2: Fetching details (website + phone) for {len(all_results)} places…"
        )
        enriched = _enrich_results_with_details(api_key, all_results)
        print(f"✅ Step 2 done: {len(enriched)} places with websites")
        return _dedupe_by_domain(enriched, limit)

    # Single keyword, single city
    seen = set()
    basic_results = _search_with_expansions(api_key, keywords[0], location, limit, seen)
    print(f"✅ Step 1 done: {len(basic_results)} places found")

    print(f"🔎 Step 2: Fetching details for {len(basic_results)} places…")
    enriched = _enrich_results_with_details(api_key, basic_results)
    print(f"✅ Step 2 done: {len(enriched)} places with websites")
    return _dedupe_by_domain(enriched, limit)


def state_from_location(location):
    """Extract state code from location string like 'NSW (all cities)'"""
    return location.split()[0]


def _dedupe_by_domain(results, limit):
    """Remove duplicates by domain (first occurrence wins).
    Results without a domain are kept as-is."""
    seen = set()
    final = []
    for p in results:
        d = p.get("domain", "")
        if d:
            if d in seen:
                continue
            seen.add(d)
        final.append(p)
    return final[:limit]


def _search_with_expansions(
    api_key, query, location, limit, seen_ids, out_results=None
):
    """Run multiple query variations, aggregating results into out_results"""
    if out_results is None:
        out_results = []
    start = len(out_results)
    for template in QUERY_EXPANSIONS:
        if len(out_results) - start >= limit:
            break
        q = template.replace("{q}", query)
        remaining = min(MAX_PER_QUERY, limit - (len(out_results) - start))
        print(f'    Searching: "{q}" in {location} (limit {remaining})')
        batch = _run_single_query(api_key, q, location, remaining)
        new = 0
        for place in batch:
            key = place["domain"] or place["id"]
            if key in seen_ids:
                continue
            seen_ids.add(key)
            out_results.append(place)
            new += 1
        print(f"      → {new} new (total: {len(out_results)})")
        if new == 0 and len(out_results) > start:
            break
        if len(out_results) - start >= limit:
            break
        time.sleep(1)
    return out_results
