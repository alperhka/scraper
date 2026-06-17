# Project: Scraper (SPD Tübingen)

Diese Datei enthält spezifische Anweisungen und Kontext für die Arbeit an diesem Projekt. Sie hilft mir (Gemini), die Architektur und deine bevorzugten Arbeitsweisen besser zu verstehen.

## Projektübersicht
Das Ziel dieses Projekts ist das Scraping von Veranstaltungen der SPD Tübingen (https://spd-tuebingen.de/) und deren Speicherung in einer Supabase-Datenbank.

Das Projekt besteht aus zwei Hauptkomponenten:
1. **Lokaler Scraper (`scraper.py`)**: Ein Python-Skript für manuelle oder lokale Ausführung.
2. **Edge Function (`supabase/functions/scraper/`)**: Eine Deno/TypeScript-Funktion für automatisiertes Scraping in der Supabase-Cloud.

## Architektur & Konventionen
- **Datenbank**: Alle Events werden in die Tabelle `events_all` in Supabase geschrieben.
- **Deduplizierung**: Verwendung eines `source_hash` (basierend auf Titel und Datum), um doppelte Einträge zu vermeiden.
- **Tools**:
    - **Firecrawl**: Wird in der Edge Function verwendet, um Markdown-Content zu erhalten.
    - **BeautifulSoup4**: Wird im lokalen Python-Scraper verwendet.

## Workflows
- **Testen**: Bevor Änderungen an der Edge Function gepusht werden, sollten sie lokal mit `supabase functions serve` (falls verfügbar) oder durch Analyse der Logik geprüft werden.
- **Dependencies**: 
    - Python-Pakete in `requirements.txt` aktuell halten.
    - Deno-Imports in der `index.ts` der Edge Function verwenden.

## Spezifische Anweisungen
- Achte beim Parsen darauf, dass Ort und Adresse sauber getrennt werden (oft im Format "Location - Adresse" im Markdown).
- Der `organizer` sollte standardmäßig auf "SPD Tübingen" gesetzt werden.
- Die Stadt ist primär "Tübingen".
