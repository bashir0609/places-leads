import os, requests, webbrowser, time, csv, io, re
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load the API key from your .env file
load_dotenv()

def clean_url(url):
    """Strips tracking parameters (?utm...) from the website URL."""
    if not url: return ""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

def get_root_domain(url):
    """Extracts the root domain from a URL."""
    if not url: return ""
    try:
        parsed = urlparse(url)
        hostname = parsed.netloc.lower()
        if hostname.startswith("www."):
            hostname = hostname[4:]
        return hostname
    except:
        return ""

def parse_address(formatted_address):
    """
    Splits a Google formatted address into: address_line, city, state, postcode.
    Google typically returns: 'Street, Suburb VIC POSTCODE, Australia'
    """
    if not formatted_address:
        return "", "", "", ""
    
    parts = [p.strip() for p in formatted_address.split(",")]
    
    state = ""
    city = ""
    postcode = ""
    address_line = ""
    
    au_states = ["VIC", "NSW", "QLD", "SA", "WA", "TAS", "NT", "ACT"]
    
    # Find the part containing the state code
    state_part_idx = None
    for i, part in enumerate(parts):
        for s in au_states:
            if f" {s} " in f" {part} " or part.strip().upper().startswith(s + " "):
                state = s
                state_part_idx = i
                # Extract city and postcode from this segment
                # Example: "Greenacre NSW 2019" or "NSW 2019"
                remaining = part.replace(s, "").strip()
                tokens = remaining.split()
                
                # Last token is usually the postcode (4 digits for Australia)
                if tokens and tokens[-1].isdigit() and len(tokens[-1]) == 4:
                    postcode = tokens[-1]
                    city = " ".join(tokens[:-1]).strip()
                else:
                    city = remaining.strip()
                break
        if state_part_idx is not None:
            break
    
    # Address line = everything before the state part
    if state_part_idx is not None and state_part_idx > 0:
        address_line = ", ".join(parts[:state_part_idx])
    elif state_part_idx == 0:
        address_line = ""
    else:
        address_line = formatted_address  # Fallback

    return address_line, city, state, postcode

def clean_business_name(raw_name):
    """Strips common suffixes/noise from business names."""
    if not raw_name:
        return ""
    name = raw_name.strip()
    noise = [" - Victoria", " - VIC", " – Victoria", " – VIC", " | Victoria", 
             " - NSW", " - QLD", " - WA", " - SA", " - TAS", " - NT", " - ACT"]
    for n in noise:
        if name.endswith(n):
            name = name[: -len(n)].strip()
    return name

