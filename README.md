# 📅 Veranstaltungs-Scraper & Synchronisations-Plattform (Tübingen & Umland)

Dieses Projekt ist eine automatisierte Hybrid-Plattform zum Sammeln, Strukturieren und Speichern von politischen, gesellschaftlichen und akademischen Veranstaltungen in der Region Tübingen. Sie dient als Backend für ein Event-Portal und speichert alle Events dedupliziert in einer zentralen Supabase-Datenbank.

---

## 🏛️ System-Architektur & Datenfluss

Um eine maximale Abdeckung der Veranstaltungen zu gewährleisten, kombiniert das Projekt zwei unterschiedliche Datenquellen in einem **Dual-Track-Verfahren**:

```
                                  ┌────────────────────────┐
                                  │      Datenquellen      │
                                  └───────────┬────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
         [ 1. Webseiten-Scraping ]                         [ 2. Eventbrite-Schnittstelle ]
     Lokale Gliederungen / Aktivismus                     Stiftungen, Unis & Netzwerk-Hubs
  (z. B. FFF, SPD Tübingen, BUND-Websites)             (z. B. Uni Tübingen, FDP, SPD, Hubs)
                      │                                               │
                      ▼                                               ▼
            🚀 HTML/Markdown-Scraper                        ⚙️ Eventbrite API-Sync
            (Python / BeautifulSoup)                       (Deno Edge Function / API)
                      │                                               │
                      └───────────────────────┬───────────────────────┘
                                              │ (Deduplizierung per source_hash)
                                              ▼
                                 ┌─────────────────────────┐
                                 │   Supabase Datenbank    │
                                 │  (Tabelle: events_all)  │
                                 └─────────────────────────┘
```

---

## 📁 Projektstruktur & Hauptkomponenten

Das Projekt ist modular aufgebaut und trennt die lokalen Testskripte von den Cloud-basierten Produktionsfunktionen:

*   📂 **[supabase/functions/](file:///Users/alperredzepov/scraper/supabase/functions/)** - Serverless Cloud-Funktionen
    *   📂 **[eventbrite-sync/](file:///Users/alperredzepov/scraper/supabase/functions/eventbrite-sync/)** - Eventbrite-Synchronisations-Engine
        *   📄 **[index.ts](file:///Users/alperredzepov/scraper/supabase/functions/eventbrite-sync/index.ts)** - Deno Edge-Function für den automatischen Abruf mehrerer Veranstalter (inkl. Pagination, Tag-Zuweisung & robustem Error-Handling)
        *   📄 **[index_test.ts](file:///Users/alperredzepov/scraper/supabase/functions/eventbrite-sync/index_test.ts)** - Automatisierte Unit-Tests für Mappings und Tagging-Kategorien
    *   📂 **[scraper/](file:///Users/alperredzepov/scraper/supabase/functions/scraper/)** - Cloud-Scraping-Function für HTML-Quellen
*   📂 **[db_migrations/](file:///Users/alperredzepov/scraper/db_migrations/)** - SQL-Scripte zur Definition und Strukturierung der Datenbank
*   📄 **[eventbrite_org_sync.py](file:///Users/alperredzepov/scraper/eventbrite_org_sync.py)** - Lokaler Python-Zwilling der Eventbrite Edge Function (optimal für lokale Tests und Massenimporte)
*   📄 **[scraper.py](file:///Users/alperredzepov/scraper/scraper.py)** - Lokaler Python-Scraper für regionale Websites (BeautifulSoup4)
*   📄 **[.env](file:///Users/alperredzepov/scraper/.env)** - Konfigurationsdatei mit API-Schlüsseln (wird nicht committet!)

---

## 🔧 Lokales Setup

### 1. Python-Umgebung einrichten (für lokale Scraper-Skripte)
Erstelle eine virtuelle Python-Umgebung und installiere die Abhängigkeiten:
```bash
# In das Projektverzeichnis wechseln
cd /Users/alperredzepov/scraper

# Virtuelles Environment erstellen & aktivieren
python3 -m venv .venv
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

Führe den Eventbrite-Sync oder den HTML-Scraper lokal aus:
```bash
python eventbrite_org_sync.py
python scraper.py
```

### 2. Deno-Unit-Tests ausführen
Du kannst die TypeScript-Regeln für das Eventbrite-Mapping lokal validieren:
```bash
deno test --allow-env --allow-net supabase/functions/eventbrite-sync/index_test.ts
```

### 3. Edge-Functions lokal testen (mit Docker)
Um die Cloud-Funktionen vor dem Deployment lokal zu testen:
```bash
# Lokale Supabase-Dienste starten
supabase start

# Lokalen Server starten (lädt Variablen aus der .env)
supabase functions serve --env-file .env --no-verify-jwt

# Trigger die Funktion über einen neuen Terminal-Tab:
curl -i -X POST http://localhost:54321/functions/v1/eventbrite-sync
```

---

## 🚀 Deployment in die Produktion (Supabase Cloud)

Um das Projekt für den Endkunden einsatzbereit in der Cloud bereitzustellen, müssen zwei Schritte ausgeführt werden:

### 1. Umgebungsvariablen (Secrets) in der Cloud setzen
Lade deine API-Tokens und die Liste der Veranstalter-IDs auf den Supabase-Server hoch:
```bash
supabase secrets set EVENTBRITE_TOKEN=L4F75VCJ24SNNDDD2CRI \
  EVENTBRITE_ORGANIZER_IDS=32555819591,34351658429,34079879735,17387349944,17565780337,17684073356,42617718013,85750033103
```

### 2. Edge-Function deployen
Lade den neuesten Code in die Cloud hoch:
```bash
supabase functions deploy eventbrite-sync
```

Die Live-Funktion ist danach unter der folgenden URL erreichbar:
`https://jnzdnkbmiednujyvhjms.supabase.co/functions/v1/eventbrite-sync`

---

## ⚙️ Konfiguration & Pflege (Veranstalter erweitern)

Du kannst das Event-Netzwerk jederzeit erweitern, indem du neue Veranstalter-IDs (Organizer-IDs) von Eventbrite hinzufügst.

### Neue IDs ermitteln:
1. Öffne die Profilseite des gewünschten Veranstalters auf Eventbrite (z.B. der Landesverband einer Partei oder ein Kulturzentrum).
2. Kopiere die Ziffernkombination am Ende der URL (z.B. `17684073356` bei `eventbrite.de/o/universitat-tubingen-17684073356`).

### IDs hinzufügen:
* **Lokal:** Trage die ID mit einem Komma getrennt in deiner [.env](file:///Users/alperredzepov/scraper/.env)-Datei unter `EVENTBRITE_ORGANIZER_IDS` ein.
* **In der Cloud:** Richte das Secret über `supabase secrets set EVENTBRITE_ORGANIZER_IDS=...` erneut ein.

---

## 🛡️ Deduplizierung (source_hash)

Um zu verhindern, dass Veranstaltungen bei mehrfachen Durchläufen doppelt in die Datenbank geschrieben werden, besitzt jeder Datenbankeintrag ein eindeutiges `source_hash`-Feld. 
* Für Eventbrite wird dieses Feld generiert als: `eb_{event_id}`.
* Bei Änderungen eines Events überschreibt Supabase den bestehenden Eintrag (`UPSERT` auf `source_hash`), anstatt ein neues Event anzulegen.
