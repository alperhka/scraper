-- 001_create_tags.sql
-- Create normalized tags tables and indexes

BEGIN;

-- tags master table
CREATE TABLE IF NOT EXISTS tags (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  created_at timestamptz DEFAULT now()
);

-- association table
CREATE TABLE IF NOT EXISTS event_tags (
  event_id uuid NOT NULL,
  tag_id uuid NOT NULL,
  created_at timestamptz DEFAULT now(),
  PRIMARY KEY (event_id, tag_id),
  FOREIGN KEY (event_id) REFERENCES events_all(id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- index for faster lookup
CREATE INDEX IF NOT EXISTS idx_events_all_source_hash ON events_all (source_hash);

-- full text search index (title + description)
ALTER TABLE events_all
  ADD COLUMN IF NOT EXISTS text_search tsvector;

CREATE INDEX IF NOT EXISTS idx_events_all_textsearch ON events_all USING GIN (text_search);

-- trigger to update text_search
CREATE FUNCTION events_all_trigger_tsvector() RETURNS trigger AS $$
BEGIN
  NEW.text_search := to_tsvector('german', coalesce(NEW.title,'') || ' ' || coalesce(NEW.description,''));
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'events_all_tsvector_update') THEN
    CREATE TRIGGER events_all_tsvector_update
    BEFORE INSERT OR UPDATE ON events_all
    FOR EACH ROW EXECUTE FUNCTION events_all_trigger_tsvector();
  END IF;
END$$;

COMMIT;