def scrape_emails_from_websites(results):
    """Visits each website & extracts a general email using regex. Updates results in-place."""
    for p in results:
        website = p.get("_website", "")
        if not website:
            p["_email"] = ""
            continue
        try:
            res = requests.get(website, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", res.text)
            p["_email"] = match.group(0).lower() if match else ""
            if p["_email"]:
                print(f"  📧 {p.get('_name', 'Unknown')}: {p['_email']}")
        except Exception as e:
            p["_email"] = ""
        time.sleep(1.5)  # Avoid IP blocks
    return results

def extract_hire_companies_au(query="equipment hire", limit=50):
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    url = "https://places.googleapis.com/v1/places:searchText"
    
    cities = [
        "Sydney NSW", "Melbourne VIC", "Brisbane QLD", "Perth WA", "Adelaide SA",
        "Gold Coast QLD", "Newcastle NSW", "Canberra ACT", "Hobart TAS", "Darwin NT",
        "Geelong VIC", "Sunshine Coast QLD", "Wollongong NSW", "Ballarat VIC", 
        "Townsville QLD", "Launceston TAS", "Bendigo VIC", "Toowoomba QLD"
    ]

    EXCLUDE_CHAINS = [
        "coates hire", "kennards hire", "onsite", "hewes hire", 
        "national plant hire", "scs group", "hirepool"
    ]

    all_results = []
    seen_ids = set()

    for city in cities:
        if len(all_results) >= limit:
            break
        print(f"🏙️ Searching: '{query}' in {city}... Found: {len(all_results)}")
        
        next_token = None
        for page in range(3):
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.websiteUri,places.nationalPhoneNumber,nextPageToken"
            }
            data = {"textQuery": f"{query} in {city}", "maxResultCount": 20}
            if next_token:
                data["pageToken"] = next_token

            try:
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()
                res_json = response.json()
                places = res_json.get("places", [])

                for p in places:
                    address = p.get("formattedAddress", "")
                    if "Australia" not in address:
                        continue

                    place_id = p.get("id")
                    if place_id in seen_ids:
                        continue
                        
                    raw_name = p.get("displayName", {}).get("text", "")
                    clean_name = clean_business_name(raw_name)
                    
                    if any(chain in clean_name.lower() for chain in EXCLUDE_CHAINS):
                        continue

                    address_line, city_parsed, state_parsed, postcode_parsed = parse_address(address)
                    website = clean_url(p.get("websiteUri", ""))
                    phone = p.get("nationalPhoneNumber", "")

                    # ✅ Use underscore-prefixed keys for consistency with output functions
                    p["_name"] = clean_name
                    p["_address_line"] = address_line
                    p["_city"] = city_parsed
                    p["_state"] = state_parsed
                    p["_postcode"] = postcode_parsed
                    p["_website"] = website
                    p["_phone"] = phone
                    p["_email"] = ""  # Will be filled by scraper
                    p["_root_domain"] = get_root_domain(website)
                    p["_notes"] = f"{query.replace(' in ', ' ')} | City: {city_parsed}"

                    all_results.append(p)
                    seen_ids.add(place_id)

                next_token = res_json.get("nextPageToken")
                if not next_token or len(all_results) >= limit:
                    break
                time.sleep(1.5)
            except Exception as e:
                print(f"❌ Error in {city}: {e}")
                break

    print(f"\n✅ Finished! Found {len(all_results)} unique hire companies.")
    return all_results

def build_csv_data(results):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["#", "Business Name", "Address", "City", "State", "Postcode", "Phone", "Website URL", "General Email", "Root Domain", "Notes"])
    for i, p in enumerate(results, 1):
        writer.writerow([
            i,
            p.get("_name", ""),
            p.get("_address_line", ""),
            p.get("_city", ""),
            p.get("_state", ""),
            p.get("_postcode", ""),  # ✅ Add this
            p.get("_phone", ""),
            p.get("_website", ""),
            p.get("_email", ""),
            p.get("_root_domain", ""),
            p.get("_notes", ""),
        ])
    return output.getvalue()

