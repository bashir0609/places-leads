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


def _parse_place(place):
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
    """Run a single text query with pagination"""
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.websiteUri,places.nationalPhoneNumber,places.primaryType,places.primaryTypeDisplayName,places.types,nextPageToken",
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
            result = _parse_place(place)
            if result and result["website"]:  # Only include results with websites
                results.append(result)

        page_token = data.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.5)

    return results


def search_places(api_key, query, location, limit=50, cities=None, state_code=None):
    """Search with multiple keywords, multi-city, and query expansions."""
    keywords = [k.strip() for k in query.split(",") if k.strip()]
    city_list = cities if cities else [location.split()[0]]
    st = state_code or state_from_location(location)

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

        print(f"✅ Done: {len(all_results)} total")
        return all_results[:limit]

    # Single keyword, single city — use expansions directly
    seen = set()
    return _search_with_expansions(api_key, keywords[0], location, limit, seen)


def state_from_location(location):
    """Extract state code from location string like 'NSW (all cities)'"""
    return location.split()[0]


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
