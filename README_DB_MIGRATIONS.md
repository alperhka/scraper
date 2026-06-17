DB Migrations / Backfill

Files:
- db_migrations/001_create_tags.sql  -> creates `tags` and `event_tags`, adds text_search column/index and source_hash index
- db_migrations/002_backfill_tags.sql -> backfills existing `events_all.tags` into normalized tables
- db_backfill_runner.py -> helper to run the SQL files against a Postgres connection

How to run (recommended):
1. Get a direct Postgres connection string from Supabase:
   - In Supabase Console: Project Settings -> Database -> Connection Pooling -> Connection string (or 'Connection Info').
   - Copy to `.env` as `SUPABASE_DB_URL=postgresql://...`

2. Install dependencies and run:
```bash
python3 -m pip install psycopg2-binary python-dotenv
python3 db_backfill_runner.py
```

Alternative: Open each SQL file in Supabase SQL Editor and run manually.

Notes:
- The runner is idempotent (uses ON CONFLICT DO NOTHING) so you can re-run safely.
- Make a DB backup before running on production.
