#!/bin/bash
# Equation drip: +2,000 official JAH-EQ records every 2h toward 1,000,000.
set -e
cd ~/workspace/jah-calculator
SZ=$(du -sm data 2>/dev/null | cut -f1)
if [ "${SZ:-0}" -gt 700 ]; then echo "GUARD: data/equations over 700MB, skipping"; exit 1; fi
python3 code/equations/generator.py 2000
python3 code/equations/sitemap.py
python3 code/equations/stamp_count.py
python3 code/equations/build_csv.py
python3 -c "
import json, datetime
st=json.load(open('code/equations/state.json'))
now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')
rev='eq-drip-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M')
d=json.load(open('api.json'))
n=st['next_index']-1
d['records_approx']=n
d['archive_count']=n
d['records_as_of']=now[:10]
d['archive_generated_at']=now
d['archive_updated_at']=now
d['archive_revision']=rev
json.dump(d,open('api.json','w'),indent=2,sort_keys=True)"
# BUILD GATE: fail the run (and skip the commit/push) if the archive is inconsistent
bash code/qa/run_all.sh
git add -A
git commit -qm "equation drip $(date -u +%Y-%m-%dT%H:%M)" || true
git push -q origin main
echo "drip done"
