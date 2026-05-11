# ⚡ Edge Function - Quick Start

## 1️⃣ Supabase CLI installieren (macOS)
```bash
brew install supabase/tap/supabase
```

## 2️⃣ Mit deinem Projekt verbinden
```bash
cd /Users/alperredzepov/scraper
supabase link --project-ref jnzdnkbmiednujyvhjms
```

## 3️⃣ Secrets in Supabase setzen

Gehe zu: https://app.supabase.com → Dein Projekt → Settings → Secrets

**Füge diese ein:**
```
FIRECRAWL_KEY = fc-140e7c9fa5a947e6b6a355fd38248769
SUPABASE_SERVICE_ROLE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpuemRua2JtaWVkbnVqeXZoam1zIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjYwNzYyMCwiZXhwIjoyMDkyMTgzNjIwfQ.vvw1B3UST1tven2iWialCKfzeECS4k3rtKupOY1TXCQ
```

## 4️⃣ Edge Function deployen
```bash
supabase functions deploy scraper --project-ref jnzdnkbmiednujyvhjms
```

## 5️⃣ Testen (lokal)
```bash
supabase functions serve scraper
```

Neues Terminal:
```bash
curl -X POST http://localhost:54321/functions/v1/scraper
```

## 6️⃣ Cron einrichten

**Option A: Mit pg_cron (einfach)**

Gehe zu: Supabase Dashboard → SQL Editor → New Query

```sql
select cron.schedule('scraper-daily', '0 9 * * *', $$
  select net.http_post(
    url:='https://jnzdnkbmiednujyvhjms.supabase.co/functions/v1/scraper',
    headers:='{"Content-Type": "application/json"}'::jsonb
  )
$$);
```

**Option B: Mit Webhook**

Dashboard → Database → Webhooks → Create

## ✅ Fertig!

Die Edge Function läuft jetzt täglich um 9:00 Uhr! 🚀

**Logs ansehen:**
```bash
supabase functions logs scraper --project-ref jnzdnkbmiednujyvhjms
```

