-- 002_backfill_tags.sql
-- Backfill existing tags array from events_all into normalized tags & event_tags

BEGIN;

-- Insert unique tags into tags table
WITH all_tags AS (
  SELECT unnest(tags) as tag_name
  FROM events_all
  WHERE tags IS NOT NULL
), distinct_tags AS (
  SELECT DISTINCT tag_name FROM all_tags
)
INSERT INTO tags (name)
SELECT tag_name FROM distinct_tags
ON CONFLICT (name) DO NOTHING;

-- Insert event_tags relations
WITH tag_map AS (
  SELECT id, name FROM tags
), evt AS (
  SELECT id as event_id, unnest(tags) as tag_name
  FROM events_all
  WHERE tags IS NOT NULL
)
INSERT INTO event_tags (event_id, tag_id)
SELECT evt.event_id, tag_map.id
FROM evt
JOIN tag_map ON tag_map.name = evt.tag_name
ON CONFLICT (event_id, tag_id) DO NOTHING;

COMMIT;
