import os
import json
import re
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Initialize API keys and URLs from environment variables
FIRECRAWL_KEY = os.getenv("FIRECRAWL_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validate that all required environment variables are set
if not all([FIRECRAWL_KEY, SUPABASE_URL, SUPABASE_KEY]):
    print("⚠️  Warning: Some environment variables are missing")
    if not FIRECRAWL_KEY:
        raise ValueError("FIRECRAWL_KEY is required!")
    else:
        print("Continuing with Firecrawl only (Supabase will be skipped)")

# Initialize Firecrawl client
firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_KEY)

# Initialize Supabase client (with error handling)
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✓ Supabase connection established")
except Exception as e:
    print(f"⚠️  Supabase connection failed: {e}")
    print("Continuing without Supabase (dry-run mode)...")
    supabase = None

# JSON Schema for Firecrawl Extract
EVENT_SCHEMA = {
    "type": "object",
    "properties": {
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title or name of the event"
                    },
                    "event_date": {
                        "type": "string",
                        "description": "Date and time in format YYYY-MM-DD HH:MM"
                    },
                    "location": {
                        "type": "string",
                        "description": "Location or venue of the event"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the event"
                    }
                },
                "required": ["title"]
            }
        }
    }
}


def parse_events_from_markdown(markdown_content: str) -> list[dict]:
    """
    Parse events from markdown content extracted from the website.
    
    Args:
        markdown_content (str): The markdown content from Firecrawl
        
    Returns:
        list[dict]: List of parsed events
    """
    events = []
    
    # German month names
    month_map = {
        'januar': 1, 'februar': 2, 'märz': 3, 'april': 4,
        'mai': 5, 'juni': 6, 'juli': 7, 'august': 8,
        'september': 9, 'oktober': 10, 'november': 11, 'dezember': 12
    }
    
    lines = markdown_content.split('\n')
    
    current_event = None
    for i, line in enumerate(lines):
        # Match date pattern: **Dienstag, DD. Monat YYYY, HH:MM Uhr - HH:MM Uhr**
        date_match = re.search(
            r'\*\*(\w+,\s+(\d{1,2})\.\s+(\w+)\s+(\d{4})),\s+(\d{2}):(\d{2})\s+Uhr',
            line
        )
        
        if date_match:
            # Save previous event if exists
            if current_event and current_event.get('title'):
                events.append(current_event)
            
            day = int(date_match.group(2))
            month_str = date_match.group(3).lower()
            year = int(date_match.group(4))
            hour = int(date_match.group(5))
            minute = int(date_match.group(6))
            
            # Convert month name to number
            month = month_map.get(month_str, 1)
            
            # Format as ISO datetime
            try:
                dt = datetime(year, month, day, hour, minute)
                start_at = dt.isoformat()
            except ValueError:
                start_at = None
            
            current_event = {
                'title': '',
                'event_date': date_match.group(1),  # Store original date string too
                'start_at': start_at,
                'location': '',
                'description': ''
            }
        
        # Match event title (line starting with ###)
        elif line.startswith('### ') and current_event is not None:
            current_event['title'] = line.replace('### ', '').strip()
        
        # Match location (line with - and address)
        elif ' - ' in line and current_event is not None and not current_event['location']:
            # Look for venue name and address pattern
            parts = line.split(' - ')
            if len(parts) >= 2:
                venue = parts[0].strip().replace('**', '').replace('\\', '')
                address = parts[1].strip().replace('\\', '')
                current_event['location'] = f"{venue}, {address}"
        
        # Add description
        elif current_event is not None and line.strip() and not line.startswith('#'):
            if not current_event['description'] and not line.startswith('**'):
                current_event['description'] = line.strip()
            elif not line.startswith('**') and current_event['description']:
                # Append to description if not already set
                pass
    
    # Add the last event if exists
    if current_event and current_event.get('title'):
        events.append(current_event)
    
    return events


