-- Input is a reviewed snapshot of IDs, exact URLs, titles and existing labels.
WITH expected AS (
    SELECT * FROM jsonb_to_recordset(convert_from(decode('__REVIEWED_ROWS_BASE64__', 'base64'), 'UTF8')::jsonb)
        AS x(id bigint, url text, title text, team text, description text)
)
UPDATE public.team_jobs AS j
SET description = ''
FROM expected AS x
WHERE j.id = x.id AND j.url = x.url AND j.title = x.title AND j.team = x.team
    AND j.description = x.description AND j.platform = 'teamworkonline' AND j.is_active
    AND length(btrim(j.description)) > 0 AND length(btrim(j.description)) < 80
    AND lower(btrim(j.description)) IN (lower(btrim(j.team)), lower(btrim(j.company)))
RETURNING j.id, j.url;
