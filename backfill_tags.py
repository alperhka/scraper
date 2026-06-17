import os
import hashlib
from typing import List, Dict, Any
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase connected")
except Exception as e:
    print(f"❌ Supabase connection failed: {e}")
    exit(1)

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

def backfill_tags():
    """Fetches all existing events and adds tags to them."""
    print("\n🔄 Starting backfill process...")
    
    try:
        # Fetch all events from the database
        response = supabase.table("events_all").select("*").execute()
        events = response.data
        
        print(f"📊 Found {len(events)} events to update")
        
        # Process each event
        updated_events = []
        for event in events:
            # Skip if event already has tags
            if event.get("tags") and len(event.get("tags", [])) > 0:
                print(f"⏭️  Skipping '{event['title']}' (already has tags)")
                continue
            
            # Assign tags
            tags = assign_tags(
                event.get("title", ""),
                event.get("description", ""),
                event.get("organizer", "")
            )
            
            event["tags"] = tags
            updated_events.append(event)
            print(f"✏️  Tagged '{event['title']}' → {tags}")
        
        # Upload updated events back to Supabase
        if updated_events:
            print(f"\n💾 Uploading {len(updated_events)} updated events...")
            supabase.table("events_all").upsert(updated_events).execute()
            print(f"✅ Successfully updated {len(updated_events)} events with tags!")
        else:
            print("⏭️  No events needed updating")
            
    except Exception as e:
        print(f"❌ Error during backfill: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Event Tags Backfill Tool")
    print("=" * 50)
    success = backfill_tags()
    print("=" * 50)
    if success:
        print("✨ Backfill complete!")
    else:
        print("⚠️  Backfill encountered errors")
