# 🤖 Automatisierung des Scrapers mit Cron (macOS)

## Cron-Job einrichten

### 1. Öffne Crontab
```bash
crontab -e
```
o
### 2. Füge eine dieser Zeilen hinzu:

#### Option A: **Täglich um 08:00 Uhr ausführen**
```
0 8 * * * /Users/alperredzepov/scraper/run_scraper.sh
```

#### Option B: **Alle 6 Stunden ausführen**
```
0 */6 * * * /Users/alperredzepov/scraper/run_scraper.sh
```

#### Option C: **Jeden Montag um 09:00 Uhr (für Wochenübersicht)**
```
0 9 * * 1 /Users/alperredzepov/scraper/run_scraper.sh
```

#### Option D: **Mehrmals täglich (08:00, 14:00, 20:00 Uhr)**
```
0 8,14,20 * * * /Users/alperredzepov/scraper/run_scraper.sh
```

### 3. Mit Logging (optional)

Für Debugging: Speichere Output in Log-Datei

```bash
# Erstelle Logs-Verzeichnis
mkdir -p /Users/alperredzepov/scraper/logs

# Dann in Crontab:
0 8 * * * /Users/alperredzepov/scraper/run_scraper.sh >> /Users/alperredzepov/scraper/logs/scraper.log 2>&1
```

## 📋 Crontab Syntax

```
┌───────────── Minute (0 - 59)
│ ┌───────────── Stunde (0 - 23)
│ │ ┌───────────── Tag des Monats (1 - 31)
│ │ │ ┌───────────── Monat (1 - 12)
│ │ │ │ ┌───────────── Wochentag (0 - 6) (0 = Sonntag)
│ │ │ │ │
│ │ │ │ │
* * * * *
```

## 🔍 Cron-Jobs überprüfen

```bash
# Alle Cron-Jobs auflisten
crontab -l

# Letzte Cron-Logs (macOS)
log stream --predicate 'process == "cron"' --level debug
```

## ❌ Cron-Job entfernen

```bash
# Öffne Crontab und lösche die Zeile
crontab -e
```

## 💡 Tipps

1. **Fehler debuggen:** Nutze Logging (siehe Option C oben)
2. **Test ausführen:** `bash /Users/alperredzepov/scraper/run_scraper.sh`
3. **PATH-Probleme:** In Crontab kann der PATH unterschiedlich sein
4. **Zeitzone:** Prüfe deine Systemzeitzone mit `date`

## 📌 Empfohlene Konfiguration

```bash
# Täglich um 9:00 Uhr mit Logging
0 9 * * * /Users/alperredzepov/scraper/run_scraper.sh >> /Users/alperredzepov/scraper/logs/scraper.log 2>&1
```

Nach dem Speichern (Ctrl+X, Y, Enter in nano/vim):
```bash
# Überprüfe dass der Job eingetragen ist
crontab -l
```
