import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Konfiguration
URL = os.getenv("SUPABASE_URL") or "https://jnzdnkbmiednujyvhjms.supabase.co"
KEY = os.getenv("SUPABASE_KEY")

def check():
    try:
        supabase = create_client(URL, KEY)
        # Wir holen uns die ID und den Titel der letzten 5 Einträge aus events_all
        res = supabase.table("events_all").select("id, title, source_name").order("created_at", desc=True).limit(10).execute()
        
        print("\n--- Die letzten 10 Einträge in 'events_all' ---")
        if res.data:
            for i, row in enumerate(res.data):
                mark = "⭐" if row['source_name'] == "Eventbrite API" else "  "
                print(f"{mark} {i+1}. [{row['source_name']}] {row['title']}")
        else:
            print("Tabelle ist leer.")
            
    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    check()
