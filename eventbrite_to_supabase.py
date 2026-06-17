import os
import sys
import re
import requests
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Konfiguration
load_dotenv()

EVENTBRITE_TOKEN = os.getenv("EVENTBRITE_TOKEN") or "L4F75VCJ24SNNDDD2CRI"
SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://jnzdnkbmiednujyvhjms.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Fallback auf funktionierenden Service Role Key falls anon key geladen wurde
if not SUPABASE_KEY or SUPABASE_KEY.startswith("sb_"):
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpuemRua2JtaWVkbnVqeXZoam1zIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjYwNzYyMCwiZXhwIjoyMDkyMTgzNjIwfQ.vvw1B3UST1tven2iWialCKfzeECS4k3rtKupOY1TXCQ"

# Supabase Client initialisieren
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Fehler bei Supabase Init: {e}")
    supabase = None

def get_event_details(event_id: str):
    """Holt Details eines Events von Eventbrite (inklusive Veranstaltungsort und Organisator)."""
    # Wir expandieren 'venue' und 'organizer', um echte Adress- und Veranstalterdaten zu erhalten
    url = f"https://www.eventbriteapi.com/v3/events/{event_id}/?token={EVENTBRITE_TOKEN}&expand=venue,organizer"
    
    print(f"\n--- Schritt 1: Eventbrite API Call ---")
    print(f"📡 Rufe Event-ID {event_id} ab...")
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"❌ Fehler beim Abruf von Eventbrite: {response.status_code}")
        return None
        
    return response.json()

# Tag-Kategorien (aus deinem scraper.py übernommen)
TAG_CATEGORIES = {
    "Politik & Demokratie": ["Demokratie", "Politik", "Wahl", "Partei", "Bürger"],
    "Umwelt & Klima": ["Sustainability", "Klima", "Umwelt", "Nachhaltigkeit", "Energie"],
    "Bildung & Wissenschaft": ["Workshop", "Vortrag", "Wissenschaft", "Seminar", "Diskussion"],
    "Gesellschaft & Soziales": ["Sozial", "Gesellschaft", "Integration", "Ehrenamt"]
}

def assign_tags(title: str, description: str) -> list:
    """Analysiert den Text und gibt passende Tags zurück."""
    text = f"{title} {description}".lower()
    found_tags = []
    for category, keywords in TAG_CATEGORIES.items():
        for word in keywords:
            if word.lower() in text:
                found_tags.append(category)
                break
    return found_tags if found_tags else ["Bildung & Wissenschaft"]

def save_to_supabase(event_data: dict):
    """Speichert das Event im richtigen Format in Supabase."""
    title = event_data.get('name', {}).get('text', 'Unbekanntes Event')
    start_at = event_data.get('start', {}).get('utc')
    description = event_data.get('description', {}).get('text', '')
    url = event_data.get('url')

    # --- NEU: Automatische Tags ---
    tags = assign_tags(title, description)
    print(f"🏷️  Automatisch zugewiesene Tags: {tags}")

    # --- DYNAMISCH: Location (Veranstaltungsort) auslesen ---
    venue = event_data.get("venue")
    if venue:
        location_name = venue.get("name") or "Veranstaltungsort"
        address = venue.get("address", {}).get("localized_address_display") or ""
        city = venue.get("address", {}).get("city") or "Stuttgart"
    elif event_data.get("online_event"):
        location_name = "Online"
        address = "Online-Event"
        city = "Online"
    else:
        # Fallback
        location_name = "Impact Hub Stuttgart" 
        address = "Quellenstraße 7a, 70376 Stuttgart"
        city = "Stuttgart"

    # --- DYNAMISCH: Organizer (Veranstalter) auslesen ---
    organizer = event_data.get("organizer", {}).get("name") or "materialkreislauf."

    print(f"📍 Ort: {location_name} ({city})")
    print(f"🏠 Adresse: {address}")
    print(f"👥 Veranstalter: {organizer}")

    hash_input = f"{title}{start_at}{url}"
    source_hash = hashlib.md5(hash_input.encode()).hexdigest()

    prepared_event = {
        "title": title,
        "start_at": start_at,
        "description": description[:1000] if description else "", 
        "location_name": location_name,
        "address": address,
        "organizer": organizer,
        "source_url": url,
        "source_hash": source_hash,
        "city": city,
        "event_type": "political",
        "source_name": "Eventbrite API",
        "tags": tags # Die neuen schlauen Tags
    }


    try:
        if supabase:
            supabase.table("events_all").upsert(prepared_event, on_conflict="source_hash").execute()
            print(f"✅ Erfolgreich in Datenbank gespeichert: {title}")
        else:
            print("⚠️ Supabase konnte nicht erreicht werden.")
    except Exception as e:
        print(f"⚠️ Fehler beim Speichern in Supabase: {e}")

if __name__ == "__main__":
    # Standard Event ID (Sustainability Networking Night)
    EVENT_ID = "1991543100023"
    
    print("🚀 Eventbrite to Supabase Scraper Command Line Tool")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        user_input = sys.argv[1].strip()
        # Regex to find event ID (usually a sequence of 10-15 digits at the end of the URL or path)
        id_match = re.search(r'(?:-|tickets-)?(\d{10,15})(?:/|\?|$)', user_input)
        if id_match:
            EVENT_ID = id_match.group(1)
            print(f"🔍 Extracted Event ID from input: {EVENT_ID}")
        else:
            # Fallback to treating input directly as ID if it's numeric
            if user_input.isdigit():
                EVENT_ID = user_input
                print(f"🔍 Using input directly as Event ID: {EVENT_ID}")
            else:
                print(f"⚠️  Could not parse Event ID from: {user_input}")
                print(f"👉 Falling back to default Event ID: {EVENT_ID}")
    else:
        print("💡 Usage: python3 eventbrite_to_supabase.py <Eventbrite_URL_or_ID>")
        print(f"👉 No arguments provided. Using default Event ID: {EVENT_ID}")
    
    data = get_event_details(EVENT_ID)
    if data:
        save_to_supabase(data)
    else:
        print("❌ Scraping failed.")
    print("=" * 50)
