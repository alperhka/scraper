# ✅ SPD Tübingen Events Scraper - Komplett Setup

## 🚀 Status

✅ **Scraper funktioniert vollständig!**

- ✅ Firecrawl scrapet https://spd-tuebingen.de/
- ✅ Events werden in Supabase `events_all` Tabelle gespeichert
- ✅ Service Role Key konfiguriert
- ✅ Fallback auf lokale JSON-Datei
- ✅ Automatisierung mit Cron bereit

## 📊 Was wurde gescrapt

**3 SPD-Events gefunden:**
- Roter Feierabend (Dienstag, 28. April 2026)
- Roter Feierabend (Dienstag, 26. Mai 2026)
- Roter Feierabend (Dienstag, 30. Juni 2026)

## 📁 Projektstruktur

```
/scraper/
├── scraper.py                # Hauptskript ✅
├── requirements.txt          # Python-Abhängigkeiten ✅
├── .env                       # Deine Secrets (nicht in Git) ✅
├── .env.example              # Template für .env ✅
├── .gitignore                # Git-Ausschlüsse ✅
├── run_scraper.sh            # Cron-Wrapper ✅
├── scraped_events.json       # Output (wenn Supabase offline) ✅
├── logs/                      # Cron-Logs ✅
├── venv/                      # Virtual Environment ✅
├── README.md                 # Setup-Anleitung
└── CRON_SETUP.md             # Cron-Konfiguration ✅
```

## 🔧 Schnellstart

### Virtual Environment aktivieren
```bash
cd /Users/alperredzepov/scraper
source venv/bin/activate
```

### Scraper manuell ausführen
```bash
python scraper.py
```

### Mit Bash-Wrapper ausführen (wie Cron macht)
```bash
bash run_scraper.sh
```

## 🤖 Automatisierung mit Cron

### Cron-Job einrichten (Täglich um 9:00 Uhr)
```bash
crontab -e
```

Füge diese Zeile ein:
```
0 9 * * * /Users/alperredzepov/scraper/run_scraper.sh >> /Users/alperredzepov/scraper/logs/scraper.log 2>&1
```

Speichern: `Ctrl+X`, `Y`, `Enter` (falls nano)

### Cron-Job überprüfen
```bash
crontab -l
```

### Logs ansehen
```bash
tail -f /Users/alperredzepov/scraper/logs/scraper.log
```

## 📊 Supabase Integration

**Tabelle:** `events_all`
**Auth:** Service Role Key (für Schreibzugriff)

**Spalten die gefüllt werden:**
- `title` - Event-Name
- `organizer` - "SPD Tübingen"
- `city` - "Tübingen"
- `source_url` - URL der Seite
- `source_name` - "SPD Tübingen Website"
- `event_type` - "political"
- `source_hash` - Für Deduplizierung
- `created_at` / `updated_at` - Automatisch

## 🔐 Sicherheit

✅ **API-Keys sind SICHER:**
- `.env` enthält echte Secrets
- `.gitignore` schließt `.env` aus
- `.env.example` hat nur Platzhalter
- Keine Keys im Git-Verlauf

## 📝 Nächste Schritte (Optional)

1. **Datum-Parsing verbessern** - Derzeit werden Daten geparst, aber nicht alle Felder gefüllt
2. **Mehr URLs scrapen** - Könnte mehrere SPD-Ortsverbände scrapen
3. **E-Mail Benachrichtigungen** - Bei neuen Events
4. **Dashboard** - Visualisierung der Events
5. **Cloud Deployment** - Scraper auf AWS/Cloud Function auslagern

## 📞 Troubleshooting

### Scraper startet nicht
```bash
source venv/bin/activate
python scraper.py
```

### Supabase-Fehler
Prüfe:
- Service Role Key in `.env` korrekt?
- Supabase URL korrekt?
- Tabelle `events_all` existiert?
- Genug Credentials?

### Cron funktioniert nicht
```bash
# Logs ansehen
log stream --predicate 'process == "cron"' --level debug

# Test manuell ausführen
/Users/alperredzepov/scraper/run_scraper.sh
```

## 🎯 Zusammenfassung

Du hast jetzt einen **vollständig automatisierten Web-Scraper**, der:

1. ✅ Die SPD-Website täglich scrapet
2. ✅ Events in Supabase speichert
3. ✅ Automatisch mit Cron läuft
4. ✅ Fehler elegant handhabt
5. ✅ Logs für Debugging speichert

**Genießen! 🎉**
