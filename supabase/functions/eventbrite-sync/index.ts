import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const EVENTBRITE_TOKEN = Deno.env.get("EVENTBRITE_TOKEN");
const EVENTBRITE_ORG_ID = Deno.env.get("EVENTBRITE_ORG_ID");
const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
const SUPABASE_SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

interface EventbriteEvent {
  id: string;
  name: { text: string };
  description: { text: string };
  start: { utc: string };
  end: { utc: string };
  url: string;
  venue_id?: string;
  organization_id: string;
  logo?: { url: string };
}

interface PreparedEvent {
  title: string;
  description: string;
  start_at: string | null;
  end_at: string | null;
  location_name: string;
  address: string;
  city: string;
  organizer: string;
  event_type: string;
  source_name: string;
  source_url: string;
  image_url: string | null;
  source_hash: string;
  is_hidden: boolean;
  report_count: number;
  tags: string[];
}

async function fetchEventbriteEvents() {
  if (!EVENTBRITE_TOKEN || !EVENTBRITE_ORG_ID) {
    throw new Error("Missing Eventbrite configuration (TOKEN or ORG_ID)");
  }

  // Wir expandieren 'venue' und 'organizer', um echte Orts- und Veranstalterdaten abzurufen
  const url = `https://www.eventbriteapi.com/v3/organizations/${EVENTBRITE_ORG_ID}/events/?status=live&expand=venue,organizer`;
  
  const response = await fetch(url, {
    headers: {
      "Authorization": `Bearer ${EVENTBRITE_TOKEN}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(`Eventbrite API error: ${JSON.stringify(errorData)}`);
  }

  return await response.json();
}

// Tag-Kategorien (aus eventbrite_to_supabase.py übernommen)
const TAG_CATEGORIES: Record<string, string[]> = {
  "Politik & Demokratie": ["Demokratie", "Politik", "Wahl", "Partei", "Bürger"],
  "Umwelt & Klima": ["Sustainability", "Klima", "Umwelt", "Nachhaltigkeit", "Energie"],
  "Bildung & Wissenschaft": ["Workshop", "Vortrag", "Wissenschaft", "Seminar", "Diskussion"],
  "Gesellschaft & Soziales": ["Sozial", "Gesellschaft", "Integration", "Ehrenamt"]
};

function assignTags(title: string, description: string): string[] {
  const text = `${title} ${description}`.toLowerCase();
  const foundTags: string[] = [];
  for (const [category, keywords] of Object.entries(TAG_CATEGORIES)) {
    for (const word of keywords) {
      if (text.includes(word.toLowerCase())) {
        foundTags.push(category);
        break;
      }
    }
  }
  return foundTags.length > 0 ? foundTags : ["Bildung & Wissenschaft"];
}

function mapEventbriteToSupabase(ebEvents: EventbriteEvent[]): PreparedEvent[] {
  return ebEvents.map((event) => {
    // Generate source_hash based on Eventbrite ID for perfect deduplication
    const sourceHash = `eb_${event.id}`;
    
    const tags = assignTags(event.name.text, event.description.text || "");
    const organizer = (event as any).organizer?.name || "Eventbrite";

    return {
      title: event.name.text,
      description: event.description.text || "",
      start_at: event.start.utc,
      end_at: event.end.utc,
      location_name: (event as any).venue?.name || "TBA",
      address: (event as any).venue?.address?.localized_address_display || "",
      city: (event as any).venue?.address?.city || "Tübingen",
      organizer: organizer,
      event_type: "eventbrite",
      source_name: "Eventbrite API",
      source_url: event.url,
      image_url: event.logo?.url || null,
      source_hash: sourceHash,
      is_hidden: false,
      report_count: 0,
      tags: tags
    };
  });
}

serve(async (req) => {
  try {
    console.log("🚀 Eventbrite Sync started");

    if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
      throw new Error("Missing Supabase environment variables");
    }

    // 1. Fetch from Eventbrite
    const data = await fetchEventbriteEvents();
    const ebEvents = data.events || [];
    console.log(`Fetched ${ebEvents.length} events from Eventbrite`);

    // 2. Map to our schema
    const preparedEvents = mapEventbriteToSupabase(ebEvents);

    // 3. Upsert to Supabase
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);
    const { error } = await supabase
      .from("events_all")
      .upsert(preparedEvents, { onConflict: "source_hash" });

    if (error) throw error;

    return new Response(
      JSON.stringify({
        success: true,
        count: preparedEvents.length,
        timestamp: new Date().toISOString(),
      }),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("❌ Error:", error.message);
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
});
