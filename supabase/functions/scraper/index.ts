import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const FIRECRAWL_KEY = Deno.env.get("FIRECRAWL_KEY");
const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
const SUPABASE_SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

interface ScrapedEvent {
  title: string;
  event_date?: string;
  location?: string;
  description?: string;
}

interface PreparedEvent {
  title: string;
  description: string;
  start_at: string | null;
  end_at: null;
  location_name: string;
  address: string;
  city: string;
  postal_code: null;
  latitude: null;
  longitude: null;
  organizer: string;
  event_type: string;
  source_name: string;
  source_url: string;
  image_url: null;
  report_count: number;
  is_hidden: boolean;
  source_hash: string;
  tags: string[];
}

// Parse events from markdown
function parseEventsFromMarkdown(markdownContent: string): ScrapedEvent[] {
  const events: ScrapedEvent[] = [];
  const monthMap: Record<string, number> = {
    januar: 1,
    februar: 2,
    märz: 3,
    april: 4,
    mai: 5,
    juni: 6,
    juli: 7,
    august: 8,
    september: 9,
    oktober: 10,
    november: 11,
    dezember: 12,
  };

  const lines = markdownContent.split("\n");
  let currentEvent: ScrapedEvent | null = null;

  for (const line of lines) {
    const dateMatch = line.match(
      /\*\*(\w+,\s+(\d{1,2})\.\s+(\w+)\s+(\d{4})),\s+(\d{2}):(\d{2})\s+Uhr/i
    );

    if (dateMatch) {
      if (currentEvent && currentEvent.title) {
        events.push(currentEvent);
      }

      const day = parseInt(dateMatch[2]);
      const monthStr = dateMatch[3].toLowerCase();
      const year = parseInt(dateMatch[4]);
      const hour = parseInt(dateMatch[5]);
      const minute = parseInt(dateMatch[6]);

      const month = monthMap[monthStr] || 1;

      try {
        const dt = new Date(year, month - 1, day, hour, minute);
        const startAt = dt.toISOString();

        currentEvent = {
          title: "",
          event_date: dateMatch[1],
          start_at: startAt,
          location: "",
          description: "",
        };
      } catch {
        currentEvent = {
          title: "",
          event_date: dateMatch[1],
          location: "",
          description: "",
        };
      }
    } else if (line.startsWith("### ") && currentEvent) {
      currentEvent.title = line.replace("### ", "").trim();
    } else if (line.includes(" - ") && currentEvent && !currentEvent.location) {
      const parts = line.split(" - ");
      if (parts.length >= 2) {
        const venue = parts[0].trim().replace(/\*\*/g, "").replace(/\\/g, "");
        const address = parts[1].trim().replace(/\\/g, "");
        currentEvent.location = `${venue}, ${address}`;
      }
    } else if (
      currentEvent &&
      line.trim() &&
      !line.startsWith("#") &&
      !currentEvent.description
    ) {
      currentEvent.description = line.trim();
    }
  }

  if (currentEvent && currentEvent.title) {
    events.push(currentEvent);
  }

  return events;
}

