import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Fallback credentials matching eventbrite_to_supabase.py
URL = os.getenv("SUPABASE_URL") or "https://jnzdnkbmiednujyvhjms.supabase.co"
KEY = os.getenv("SUPABASE_KEY")

try:
    supabase = create_client(URL, KEY)
    # Suche gezielt nach dem Eventbrite-Eintrag
    response = supabase.table("events_all").select("*").eq("source_name", "Eventbrite API").execute()
    
    if response.data:
        print(f"✅ Gefunden! Es gibt {len(response.data)} Event(s) von Eventbrite in der DB.\n")
        for ev in response.data:
            print(f"📌 TITEL: {ev['title']}")
            print(f"   START: {ev['start_at']}")
            print(f"   ORT:   {ev['location_name']}")
            print(f"   URL:   {ev['source_url']}")
            print("-" * 30)
    else:
        print("❌ Kein Event von Eventbrite in der Datenbank gefunden.")

except Exception as e:
    print(f"❌ Fehler bei der Abfrage: {e}")

