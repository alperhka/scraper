import { assertEquals, assertNotEquals } from "https://deno.land/std@0.168.0/testing/asserts.ts";
import { assignTags, mapEventbriteToSupabase } from "./index.ts";

// ==========================================
// TESTSUITE 1: AUTOMATISCHE TAG-ZUWEISUNG
// ==========================================

Deno.test("assignTags - Politik & Demokratie - prüft Schlüsselwörter", () => {
  const keywords = ["Demokratie", "Politik", "Wahl", "Partei", "Bürger"];
  for (const word of keywords) {
    const tags = assignTags(`Ein Event über ${word}`, "Beschreibung hier");
    assertEquals(tags.includes("Politik & Demokratie"), true, `Fehlgeschlagen für Keyword: ${word}`);
  }
});

Deno.test("assignTags - Umwelt & Klima - prüft Schlüsselwörter", () => {
  const keywords = ["Sustainability", "Klima", "Umwelt", "Nachhaltigkeit", "Energie"];
  for (const word of keywords) {
    const tags = assignTags("Titel", `Ein Event über ${word}`);
    assertEquals(tags.includes("Umwelt & Klima"), true, `Fehlgeschlagen für Keyword: ${word}`);
  }
});

Deno.test("assignTags - Bildung & Wissenschaft - prüft Schlüsselwörter", () => {
  const keywords = ["Workshop", "Vortrag", "Wissenschaft", "Seminar", "Diskussion"];
  for (const word of keywords) {
    const tags = assignTags(`Heute: ${word}`, "Ein tolles Bildungsangebot.");
    assertEquals(tags.includes("Bildung & Wissenschaft"), true, `Fehlgeschlagen für Keyword: ${word}`);
  }
});

Deno.test("assignTags - Gesellschaft & Soziales - prüft Schlüsselwörter", () => {
  const keywords = ["Sozial", "Gesellschaft", "Integration", "Ehrenamt"];
  for (const word of keywords) {
    const tags = assignTags("Titel", `Thema: ${word}`);
    assertEquals(tags.includes("Gesellschaft & Soziales"), true, `Fehlgeschlagen für Keyword: ${word}`);
  }
});

Deno.test("assignTags - Mehrfachzuweisung von Kategorien", () => {
  const tags = assignTags("Klimapolitik und Nachhaltigkeit", "Bürger wählen die Zukunft");
  assertEquals(tags.includes("Umwelt & Klima"), true);
  assertEquals(tags.includes("Politik & Demokratie"), true);
  assertEquals(tags.includes("Gesellschaft & Soziales"), true);
});

Deno.test("assignTags - Fallback zu Bildung & Wissenschaft", () => {
  const tags = assignTags("Konzert am Abend", "Musikalisches Beisammensein ohne Keywords");
  assertEquals(tags.length, 1);
  assertEquals(tags[0], "Bildung & Wissenschaft");
});


// ==========================================
// TESTSUITE 2: DATEN-MAPPING (EVENTBRITE -> SUPABASE)
// ==========================================

const mockEventbriteEvent = {
  id: "1234567890",
  name: { text: "Klimaschutz heute - Bürgerforum" },
  description: { text: "Eine offene Diskussion zur Zukunft der Energie in Tübingen." },
  start: { utc: "2026-10-15T18:00:00Z" },
  end: { utc: "2026-10-15T20:00:00Z" },
  url: "https://www.eventbrite.de/e/1234567890",
  organization_id: "org_987",
  logo: { url: "https://img.evbuc.com/logo.jpg" },
  venue: {
    name: "Bürgerhaus Tübingen",
    address: {
      localized_address_display: "Königstraße 1, 72072 Tübingen",
      city: "Tübingen"
    }
  },
  organizer: {
    name: "Ortsverband Tübingen"
  }
};

Deno.test("mapEventbriteToSupabase - Korrektes Mapping aller Felder", () => {
  const events = [mockEventbriteEvent as any];
  const mapped = mapEventbriteToSupabase(events);
  
  assertEquals(mapped.length, 1);
  const ev = mapped[0];
  
  assertEquals(ev.title, "Klimaschutz heute - Bürgerforum");
  assertEquals(ev.description, "Eine offene Diskussion zur Zukunft der Energie in Tübingen.");
  assertEquals(ev.start_at, "2026-10-15T18:00:00Z");
  assertEquals(ev.end_at, "2026-10-15T20:00:00Z");
  assertEquals(ev.source_url, "https://www.eventbrite.de/e/1234567890");
  assertEquals(ev.image_url, "https://img.evbuc.com/logo.jpg");
  
  // Deduplizierungs-Schlüssel (source_hash)
  assertEquals(ev.source_hash, "eb_1234567890");
  
  // Herkunfts-Daten
  assertEquals(ev.source_name, "Eventbrite API");
  assertEquals(ev.event_type, "eventbrite");
  
  // Standardwerte
  assertEquals(ev.is_hidden, false);
  assertEquals(ev.report_count, 0);
  
  // Location
  assertEquals(ev.location_name, "Bürgerhaus Tübingen");
  assertEquals(ev.address, "Königstraße 1, 72072 Tübingen");
  assertEquals(ev.city, "Tübingen");
  
  // Organizer
  assertEquals(ev.organizer, "Ortsverband Tübingen");
});

Deno.test("mapEventbriteToSupabase - Behandlung von fehlenden optionalen Werten (Fallback)", () => {
  const incompleteEvent = {
    id: "999999",
    name: { text: "Minimal-Event" },
    description: {},
    start: { utc: "2026-11-01T10:00:00Z" },
    end: { utc: "2026-11-01T12:00:00Z" },
    url: "https://www.eventbrite.de/e/999999",
    organization_id: "org_987"
  };
  
  const mapped = mapEventbriteToSupabase([incompleteEvent as any]);
  assertEquals(mapped.length, 1);
  const ev = mapped[0];
  
  assertEquals(ev.description, "");
  assertEquals(ev.image_url, null);
  assertEquals(ev.location_name, "TBA");
  assertEquals(ev.address, "");
  assertEquals(ev.city, "Tübingen");
  assertEquals(ev.organizer, "Eventbrite");
});
