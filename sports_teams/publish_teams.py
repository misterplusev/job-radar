#!/usr/bin/env python3
"""publish_teams.py — sports-team job announcements.

Embed contract copied field-for-field from the three existing scrapers:

    sportsbook  scripts/scrape.py::_discord_embed          color 0x38BDF8  footer "ABET Sportsbook Jobs Monitor"
    robotics    jobradar/publish.py::_embed                color 0x34D399  footer "ABET Robotics Jobs Monitor"
    tech        jobradar/publish.py::_embed                color 0x34D399  footer "ABET Tech Jobs Monitor"

Shared shape (all three): title[:256] · url[:2048] · description normalised to 350 chars with a
per-module fallback · fields [Source?, Company, Location, Posted?] inline · footer · timestamp
(posted_at or scraped_at or now) · thumbnail logo · 5 embeds per message · 2.1 s pacing · 429 retry.

Teams follow that exactly. Only the module strings differ, which is true of the three originals too:
    color 0x34D399 (the robotics/tech green) · footer "ABET Sports Teams Jobs Monitor"
    fallback "New team job discovered." · content "New team jobs discovered: N"

State: first run seeds (one summary + newest N, records everything as seen); later runs announce
only URLs not yet seen. DISCORD_WEBHOOK_TEAMS comes from E:\\abet\\.env.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROOFS = Path(r'D:\abet_ops\proofs')
STATE = ROOT / 'posted_state.json'
ENV = Path(r'E:\abet\.env')
STOP_FILE = Path(r'D:\abet_ops\STOP_ALL_AGENTS_MACHINE')

COLOR = 0x34D399
FOOTER = 'ABET Sports Teams Jobs Monitor'
CHUNK_SIZE = 5
PACE_SECONDS = 2.1
POSTED_DAYS_MAX = 14

CANONICAL_FILES = [
    'sports_teams_20261107.jsonl',
    'sports_teams_nfl_clubs_20261107.jsonl',
    'sports_teams_nba_20261107.jsonl',
    'sports_teams_mlb_20261107.jsonl',
    'sports_teams_mlb_round2_20261107.jsonl',
    'sports_teams_mlb_ultipro_20261108.jsonl',
    'sports_teams_mlb_adp_20261108.jsonl',
    'sports_teams_twork_orgs_20261109.jsonl',
]
DROP = ('asmglobal',)          # venue operator, not a club

LOGO_PATH = ROOT / 'team_logos.json'
LOGO_MAP = json.loads(LOGO_PATH.read_text(encoding='utf-8')) if LOGO_PATH.exists() else {}
LEAGUE_LOGOS = {lg: f'https://a.espncdn.com/i/teamlogos/leagues/500/{lg.lower()}.png'
                for lg in ('NFL', 'NBA', 'MLB', 'NHL')}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def guard():
    """Operator kill switch: never publish while the machine is parked."""
    if STOP_FILE.exists():
        raise SystemExit('STOP_ALL_AGENTS_MACHINE is set - not publishing')
    if os.environ.get('NOTIFICATIONS_PAUSED', '0') != '0':
        raise SystemExit('Notifications are paused by the operator guard')


def webhook() -> str:
    if os.environ.get('DISCORD_WEBHOOK_TEAMS'):
        return os.environ['DISCORD_WEBHOOK_TEAMS'].strip()
    for line in ENV.read_text(encoding='utf-8', errors='replace').splitlines():
        m = re.match(r'\s*DISCORD_WEBHOOK_TEAMS\s*=\s*(\S+)', line)
        if m:
            return m.group(1).strip().strip('"\'')
    raise SystemExit('DISCORD_WEBHOOK_TEAMS is not configured')


def _norm(value) -> str:
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', str(value or '')).lower())


_TAG = re.compile(r'<[^>]+>')
_REL_DAYS = re.compile(r'posted\s+(\d+)\+?\s+days?\s+ago', re.I)


def _clean_text(value) -> str:
    """Strip HTML entities/tags the way the other three modules do before posting."""
    import html as _html
    text = _html.unescape(str(value or ''))
    text = _TAG.sub(' ', text).replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', text).strip()


def _iso(value):
    """Return an employer-supplied absolute date; relative text is not a timestamp."""
    from datetime import timedelta
    raw = str(value or '').strip()
    if not raw:
        return None
    m = _REL_DAYS.search(raw)
    if m:
        return None
    low = raw.lower()
    if 'today' in low:
        return None
    if 'yesterday' in low:
        return None
    if re.match(r'^\d{4}-\d{2}-\d{2}', raw):
        return raw
    for fmt in ('%B %d, %Y', '%b %d, %Y', '%m/%d/%Y'):
        try:
            return datetime.strptime(re.sub(r'\s+', ' ', raw), fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _display_team(row) -> str:
    """'mariners' -> 'Seattle Mariners' using the ESPN name already resolved for the logo."""
    team = str(row.get('team') or '').strip()
    league = (row.get('league') or '').upper()
    key = _norm(team)
    if not key:
        return team or 'Unknown'
    for k, meta in LOGO_MAP.items():
        k_league, _, k_team = k.partition(':')
        if league and k_league != league:
            continue
        kt = _norm(k_team)
        if kt == key or kt.endswith(key):
            return meta.get('espn_name') or k_team
    return team


def logo_for(row):
    """Match a scraped team label ('marlins', 'Astros', 'Miami Dolphins') to an ESPN logo."""
    league = (row.get('league') or '').upper()
    team = _norm(row.get('team'))
    if league and (not team or 'leagueoffice' in team):
        return LEAGUE_LOGOS.get(league)
    if not team:
        return None
    best = None
    for key, meta in LOGO_MAP.items():
        key_league, _, key_team = key.partition(':')
        if league and key_league != league:
            continue
        kt = _norm(key_team)
        if kt == team:
            return meta['logo']
        if not best and (team in kt or kt.endswith(team)):
            best = meta['logo']
    return best


def load_legacy_rows():
    rows, seen = [], set()
    for name in CANONICAL_FILES:
        p = PROOFS / name
        if not p.exists():
            continue
        for line in p.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if any(d in json.dumps(r).lower() for d in DROP):
                continue
            if not r.get('league'):
                portal = (r.get('portal') or '') + ' ' + (r.get('url') or '')
                if 'football-jobs' in portal:
                    r['league'] = 'NFL'
                elif 'hockey-jobs' in portal:
                    r['league'] = 'NHL'
                elif 'baseball-jobs' in portal:
                    r['league'] = 'MLB'
                elif 'basketball-jobs' in portal:
                    r['league'] = 'NBA'
            key = (r.get('team') or '', r.get('url') or '')
            if not key[1] or key in seen:
                continue
            seen.add(key)
            rows.append(r)
    return rows


def load_rows():
    """Read active tracked observations; historical files are bootstrap only."""
    import sqlite3
    db = ROOT / 'data' / 'team_jobs.db'
    if not db.exists():
        return load_legacy_rows()
    with sqlite3.connect(db.as_uri() + '?mode=ro', uri=True) as con:
        con.row_factory = sqlite3.Row
        rows = [dict(r) for r in con.execute('select * from team_jobs where is_active=1')]
    seen = set()
    unique = []
    for row in rows:
        if row['url'] not in seen:
            row['scraped_at'] = row.get('last_seen_at')
            unique.append(row)
            seen.add(row['url'])
    return unique


def load_state():
    if os.environ.get('SUPABASE_SERVICE_ROLE_KEY'):
        from cloud_storage import CloudStorage
        return CloudStorage().notification_state()
    if STATE.exists():
        return json.loads(STATE.read_text(encoding='utf-8'))
    return {'schema': 'abet.teams.posted.v1', 'seen': [], 'posted_at': None, 'posts': 0}


def save_state(state):
    if os.environ.get('SUPABASE_SERVICE_ROLE_KEY'):
        from cloud_storage import CloudStorage
        CloudStorage().save_notification_state(state)
        return
    STATE.write_text(json.dumps(state, indent=1), encoding='utf-8')


def _is_recent(value) -> bool:
    if not value:
        return False
    try:
        dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt >= datetime.now(timezone.utc) - __import__('datetime').timedelta(days=POSTED_DAYS_MAX)
    except (ValueError, TypeError):
        return False


def embed(row: dict) -> dict:
    """Field-for-field copy of the three existing scrapers' embed."""
    from urllib.parse import urlsplit
    target=urlsplit(str(row.get('url') or ''))
    if target.scheme not in ('http','https') or not target.netloc:
        raise ValueError('Refusing notification without a public job URL')
    if target.netloc.endswith('.myworkdayjobs.com') and re.match(r'^/(?:[a-z]{2}-[A-Z]{2}/)?job/',target.path):
        raise ValueError('Refusing Workday job URL without its career-site name')
    description = _clean_text(row.get('description'))
    if len(description) > 350:
        description = description[:347] + '...'
    posted_iso = _iso(row.get('posted_at'))
    item = {
        'title': _clean_text(row.get('title'))[:256] or 'New team job posting',
        'url': (str(row.get('url') or ''))[:2048] or None,
        'description': description or 'New team job discovered.',
        'color': COLOR,
        'fields': [
            {'name': 'Company', 'value': _display_team(row)[:256], 'inline': True},
            {'name': 'Location', 'value': _clean_text(row.get('location'))[:1024] or 'Unknown', 'inline': True},
        ],
        'footer': {'text': FOOTER},
        'timestamp': now_iso(),
    }
    platform = row.get('platform')
    if platform:
        item['fields'].insert(0, {'name': 'Source', 'value': str(platform)[:256], 'inline': True})
    if posted_iso:
        item['fields'].append({'name': 'Posted', 'value': posted_iso[:256], 'inline': True})
    logo = logo_for(row)
    if logo:
        item['thumbnail'] = {'url': logo}
    return item