// Scrape events from URL using Firecrawl
async function scrapeEvents(url: string): Promise<ScrapedEvent[]> {
  try {
    console.log(`Scraping events from: ${url}`);

    const response = await fetch("https://api.firecrawl.dev/v1/scrape", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${FIRECRAWL_KEY}`,
      },
      body: JSON.stringify({
        url: url,
        formats: ["markdown"],
      }),
    });

    if (!response.ok) {
      throw new Error(`Firecrawl error: ${response.statusText}`);
    }

    const data = await response.json();
    console.log(`✓ Scraped ${data.data.markdown.length} chars`);

    const events = parseEventsFromMarkdown(data.data.markdown);
    console.log(`Found ${events.length} events`);

    return events;
  } catch (error) {
    console.error("Scraping error:", error);
    throw error;
  }
}

// Tag-Kategorien zur automatischen Zuordnung
const TAG_CATEGORIES: Record<string, string[]> = {
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
};

function assignTags(title: string, description: string, organizer: string): string[] {
  const textToAnalyze = `${title} ${description} ${organizer}`.toLowerCase();
  const assignedTags: string[] = [];
  
  for (const [category, keywords] of Object.entries(TAG_CATEGORIES)) {
    for (const keyword of keywords) {
      if (textToAnalyze.includes(keyword.toLowerCase())) {
        assignedTags.push(category);
        break;
      }
    }
  }
  
  if (assignedTags.length === 0) {
    assignedTags.push("Bildung & Wissenschaft");
  }
  
  return assignedTags;
}

// Prepare events for Supabase
function prepareEventData(
  events: ScrapedEvent[],
  pageUrl: string
): PreparedEvent[] {
  return events.map((event) => {
    // Create hash for deduplication
    const hashInput = `${event.title}${event.start_at || ""}`;
    const hashBuffer = new TextEncoder().encode(hashInput);

    // Simple hash function (not crypto, but good enough for deduplication)
    let hash = 0;
    const view = new Uint8Array(hashBuffer);
    for (let i = 0; i < view.length; i++) {
      hash = (hash << 5) - hash + view[i];
      hash = hash & hash; // Convert to 32bit integer
    }
    const sourceHash = Math.abs(hash).toString(16);

    const locationParts = event.location?.split(",") || [];
    const locationName = locationParts[0]?.trim() || "";

    const tags = assignTags(event.title || "", event.description || "", "SPD Tübingen");

    return {
      title: event.title || "",
      description: event.description || "",
      start_at: event.start_at || null,
      end_at: null,
      location_name: locationName,
      address: event.location || "",
      city: "Tübingen",
      postal_code: null,
      latitude: null,
      longitude: null,
      organizer: "SPD Tübingen",
      event_type: "political",
      source_name: "SPD Tübingen Website",
      source_url: pageUrl,
      image_url: null,
      report_count: 0,
      is_hidden: false,
      source_hash: sourceHash,
      tags: tags,
    };
  });
}

// Insert events into Supabase
async function insertEventsToSupabase(
  events: PreparedEvent[]
): Promise<number> {
  if (events.length === 0) {
    console.log("No events to insert");
    return 0;
  }

  try {
    const supabase = createClient(SUPABASE_URL!, SUPABASE_SERVICE_KEY!);

    console.log(`Inserting ${events.length} events into Supabase...`);

    const { data, error } = await supabase
      .from("events_all")
      .upsert(events, { onConflict: "source_hash" });

    if (error) {
      throw new Error(`Supabase error: ${error.message}`);
    }

    console.log(`✓ Successfully inserted/updated ${events.length} events`);
    return events.length;
  } catch (error) {
    console.error("Database error:", error);
    throw error;
  }
}

// Main handler
serve(async (req) => {
  try {
    console.log("🚀 Edge Function started");

    // Validate environment variables
    if (!FIRECRAWL_KEY || !SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
      throw new Error("Missing required environment variables");
    }

    const targetUrl = "https://spd-tuebingen.de/";

    // Step 1: Scrape events
    const rawEvents = await scrapeEvents(targetUrl);

    // Step 2: Prepare event data
    const preparedEvents = prepareEventData(rawEvents, targetUrl);

    // Step 3: Insert into Supabase
    const insertedCount = await insertEventsToSupabase(preparedEvents);

    console.log("✅ Edge Function completed successfully");

    return new Response(
      JSON.stringify({
        success: true,
        message: "Scraping completed",
        eventsFound: rawEvents.length,
        eventsInserted: insertedCount,
        timestamp: new Date().toISOString(),
      }),
      {
        headers: { "Content-Type": "application/json" },
        status: 200,
      }
    );
  } catch (error) {
    console.error("❌ Edge Function error:", error);

    return new Response(
      JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
        timestamp: new Date().toISOString(),
      }),
      {
        headers: { "Content-Type": "application/json" },
        status: 500,
      }
    );
  }
});
