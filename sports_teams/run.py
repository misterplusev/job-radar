"""Sports teams CLI, matching the other jobs modules' ingest/render workflow."""
import argparse
import json
import os
import sys
from pathlib import Path
import pipeline_local as pipeline
import live_refresh


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['ingest','render','status','registry','scrape'])
    parser.add_argument('what',nargs='?',default='all')
    parser.add_argument('--out')
    args,extra=parser.parse_known_args()
    if args.command in ('ingest','status'):
        sys.argv=['pipeline_local.py']+(['--stats'] if args.command=='status' else [])+extra
        if args.command=='ingest' and os.environ.get('SUPABASE_SERVICE_ROLE_KEY'):sys.argv.append('--cloud')
        return pipeline.main()
    if args.command=='registry':
        sources=live_refresh.build_sources(pipeline.pt)
        print(json.dumps(list(sources.values()),indent=2));return 0
    if args.command=='render':
        with pipeline.connect() as con: payload=pipeline.write_outputs(pipeline.snapshot(con))
        if args.out:Path(args.out).write_text((pipeline.ROOT/'board/live.html').read_text(encoding='utf-8'),encoding='utf-8')
        print('Active jobs:',payload['count']);return 0
    results,discovery=live_refresh.collect(pipeline.pt)
    rows=[row for result in results for row in result['rows'] if args.what=='all' or row['league'].lower()==args.what.lower()]
    if args.out:Path(args.out).write_text('\n'.join(json.dumps(row,ensure_ascii=False) for row in rows)+'\n',encoding='utf-8')
    print(json.dumps({'jobs':len(rows),'sources':len(results),'failed_sources':[r['source']['key'] for r in results if r['status']!='success'],'discovery':discovery}))
    return 0 if rows else 1


if __name__=='__main__':raise SystemExit(main())