def save_and_open_results(results):
    filename = "au_hire_companies.html"
    csv_data = build_csv_data(results)

    rows_html = ""
    for i, p in enumerate(results, 1):
        name        = p.get("_name", "—")
        address     = p.get("_address_line", "—")
        city        = p.get("_city", "—")
        state       = p.get("_state", "—")
        postcode_val = p.get("_postcode", "—")
        website     = p.get("_website", "")
        root_domain = p.get("_root_domain", "—")
        email_val   = p.get("_email", "—")
        phone_val   = p.get("_phone", "—")
        
        website_cell = (
            f"<a href='{website}' target='_blank' style='color:#1a73e8;text-decoration:none;'>{website}</a>"
            f"<button onclick=\"navigator.clipboard.writeText('{website}'); this.innerText='✅'; setTimeout(() =>this.innerText='📋',1000)\""
            f"style='cursor:pointer;margin-left:8px;border:none;background:#e8f0fe;border-radius:4px;padding:2px 6px;font-size:11px;'>📋</button>"
        ) if website else "—"

        rows_html += f"""
        <tr>
            <td style='color:#94a3b8;font-size:12px;'>{i}</td>
            <td><strong>{name}</strong></td>
            <td style='color:#64748b;font-size:13px;'>{address}</td>
            <td>{city}</td>
            <td><span style='background:#dbeafe;color:#1d4ed8;padding:2px 7px;border-radius:99px;font-size:12px;font-weight:600;'>{state}</span></td>
            <td style='font-size:13px;'>{postcode_val}</td>
            <td style='font-size:13px;'>{phone_val}</td>
            <td style='font-size:12px;'>{website_cell}</td>
            <td style='font-size:12px; color:#059669;'>{email_val}</td>
            <td style='font-family:monospace;font-size:12px;color:#475569;'>{root_domain}</td>
            <td style='font-size:11px;color:#64748b;'>{p.get("_notes", "")}</td>
        </tr>
        """

    csv_escaped = csv_data.replace("\\", "\\\\").replace("`", "\\`")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Australian Hire Companies</title>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'DM Sans', sans-serif; background: #f8fafc; color: #0f172a; padding: 40px 32px; }}
        .header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 28px; flex-wrap: wrap; gap: 16px; }}
        .header h1 {{ font-size: 22px; font-weight: 600; display: flex; align-items: center; gap: 10px; }}
        .badge {{ background: #0f172a; color: #f8fafc; font-size: 13px; font-weight: 500; padding: 3px 10px; border-radius: 99px; }}
        .export-btn {{ background: #0f172a; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-family: 'DM Sans', sans-serif; font-size: 14px; font-weight: 500; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: background 0.15s; }}
        .export-btn:hover {{ background: #1e293b; }}
        .card {{ background: white; border-radius: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 4px 16px rgba(0,0,0,0.04); overflow: hidden; }}
        table {{ width: 100%; border-collapse: collapse; }}
        thead th {{ background: #0f172a; color: #94a3b8; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; padding: 12px 16px; text-align: left; white-space: nowrap; }}
        tbody tr {{ border-bottom: 1px solid #f1f5f9; transition: background 0.1s; }}
        tbody tr:last-child {{ border-bottom: none; }}
        tbody tr:hover {{ background: #f8fafc; }}
        td {{ padding: 12px 16px; font-size: 14px; vertical-align: middle; }}
        .search-bar {{ padding: 0 0 20px 0; }}
        .search-bar input {{ font-family: 'DM Sans', sans-serif; font-size: 14px; padding: 10px 16px; border: 1.5px solid #e2e8f0; border-radius: 8px; width: 320px; outline: none; transition: border-color 0.15s; }}
        .search-bar input:focus {{ border-color: #1a73e8; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>
            🇦🇺 Australian Hire Companies (Equipment • Construction • General)
            <span class="badge">{len(results)} results</span>
        </h1>
        <button class="export-btn" onclick="exportCSV()">⬇ Export CSV</button>
    </div>
    <div class="search-bar">
        <input type="text" id="searchInput" placeholder="🔍 Filter by name, city, domain..." oninput="filterTable()">
    </div>
    <div class="card">
        <table id="leadsTable">
            <thead>
                <tr>
                    <th>#</th><th>Business Name</th><th>Address</th><th>City</th><th>State</th><th>Postcode</th>
                    <th>Phone</th><th>Website URL</th><th>General Email</th><th>Root Domain</th><th>Notes</th>
                </tr>
            </thead>
            <tbody id="tableBody">{rows_html}</tbody>
        </table>
    </div>
    <script>
        const csvData = `{csv_escaped}`;
        function exportCSV() {{
            const blob = new Blob([csvData], {{ type: 'text/csv;charset=utf-8;' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url; a.download = 'au_hire_companies.csv'; a.click();
            URL.revokeObjectURL(url);
        }}
        function filterTable() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            const rows = document.querySelectorAll('#tableBody tr');
            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            }});
        }}
    </script>
</body>
</html>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    file_path = os.path.abspath(filename)
    webbrowser.open("file://" + file_path)
    print(f"✅ Table opened in browser: {filename}")

if __name__ == "__main__":
    # Run multiple targeted queries to reach 50 SMBs
    hire_queries = [
        "equipment hire",
        "construction hire yard", 
        "plant and machinery hire"
    ]
    
    all_leads = []
    for q in hire_queries:
        if len(all_leads) >= 50:
            break
        batch = extract_hire_companies_au(query=q, limit=50 - len(all_leads))
        all_leads.extend(batch)
        
    if all_leads:
        print("\n🔍 Scraping emails from websites...")
        all_leads = scrape_emails_from_websites(all_leads)
        save_and_open_results(all_leads)
    else:
        print("No results found. Verify your API Key and check 'Places API (New)' settings.")