"""URL and domain utility functions"""

from urllib.parse import urlparse


def get_root_domain(url):
    """Extract root domain from URL"""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        hostname = parsed.netloc.lower()
        return hostname[4:] if hostname.startswith("www.") else hostname
    except:
        return ""


def clean_url(url):
    """Strip paths and tracking parameters, return root URL only"""
    if not url:
        return ""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}/"


def clean_business_name(raw_name):
    """Remove common suffixes from business names"""
    if not raw_name:
        return ""
    name = raw_name.strip()
    noise = [
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
    for n in noise:
        if name.endswith(n):
            name = name[: -len(n)].strip()
    return name
