"""Address parsing for international formats (AU, US, UK, SA, and more)"""

# Recognized state codes (AU + US)
STATE_CODES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "VIC",
    "NSW",
    "QLD",
    "SA",
    "WA",
    "TAS",
    "NT",
    "ACT",
}

# Countries (last part of address) — used to skip
COUNTRIES = {
    "Australia",
    "USA",
    "United States",
    "UK",
    "United Kingdom",
    "Saudi Arabia",
    "Canada",
    "India",
    "UAE",
    "Germany",
    "France",
}


def parse_address(formatted_address):
    """Parse Google formatted address into (address_line, city, state, postcode)"""
    if not formatted_address:
        return "", "", "", ""

    parts = [p.strip() for p in formatted_address.split(",")]
    state = city = postcode = address_line = ""
    state_part_idx = None

    # Step 1: Try to find a recognized state code
    for i, part in enumerate(parts):
        tokens = part.strip().split()
        for s in STATE_CODES:
            if s in tokens:
                state = s
                state_part_idx = i
                for t in reversed(tokens):
                    if t.isdigit() and len(t) >= 4:
                        postcode = t
                        break
                same_part_city = " ".join(
                    t for t in tokens if t != s and not (t.isdigit() and len(t) >= 4)
                )
                if same_part_city:
                    city = same_part_city
                elif i > 0:
                    city = parts[i - 1]
                break
        if state_part_idx is not None:
            break

    # Step 2: Fallback — no state code found (e.g. Saudi Arabia, UK, etc.)
    if state_part_idx is None and len(parts) >= 2:
        # Last part is usually the country — skip it
        last_idx = len(parts) - 1
        if parts[last_idx].strip() in COUNTRIES:
            last_idx -= 1

        # Walk backwards to find the part with a postcode (4+ digits)
        for i in range(last_idx, 0, -1):
            tokens = parts[i].strip().split()
            found_postcode = None
            for t in reversed(tokens):
                if t.isdigit() and len(t) >= 4:
                    found_postcode = t
                    break
            if found_postcode:
                postcode = found_postcode
                city = " ".join(t for t in tokens if t != found_postcode)
                state_part_idx = i
                break

        # If still no postcode, use the second-to-last meaningful part as city
        if state_part_idx is None:
            for i in range(last_idx, 0, -1):
                tokens = parts[i].strip().split()
                all_num = all(t.isdigit() for t in tokens)
                if not all_num and tokens:
                    city = parts[i]
                    state_part_idx = i
                    break

    # Build address_line from parts before city/state
    if state_part_idx is not None and state_part_idx > 0:
        address_line = ", ".join(parts[:state_part_idx])

    return address_line, city, state, postcode
