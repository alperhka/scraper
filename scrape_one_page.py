import os
import sys
import hashlib
import os
import sys
import hashlib
from typing import List, Dict, Any
from dotenv import load_dotenv

# Optional Firecrawl
try:
    from firecrawl import FirecrawlApp
    FIRECRAWL_AVAILABLE = True
except Exception:
    FIRECRAWL_AVAILABLE = False

# Optional BeautifulSoup
try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

import requests
from supabase import create_client, Client

# Load .env
load_dotenv()

FIRECRAWL_KEY = os.getenv("FIRECRAWL_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Init supabase
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase connected")
except Exception as e:
    print(f"❌ Supabase connection failed: {e}")
    supabase = None

if FIRECRAWL_AVAILABLE and FIRECRAWL_KEY:
    firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_KEY)

TAG_CATEGORIES = {
    "Politik & Demokratie": [
        "Parteiveranstaltung", "Podiumsdiskussion", "Kommunalpolitik", "Bürgertreff",
        "politisch", "wahl", "demokratie", "regierung"
    ],
    "Umwelt & Klima": [
        "Nachhaltigkeit", "Energie", "Tierschutz", "Mobilität",
        "klima", "umwelt", "co2", "erneuerbar"
    ],
    "Bildung & Wissenschaft": [
        "Vortrag", "Workshop", "Künstliche Intelligenz", "Ethik",
        "bildung", "wissenschaft", "forschung", "universität"
    ],
    "Gesellschaft & Soziales": [
        "Antidiskriminierung", "Integration", "Ehrenamt", "Menschenrechte",
        "sozial", "gesellschaft"
    ],
    "Kultur & Protest": [
        "Politische Kunst", "Lesung", "Demonstration", "Filmabend",
        "kultur", "kunst", "protest"
    ]
}


def assign_tags(title: str, description: str, organizer: str) -> List[str]:
    text_to_analyze = f"{title} {description} {organizer}".lower()
    assigned: List[str] = []
    for category, keywords in TAG_CATEGORIES.items():
        for kw in keywords:
            if kw.lower() in text_to_analyze:
                assigned.append(category)
                break
    if not assigned:
        assigned.append("Bildung & Wissenschaft")
    return assigned


def extract_with_firecrawl(url: str) -> List[Dict[str, Any]]:
    if not (FIRECRAWL_AVAILABLE and FIRECRAWL_KEY):
        return []
    schema = {
        "type": "object",
        "properties": {
            "events": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "date": {"type": "string"},
                        "location": {"type": "string"},
                        "description": {"type": "string"}
                    }
                }
            }
        }
    }
    try:
        resp = firecrawl_app.extract([url], schema=schema)
        if hasattr(resp, 'data') and resp.data:
            return resp.data.get('events', [])
        if isinstance(resp, dict) and 'data' in resp:
            return resp['data'].get('events', [])
    except Exception as e:
        print(f"Firecrawl error: {e}")
    return []


def simple_extract(url: str) -> List[Dict[str, Any]]:
    if BeautifulSoup is None:
        print("BeautifulSoup not installed; simple extraction disabled.")
        return []
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"Request failed: {e}")
        return []
    soup = BeautifulSoup(r.text, 'html.parser')
    results: List[Dict[str, Any]] = []
    # Extract headings and their following paragraphs as potential events
    for h in soup.find_all(['h1', 'h2', 'h3']):
        title = h.get_text(strip=True)
        # find a nearby paragraph or time element
        desc = ''
        p = h.find_next_sibling()
        # collect a short description if available
        if p and getattr(p, 'get_text', None):
            desc = p.get_text(strip=True)
        if len(title) > 5:
            results.append({'title': title, 'description': desc, 'location': '', 'date': ''})
    return results


def upsert_events(events: List[Dict[str, Any]], source_url: str, source_name: str = 'one-page-scrape'):
    prepared = []
    for ev in events:
        h = hashlib.md5(f"{ev.get('title','')}{ev.get('date','')}{source_url}".encode()).hexdigest()
        tags = assign_tags(ev.get('title', ''), ev.get('description', ''), source_name)
        prepared.append({
            'title': ev.get('title', 'Untitled'),
            'start_at': ev.get('date', ''),
            'description': ev.get('description', ''),
            'location_name': ev.get('location', ''),
            'address': ev.get('location', ''),
            'organizer': source_name,
            'source_url': source_url,
            'source_hash': h,
            'city': 'Unknown',
            'event_type': 'unknown',
            'source_name': source_name,
            'tags': tags
        })
    if prepared and supabase:
        try:
            supabase.table('events_all').upsert(prepared, on_conflict='source_hash').execute()
            print(f"💾 Upserted {len(prepared)} events")
        except Exception as e:
            print(f"Supabase upsert error: {e}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scrape_one_page.py <URL>")
        sys.exit(1)
    url = sys.argv[1]
    print(f"Scraping: {url}")

    events: List[Dict[str, Any]] = []
    if FIRECRAWL_AVAILABLE and FIRECRAWL_KEY:
        events = extract_with_firecrawl(url)
        print(f"Firecrawl returned {len(events)} events")
    if not events:
        events = simple_extract(url)
        print(f"Simple extract found {len(events)} potential events")

    if events:
        upsert_events(events, url)
    else:
        print("No events found to upsert.")