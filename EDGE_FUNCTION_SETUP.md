# 🚀 Supabase Edge Function - Deploy Anleitung

## Was ist diese Edge Function?

Das ist dein Python-Scraper, aber jetzt als **TypeScript/Deno** in Supabase.

- ✅ Läuft in der Cloud (nicht auf deinem Mac)
- ✅ Kann mit Webhook/Scheduler getriggert werden
- ✅ Kostenlos auf Supabase

## 📋 Voraussetzungen

1. **Supabase CLI installieren:**
```bash
brew install supabase/tap/supabase
```

2. **Supabase Projekt Setup:**
```bash
supabase link --project-ref jnzdnkbmiednujyvhjms
```

## 🔧 Setup-Schritte

### 1. Umgebungsvariablen setzen

Gehe zu: https://app.supabase.com → Dein Projekt → Settings → Secrets

Füge diese Secrets hinzu:
```
FIRECRAWL_KEY = dein_firecrawl_key
SUPABASE_SERVICE_ROLE_KEY = dein_service_role_key
```

### 2. Function lokal testen

```bash
cd /Users/alperredzepov/scraper
supabase functions serve scraper
```

Dann in neuem Terminal:
```bash
curl -X POST http://localhost:54321/functions/v1/scraper
```

### 3. Zu Supabase deployen

```bash
supabase functions deploy scraper --project-ref jnzdnkbmiedznjyvhjms
```

### 4. Scheduler einrichten (Cron-Like)

In Supabase Dashboard:
- **Database → Webhooks**
- **Create Webhook**
- URL: `https://jnzdnkbmiednujyvhjms.supabase.co/functions/v1/scraper`
- Events: (beliebig, nur für Trigger)

Oder mit `pg_cron`:
```sql
select
  cron.schedule(
    'scraper-daily',
    '0 9 * * *',  -- Daily at 9 AM
    $$select net.http_post(
      url:='https://jnzdnkbmiednujyvhjms.supabase.co/functions/v1/scraper',
      headers:='{"Content-Type": "application/json"}'::jsonb
    )$$
  );
```

## 🧪 Testen

```bash
# Response sollte so aussehen:
{
  "success": true,
  "message": "Scraping completed",
  "eventsFound": 3,
  "eventsInserted": 3,
  "timestamp": "2026-05-11T09:00:00.000Z"
}
```

## 📊 Logs ansehen

```bash
supabase functions logs scraper --project-ref jnzdnkbmiednujyvhjms
```

Oder im Dashboard: Functions → scraper → Logs

## 🔐 Sicherheit

- ✅ Secrets sind sicher gespeichert
- ✅ Keine Keys in Code
- ✅ Service Role Key nur im Secret

## 💡 Vorteile vs. Local Cron

| | Local Cron | Edge Function |
|---|---|---|
| Mac muss an sein | ✅ Ja | ❌ Nein |
| Zuverlässig | ⚠️ Manchmal | ✅ Immer |
| Kosten | ✅ Kostenlos | ✅ Kostenlos (Tier) |
| Einfach zu debuggen | ✅ Ja | ⚠️ Logs online |

## 🎯 Nächste Schritte

1. Supabase CLI installieren
2. Secrets in Supabase setzen
3. Function deployen
4. Scheduler konfigurieren
5. Lokale Cron deaktivieren (optional)

