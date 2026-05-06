# Politischer Events Scraper - SPD Tübingen

Ein Python-Scraper zum Sammeln politischer Veranstaltungen der SPD Tübingen mit Firecrawl und Supabase.

## Anforderungen

- Python 3.9 oder höher
- macOS oder Linux
- Firecrawl API Key (https://app.firecrawl.dev)
- Supabase Projekt mit entsprechender Tabelle (https://app.supabase.com)

## Setup-Anleitung

### 1. Virtuelles Environment erstellen und aktivieren

```bash
# Im Projekt-Verzeichnis navigieren
cd /Users/alperredzepov/scraper

# Virtuelles Environment erstellen
python3 -m venv venv

# Virtual Environment aktivieren (macOS/Linux)
source venv/bin/activate
```

### 2. Abhängigkeiten installieren

```bash
# Pip aktualisieren (optional, aber empfohlen)
pip install --upgrade pip

# Alle erforderlichen Pakete installieren
pip install -r requirements.txt
```

### 3. Umgebungsvariablen konfigurieren

```bash
# .env.example kopieren und anpassen
cp .env.example .env

# .env öffnen und eigene API-Keys eintragen
# FIRECRAWL_KEY=dein_key_hier
# SUPABASE_URL=deine_url_hier
# SUPABASE_KEY=dein_key_hier
```

### 4. Supabase Tabelle erstellen

In der Supabase-Konsole folgende SQL ausführen:

```sql
CREATE TABLE political_events_bw (
  id BIGSERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  event_date VARCHAR(50),
  city VARCHAR(100),
  location VARCHAR(255),
  description TEXT,
  organizer VARCHAR(100),
  link VARCHAR(500),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(link)
);

CREATE INDEX idx_link ON political_events_bw(link);
CREATE INDEX idx_event_date ON political_events_bw(event_date);
```

### 5. Scraper ausführen

```bash
python scraper.py
```

## Projektstruktur

```
/scraper/
├── scraper.py          # Hauptskript für das Scraping
├── requirements.txt    # Python-Abhängigkeiten
├── .env               # Umgebungsvariablen (nicht committen!)
├── .env.example       # Template für Umgebungsvariablen
└── README.md          # Diese Datei
```

## Konfigurierbare Parameter

Folgende Parameter können angepasst werden:

- **TARGET_URL**: URL zum Scraping (Standard: `https://spd-tuebingen.de/`)
- **CITY**: Standardstadt für Veranstaltungen (Standard: "Tübingen")
- **ORGANIZER**: Standardorganisator (Standard: "SPD Tübingen")
- **EXTRACT_PROMPT**: Der Prompt für Firecrawl (angepasst für SPD-Events)

## Fehlerbehandlung

Das Skript beinhaltet:
- Validierung aller erforderlichen Umgebungsvariablen
- Fehlerbehandlung bei Firecrawl-Anfragen
- Fehlerbehandlung bei Supabase-Datenbankoperationen
- Aussagekräftige Fehlermeldungen für Debugging

## Sicherheit

⚠️ **Wichtig**: 
- Die `.env`-Datei enthält sensible Daten und sollte **NIEMALS** in Git committed werden
- Nutze `.env.example` als Template
- API-Keys sollten streng geheim gehalten werden

## Häufig gestellte Fragen

**Q: Kann ich den Scraper automatisiert ausführen lassen?**
A: Ja, nutze einen Cron-Job (macOS/Linux) oder Task Scheduler (Windows).

**Q: Wie verhindere ich Duplikate?**
A: Das Skript nutzt `UPSERT` mit `on_conflict="link"` - Datensätze mit gleichem Link werden aktualisiert.

**Q: Was ist das Extract-Schema?**
A: Es definiert die JSON-Struktur der extrahierten Daten für Firecrawl.
