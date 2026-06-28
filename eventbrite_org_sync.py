import os
import sys
import requests
import hashlib
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Logging konfigurieren
os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("eventbrite_org_sync")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File Handler
file_handler = logging.FileHandler("logs/eventbrite_sync.log", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 2. Konfiguration laden
load_dotenv()

EVENTBRITE_TOKEN = os.getenv("EVENTBRITE_TOKEN") or "L4F75VCJ24SNNDDD2CRI"

# Unterstützt sowohl eine einzelne ID als auch eine Komma-separierte Liste von IDs in der .env
organizer_ids_str = os.getenv("EVENTBRITE_ORGANIZER_IDS") or os.getenv("EVENTBRITE_ORGANIZER_ID") or "32555819591,17366367807"
EVENTBRITE_ORGANIZER_IDS = [oid.strip() for oid in organizer_ids_str.split(",") if oid.strip()]

SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://jnzdnkbmiednujyvhjms.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    logger.error(f"Fehler bei Supabase Initialisierung: {e}")
    supabase = None

# Tag-Kategorien (aus eventbrite_to_supabase.py übernommen)
TAG_CATEGORIES = {
    "Politik & Demokratie": ["Demokratie", "Politik", "Wahl", "Partei", "Bürger"],
    "Umwelt & Klima": ["Sustainability", "Klima", "Umwelt", "Nachhaltigkeit", "Energie"],
    "Bildung & Wissenschaft": ["Workshop", "Vortrag", "Wissenschaft", "Seminar", "Diskussion"],
    "Gesellschaft & Soziales": ["Sozial", "Gesellschaft", "Integration", "Ehrenamt"]
}

def assign_tags(title: str, description: str) -> list:
    """Analysiert Text und ordnet passende Tags zu."""
    text = f"{title} {description}".lower()
    found_tags = []
    for category, keywords in TAG_CATEGORIES.items():
        for word in keywords:
            if word.lower() in text:
                found_tags.append(category)
                break
    return found_tags if found_tags else ["Bildung & Wissenschaft"]

def fetch_all_organizer_events(organizer_id: str, token: str) -> list:
    """Ruft alle Live-Events des Veranstalters inkl. Venue & Organizer per Pagination ab."""
    events = []
    has_more = True
    page = 1
    
    logger.info(f"📡 Starte API-Abruf aller Events für Organizer-ID: {organizer_id}")
    
    while has_more:
        url = f"https://www.eventbriteapi.com/v3/organizers/{organizer_id}/events/?status=live&expand=venue,organizer&page={page}&token={token}"
        response = requests.get(url)
        
        if response.status_code != 200:
            logger.error(f"❌ Fehler beim Eventbrite API-Abruf (Seite {page}) für Organizer {organizer_id}: {response.status_code}")
            break
            
        data = response.json()
        page_events = data.get("events", [])
        events.extend(page_events)
        
        pagination = data.get("pagination", {})
        has_more = pagination.get("has_more_items", False)
        logger.info(f"   Seite {page} geladen ({len(page_events)} Events gefunden)")
        page += 1
        
    logger.info(f"✅ Insgesamt {len(events)} Events von Eventbrite API geladen für Organizer {organizer_id}.")
    return events

def sync_events():
    if not supabase:
        logger.error("❌ Keine Supabase-Verbindung. Sync abgebrochen.")
        return

    all_prepared_events = []

    for organizer_id in EVENTBRITE_ORGANIZER_IDS:
        logger.info(f"🔄 Starte Synchronisierung für Organizer-ID: {organizer_id}")
        raw_events = fetch_all_organizer_events(organizer_id, EVENTBRITE_TOKEN)
        if not raw_events:
            logger.warning(f"⚠️ Keine aktiven Events für Organizer {organizer_id} gefunden.")
            continue

        for ev in raw_events:
            title = ev.get('name', {}).get('text', 'Unbekanntes Event')
            start_at = ev.get('start', {}).get('utc')
            description = ev.get('description', {}).get('text', '')
            url = ev.get('url')
            
            tags = assign_tags(title, description)
            
            venue = ev.get("venue")
            if venue:
                location_name = venue.get("name") or "Veranstaltungsort"
                address = venue.get("address", {}).get("localized_address_display") or ""
                city = venue.get("address", {}).get("city") or "Tübingen"
            elif ev.get("online_event"):
                location_name = "Online"
                address = "Online-Event"
                city = "Online"
            else:
                location_name = "TBA"
                address = ""
                city = "Tübingen"

            organizer = ev.get("organizer", {}).get("name") or "Eventbrite"
            
            hash_input = f"{title}{start_at}{url}"
            source_hash = hashlib.md5(hash_input.encode()).hexdigest()

            all_prepared_events.append({
                "title": title,
                "start_at": start_at,
                "description": description[:1000] if description else "",
                "location_name": location_name,
                "address": address,
                "organizer": organizer,
                "source_url": url,
                "source_hash": source_hash,
                "city": city,
                "event_type": "eventbrite",
                "source_name": "Eventbrite API",
                "tags": tags
            })

    if all_prepared_events:
        logger.info(f"💾 Synchronisiere insgesamt {len(all_prepared_events)} Events mit der Supabase-Datenbank...")
        try:
            supabase.table("events_all").upsert(all_prepared_events, on_conflict="source_hash").execute()
            logger.info("🎉 Alle Events erfolgreich synchronisiert und in Supabase gespeichert!")
        except Exception as e:
            logger.error(f"❌ Fehler beim Schreiben in die Datenbank: {e}")
    else:
        logger.warning("⚠️ Keine aktiven Events zum Synchronisieren gefunden.")

if __name__ == "__main__":
    logger.info("🚀 Starte Eventbrite Full-Sync Pipeline")
    logger.info("=" * 50)
    sync_events()
    logger.info("=" * 50)
