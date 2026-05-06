#!/bin/bash
# Scraper-Wrapper für Cron-Jobs

cd /Users/alperredzepov/scraper

# Aktiviere Virtual Environment
source venv/bin/activate

# Führe Scraper aus
python scraper.py

# Optional: Log in Datei schreiben
# python scraper.py >> logs/scraper.log 2>&1
