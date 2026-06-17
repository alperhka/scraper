"""Run DB migrations/backfills against Supabase Postgres.

This script reads SQL files in db_migrations/ in lexical order and runs them.

Requires:
- psycopg2-binary
- SUPABASE_URL and SUPABASE_KEY in .env (SUPABASE_URL contains the project URL; this script expects a full Postgres connection string in SUPABASE_DB_URL if you have it)

If you don't have a direct Postgres URL, you can copy the SQL into Supabase SQL editor as an alternative.
"""
import os
import glob
from dotenv import load_dotenv

load_dotenv()

PG_CONNECTION = os.getenv('SUPABASE_DB_URL')  # Prefer full Postgres connection string
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not PG_CONNECTION:
    print('No SUPABASE_DB_URL found in .env. Please add the direct Postgres connection string (SUPABASE_DB_URL).')
    print('Alternatively, run the SQL files manually in Supabase SQL Editor.')
    exit(1)

import psycopg2

migrations = sorted(glob.glob(os.path.join(os.path.dirname(__file__), 'db_migrations', '*.sql')))

conn = psycopg2.connect(PG_CONNECTION)
conn.autocommit = True
cur = conn.cursor()

for m in migrations:
    print('Running', m)
    with open(m, 'r') as f:
        sql = f.read()
    try:
        cur.execute(sql)
        print('OK')
    except Exception as e:
        print('ERROR running', m, e)

cur.close()
conn.close()
print('Done')
