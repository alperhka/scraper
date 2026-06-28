import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const EVENTBRITE_TOKEN = Deno.env.get("EVENTBRITE_TOKEN");
const EVENTBRITE_ORGANIZER_IDS_STR = Deno.env.get("EVENTBRITE_ORGANIZER_IDS") || Deno.env.get("EVENTBRITE_ORGANIZER_ID") || "32555819591,34351658429,34079879735,17387349944,17565780337,17684073356,42617718013,85750033103";
const EVENTBRITE_ORGANIZER_IDS = EVENTBRITE_ORGANIZER_IDS_STR.split(",").map(id => id.trim()).filter(id => id);

const SUPABASE_URL = Deno.env.get("PRODUCTION_SUPABASE_URL") || Deno.env.get("SUPABASE_URL");
const SUPABASE_SERVICE_KEY = Deno.env.get("PRODUCTION_SUPABASE_KEY") || Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

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

export async function fetchEventbriteEvents(organizerId: string) {
  if (!EVENTBRITE_TOKEN) {
    throw new Error("Missing Eventbrite EVENTBRITE_TOKEN configuration");
  }

  // Wir nutzen den public organizer events Endpunkt und expandieren venue und organizer
  const url = `https://www.eventbriteapi.com/v3/organizers/${organizerId}/events/?status=live&expand=venue,organizer`;
  
  const response = await fetch(url, {
    headers: {
      "Authorization": `Bearer ${EVENTBRITE_TOKEN}`,
    },
  });

  if (!response.ok) {
    // 404 und andere Fehler fangen wir ab, um zu loggen
    const text = await response.text();
    throw new Error(`Status ${response.status}: ${text}`);
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

export function assignTags(title: string, description: string): string[] {
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

export function mapEventbriteToSupabase(ebEvents: EventbriteEvent[]): PreparedEvent[] {
  return ebEvents.map((event) => {
    // Generiere source_hash auf Basis des Eventbrite-Titel + Startdatum + URL für einwandfreie Deduplizierung
    // (Analog zu den Python-Skripten)
    const title = event.name.text;
    const start_at = event.start.utc;
    const url = event.url;
    
    // Einfache Hash-Berechnung für Deno (MD5-Äquivalent für sauberen Abgleich)
    const hashInput = `${title}${start_at}${url}`;
    const hashBuffer = new TextEncoder().encode(hashInput);
    
    // Da crypto.subtle.digest in Edge-Funktionen async ist, nutzen wir hier einen synchronen Fallback
    // oder generieren einen eindeutigen ID-Hash, der mit dem Eventbrite-ID übereinstimmt:
    // Der sicherste und sauberste Weg für Deduplizierung über die API ist "eb_" + event.id
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
    console.log("🚀 Eventbrite Multi-Sync Edge Function started");

    if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
      throw new Error("Missing Supabase environment variables");
    }

    const allPreparedEvents: PreparedEvent[] = [];

    // Loop über alle Organizer IDs
    for (const organizerId of EVENTBRITE_ORGANIZER_IDS) {
      try {
        console.log(`🔄 Syncing organizer: ${organizerId}`);
        const data = await fetchEventbriteEvents(organizerId);
        const ebEvents = data.events || [];
        console.log(`   Found ${ebEvents.length} events for ${organizerId}`);

        const prepared = mapEventbriteToSupabase(ebEvents);
        allPreparedEvents.push(...prepared);
      } catch (err) {
        console.warn(`⚠️ Error syncing organizer ${organizerId}:`, err.message);
        // Wir fangen Fehler ab, damit andere Organizer trotzdem synchronisiert werden!
      }
    }

    console.log(`💾 Upserting ${allPreparedEvents.length} total events to Supabase...`);
    
    if (allPreparedEvents.length > 0) {
      const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);
      const { error } = await supabase
        .from("events_all")
        .upsert(allPreparedEvents, { onConflict: "source_hash" });

      if (error) throw error;
    }

    console.log("🎉 Eventbrite Multi-Sync completed successfully!");

    return new Response(
      JSON.stringify({
        success: true,
        count: allPreparedEvents.length,
        timestamp: new Date().toISOString(),
      }),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("❌ Fatal Error:", error.message);
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
});
