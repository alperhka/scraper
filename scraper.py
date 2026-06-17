import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from supabase import create_client, Client

# Load environment variables
load_dotenv()

FIRECRAWL_KEY = os.getenv("FIRECRAWL_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Clients
firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_KEY)
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"⚠️  Supabase not connected: {e}")
    supabase = None

# Tag Categories Dictionary
TAG_CATEGORIES = {
    "Politik & Demokratie": [
        "Parteiveranstaltung", "Podiumsdiskussion", "Kommunalpolitik", "Bürgertreff",
        "politisch", "wahl", "demokratie", "regierung", "parlament", "bundestag", "landtag",
        "spd", "grüne", "fdp", "cdu", "csu", "linke", "afd"
    ],
    "Umwelt & Klima": [
        "Nachhaltigkeit", "Energie", "Tierschutz", "Mobilität",
        "klima", "umwelt", "co2", "kohlenstoff", "erneuerbar", "öko", "grün",
        "wald", "wasser", "luft", "verkehr", "auto", "fahrrad", "öffentlich"
    ],
    "Bildung & Wissenschaft": [
        "Vortrag", "Workshop", "Künstliche Intelligenz", "Ethik",
        "bildung", "wissenschaft", "forschung", "universität", "schule", "training",
        "seminar", "kurs", "ki", "ai", "technologie", "innovation", "kultur"
    ],
    "Gesellschaft & Soziales": [
        "Antidiskriminierung", "Integration", "Ehrenamt", "Menschenrechte",
        "sozial", "gesellschaft", "recht", "diskriminierung", "rechte", "integration",
        "migration", "flucht", "hilfe", "unterstützung", "gemeinde", "netzwerk"
    ],
    "Kultur & Protest": [
        "Politische Kunst", "Lesung", "Demonstration", "Filmabend",
        "kultur", "kunst", "musik", "film", "theater", "ausstellung", "lesung",
        "protest", "demonstration", "aktivismus", "aktion", "kampagne"
    ]
}

def assign_tags(title: str, description: str, organizer: str) -> List[str]:
    """
    Assigns relevant tags to an event based on title, description, and organizer.
    Returns a list of matching category tags.
    """
    text_to_analyze = f"{title} {description} {organizer}".lower()
    assigned_tags = []
    
    for category, keywords in TAG_CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in text_to_analyze:
                assigned_tags.append(category)
                break  # Only add category once per event
    
    # If no tags were assigned, default to "Bildung & Wissenschaft"
    if not assigned_tags:
        assigned_tags.append("Bildung & Wissenschaft")
    
    return assigned_tags

# New URLs to scrape
NEW_SOURCES = [
    {"name": "SPD Bund", "url": "https://www.spd.de/service/#m75572"},
    {"name": "Bündnis 90/Die Grünen Bund", "url": "https://www.gruene.de/termine"},
    {"name": "FDP Bund", "url": "https://www.fdp.de/termine"},
    {"name": "Friedrich-Ebert-Stiftung", "url": "https://www.fes.de/veranstaltungen"},
    {"name": "Amnesty Deutschland", "url": "https://www.amnesty.de/termine"}
]

# JSON Schema for AI-powered extraction
EVENT_SCHEMA = {
    "type": "object",
    "properties": {
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the event"},
                    "date": {"type": "string", "description": "Date and time (e.g. YYYY-MM-DD HH:MM)"},
                    "location": {"type": "string", "description": "Venue or city"},
                    "description": {"type": "string", "description": "Short summary"}
                },
                "required": ["title", "date"]
            }
        }
    }
}

def scrape_with_ai(source: Dict[str, str]) -> List[Dict[str, Any]]:
    """Uses Firecrawl's AI to extract events from any website structure."""
    print(f"\n🔍 Scrape: {source['name']} ({source['url']})")
    try:
        response = firecrawl_app.extract([source['url']], schema=EVENT_SCHEMA)
        
        # Access data attribute of the response object
        if hasattr(response, 'data') and response.data:
            events = response.data.get('events', [])
            print(f"✅ Found {len(events)} events")
            return events
        
        # Fallback for dict response
        if isinstance(response, dict) and 'data' in response:
            events = response['data'].get('events', [])
            print(f"✅ Found {len(events)} events")
            return events

        print(f"⚠️  No structured data extracted from {source['name']}")
        return []
    except Exception as e:
        print(f"❌ Error at {source['name']}: {e}")
        return []

def process_and_save(raw_events: List[Dict], source: Dict[str, str]):
    """Prepares and saves events to Supabase."""
    prepared = []
    for ev in raw_events:
        hash_input = f"{ev.get('title', '')}{ev.get('date', '')}{source['url']}"
        source_hash = hashlib.md5(hash_input.encode()).hexdigest()
        
        # Assign tags based on event content
        tags = assign_tags(
            ev.get("title", ""),
            ev.get("description", ""),
            source["name"]
        )

        prepared.append({
            "title": ev.get("title", "Unbenannt"),
            "start_at": ev.get("date"),
            "description": ev.get("description", ""),
            "location_name": ev.get("location", ""),
            "address": ev.get("location", ""),
            "organizer": source["name"],
            "source_url": source["url"],
            "source_hash": source_hash,
            "city": "Überregional" if "Bund" in source["name"] else "Tübingen",
            "event_type": "political",
            "source_name": "Firecrawl AI",
            "tags": tags
        })

    if prepared and supabase:
        try:
            supabase.table("events_all").upsert(prepared, on_conflict="source_hash").execute()
            print(f"💾 Saved {len(prepared)} events")
        except Exception as e:
            print(f"⚠️  Save error: {e}")

def main():
    print("🚀 Starting AI Multi-Scraper")
    for source in NEW_SOURCES:
        events = scrape_with_ai(source)
        if events:
            process_and_save(events, source)
    print("\n✨ All done!")

if __name__ == "__main__":
    main()