def scrape_political_events(url: str) -> list[dict]:
    """
    Scrape political events from the given URL using Firecrawl.

    Args:
        url (str): The URL to scrape (e.g., https://spd-tuebingen.de/)

    Returns:
        list[dict]: A list of extracted events
    """
    try:
        print(f"Starting to scrape events from: {url}")

        # Use Firecrawl's scrape with markdown
        response = firecrawl_app.scrape(
            url,
            formats=["markdown"]
        )

        print(f"Firecrawl response type: {type(response)}")
        
        # The response is a Document object with markdown attribute
        if hasattr(response, 'markdown') and response.markdown:
            markdown_content = response.markdown
            print(f"✓ Scraped {len(markdown_content)} chars of markdown")
            
            # Parse events from markdown
            events = parse_events_from_markdown(markdown_content)
            print(f"Found {len(events)} events")
            return events
        
        print("No markdown content found in the response")
        return []

    except Exception as e:
        print(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        # Fallback: return empty list instead of crashing
        return []


def prepare_event_data(events: list[dict], page_url: str) -> list[dict]:
    """
    Prepare event data for insertion into Supabase events_all table.

    Args:
        events (list[dict]): List of raw events from Firecrawl
        page_url (str): The URL of the page being scraped

    Returns:
        list[dict]: List of events formatted for Supabase insertion
    """
    prepared_events = []

    for event in events:
        # Create a hash for deduplication
        event_hash = hashlib.md5(
            f"{event.get('title', '')}{event.get('start_at', '')}".encode()
        ).hexdigest()

        prepared_event = {
            "title": event.get("title", ""),
            "description": event.get("description", ""),
            "start_at": event.get("start_at"),  # ISO format datetime
            "end_at": None,  # Not available from basic scraping
            "location_name": event.get("location", "").split(',')[0] if event.get("location") else "",
            "address": event.get("location", ""),
            "city": "Tübingen",  # Default city
            "postal_code": None,
            "latitude": None,
            "longitude": None,
            "organizer": "SPD Tübingen",  # Default organizer
            "event_type": "political",
            "source_name": "SPD Tübingen Website",
            "source_url": page_url,
            "image_url": None,
            "report_count": 0,
            "is_hidden": False,
            "source_hash": event_hash
        }
        prepared_events.append(prepared_event)

    return prepared_events


def insert_events_into_supabase(events: list[dict]) -> None:
    """
    Insert or upsert events into Supabase database, or save locally if not available.

    Args:
        events (list[dict]): List of events to insert
    """
    if not events:
        print("No events to insert")
        return

    if not supabase:
        print(f"Supabase not available. Saving {len(events)} events to JSON file...")
        save_events_to_file(events)
        return

    try:
        print(f"Inserting {len(events)} events into Supabase events_all...")

        # Use upsert to avoid duplicates based on source_hash
        response = supabase.table("events_all").upsert(
            events,
            on_conflict="source_hash"
        ).execute()

        print(f"✓ Successfully inserted/updated {len(events)} events in Supabase")

    except Exception as e:
        print(f"⚠️  Error inserting into Supabase: {e}")
        print(f"Falling back to local JSON file...")
        save_events_to_file(events)


def save_events_to_file(events: list[dict]) -> None:
    """
    Save events to a local JSON file.
    
    Args:
        events (list[dict]): List of events to save
    """
    try:
        output_file = "scraped_events.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved {len(events)} events to {output_file}")
    except Exception as e:
        print(f"Error saving events to file: {e}")


def main():
    """Main function to orchestrate the scraping process."""
    try:
        # Target URL for scraping
        target_url = "https://spd-tuebingen.de/"

        # Step 1: Scrape events from the URL
        raw_events = scrape_political_events(target_url)

        # Step 2: Prepare event data for database insertion
        prepared_events = prepare_event_data(raw_events, target_url)

        # Step 3: Insert events into Supabase
        insert_events_into_supabase(prepared_events)

        print("✓ Scraping process completed successfully!")

    except Exception as e:
        print(f"✗ Scraping process failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
