"""Email extraction from business websites"""

import re
import time

import requests


def scrape_emails_from_websites(results):
    """Visit each website and extract contact email using regex.
    Updates results in-place with 'email' field."""
    for i, p in enumerate(results):
        website = p.get("website", "")
        if not website:
            p["email"] = ""
            continue

        try:
            print(f"  [{i + 1}/{len(results)}] Scraping: {website}")
            res = requests.get(
                website,
                timeout=8,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            )
            match = re.search(
                r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", res.text
            )
            p["email"] = match.group(0).lower() if match else ""
            if p["email"]:
                print(f"    📧 Found: {p['email']}")
            else:
                print(f"    ❌ No email found")
        except Exception as e:
            p["email"] = ""
            print(f"    ⚠️ Error: {str(e)[:80]}")

        time.sleep(0.5)  # Be respectful to websites

    return results
