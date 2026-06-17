import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = "https://jnzdnkbmiednujyvhjms.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpuemRua2JtaWVkbnVqeXZoam1zIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjYwNzYyMCwiZXhwIjoyMDkyMTgzNjIwfQ.vvw1B3UST1tven2iWialCKfzeECS4k3rtKupOY1TXCQ"

try:
    supabase = create_client(url, key)
    # Get count and some samples
    response = supabase.table("events_all").select("title, source_name, start_at").limit(5).execute()
    count_res = supabase.table("events_all").select("id", count="exact").execute()
    
    print(f"Total events in DB: {count_res.count}")
    print("\nRecent samples:")
    for row in response.data:
        print(f"- {row['title']} (Source: {row['source_name']}, Start: {row['start_at']})")
except Exception as e:
    print(f"Error connecting: {e}")