def notify(webhook_url: str, payload: dict, attempts: int = 8) -> bool:
    body = json.dumps(payload).encode()
    for i in range(attempts):
        guard()
        req = urllib.request.Request(webhook_url, data=body, method='POST',
                                     headers={'Content-Type': 'application/json',
                                              'User-Agent': 'ABET-TeamsJobs/1.0',
                                              **({'Authorization':'Bearer '+os.environ['DISCORD_RELAY_TOKEN']} if os.environ.get('DISCORD_RELAY_TOKEN') else {})})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status in (200, 204)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                try:
                    wait = float(json.loads(e.read().decode()).get('retry_after', PACE_SECONDS))
                except Exception:
                    wait = PACE_SECONDS
                print(f'  429, waiting {wait:.1f}s')
                time.sleep(min(max(wait,1),30))
                continue
            print(f'  HTTP {e.code}: {e.read().decode()[:160]}')
            return False
        except Exception as e:
            print(f'  ERR {type(e).__name__}: {e}')
            time.sleep(2 * (i + 1))
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--seed', action='store_true')
    ap.add_argument('--post', action='store_true')
    ap.add_argument('--baseline', action='store_true',help='Explicit one-time catch-up summary; archive existing URLs as seeded, not individually delivered')
    ap.add_argument('--preview', action='store_true', help='post the newest N regardless of state')
    ap.add_argument('--limit', type=int, default=10,help='Job limit; 0 processes every eligible job within the delivery time budget')
    ap.add_argument('--show-payload', action='store_true')
    args = ap.parse_args()

    rows = load_rows()
    state = load_state()
    seen = set(state.get('seen') or [])
    if args.baseline:
        payload={'content':('**Sports Teams Jobs — coverage repaired**\n'
            f'{len(rows):,} active listings are available on the [full job board](https://misterplusev.github.io/job-radar/). '
            'The scraper now has a working employer source for all 124 NFL, NBA, MLB and NHL teams. '
            '[Review coverage and remaining alternate-link errors](https://misterplusev.github.io/job-radar/coverage.html).\n'
            'Existing listings remain searchable on the board. Individual alerts will cover newly discovered jobs from here forward.')}
        if args.dry_run:
            print(json.dumps(payload,ensure_ascii=False));print('Would baseline',len({r['url'] for r in rows}-seen),'existing URLs; no messages sent.');return 0
        guard()
        if not notify(webhook(),payload):return 1
        baseline={r['url'] for r in rows}-seen
        state.update(seen=sorted(seen|baseline),baseline_urls=sorted(baseline),posted_at=now_iso(),posts=int(state.get('posts') or 0)+1)
        save_state(state)
        print('Catch-up summary delivered; existing jobs recorded as seeded, not individually delivered.');return 0
    fresh = [r for r in rows if r['url'] not in seen]
    fresh.sort(key=lambda r: (str(r.get('posted_at') or r.get('first_seen_at') or ''),r['url']), reverse=True)
    if args.preview:
        fresh = sorted(rows, key=lambda r: str(r.get('posted_at') or ''), reverse=True)

    print(f'rows={len(rows)}  already_seen={len(seen)}  fresh={len(fresh)}')
    if not fresh:
        print('nothing new')
        return 0

    eligible = fresh if args.preview else [r for r in fresh if _is_recent(r.get('posted_at'))
                  or (not r.get('posted_at') and _is_recent(r.get('first_seen_at')))]
    if args.limit<0:ap.error('--limit must be nonnegative')
    to_post = eligible if args.limit==0 else eligible[:args.limit]
    if not to_post:
        print('No newly observed/recently posted jobs eligible for notification.')
        return 0

    if args.show_payload:
        print(json.dumps(embed(to_post[0]), indent=2, ensure_ascii=False))
        if args.dry_run:
            return 0

    if args.dry_run:
        for r in to_post:
            print(f'  DRY [{r.get("league")}] {r.get("title")} | {r.get("team")} | {r.get("url")}')
        print(f'{len(to_post)} would post; {len(fresh) - len(to_post)} held back by --limit')
        return 0

    if not (args.post or args.seed or args.preview):
        print('No publishing mode selected; use --dry-run or explicitly --post.')
        return 0

    guard()
    hook = webhook()
    ok = 0
    delivered = set()
    summary_ok = False
    starting_posts=int(state.get('posts') or 0)
    delivery_started=time.monotonic()
    if args.seed:
        summary = (f'**Sports Teams Jobs — scraper online**\n'
                   f'{len(rows)} active postings across {len({r.get("team") for r in rows})} team sources. '
                   f'Announcing the {len(to_post)} newest now; from here only genuinely new postings.')
        if notify(hook, {'content': summary}):
            summary_ok = True
            ok += 1
            print('  posted summary')
        time.sleep(PACE_SECONDS)

    for idx in range(0, len(to_post), CHUNK_SIZE):
        if time.monotonic()-delivery_started>=600:
            print('Delivery time budget reached; unsent URLs remain queued.');break
        chunk = to_post[idx:idx + CHUNK_SIZE]
        payload = {'content': f'New team jobs discovered: {len(chunk)}',
                   'embeds': [embed(r) for r in chunk]}
        if notify(hook, payload):
            delivered.update(r['url'] for r in chunk)
            ok += 1
            print(f'  posted chunk {idx // CHUNK_SIZE + 1} ({len(chunk)} embeds)')
            if not args.preview:
                state.update(seen=sorted(seen|delivered),posted_at=now_iso(),posts=starting_posts+ok)
                save_state(state)
        else:
            print(f'  chunk {idx // CHUNK_SIZE + 1} failed')
        time.sleep(PACE_SECONDS)

    if args.preview:
        print('preview mode: state not modified')
        return 0
    if delivered:
        # Deliberate seed suppresses the initial backlog only after every selected
        # notification succeeded. Normal runs record delivered URLs, never the backlog.
        seed_complete = args.seed and summary_ok and len(delivered) == len({r['url'] for r in to_post})
        state['seen'] = sorted(seen | ({r['url'] for r in rows} if seed_complete else delivered))
        state['posted_at'] = now_iso()
        state['posts'] = starting_posts + ok
        if seed_complete:state['baseline_urls']=sorted({r['url'] for r in rows}-seen-delivered)
        save_state(state)
        print(f'state updated: {len(state["seen"])} urls recorded')
    else:
        print('nothing posted; state unchanged')
    return 0 if len(delivered) == len({r['url'] for r in to_post}) else 1


if __name__ == '__main__':
    sys.exit(main())
