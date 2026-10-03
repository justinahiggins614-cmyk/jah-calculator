#!/bin/bash
# JAH Calculator QA build gate: every checker must pass, or the build fails.
# Called by code/equations/drip.sh before any commit. Exits non-zero on failure.
set -e
cd "$(dirname "$0")"
echo "== qa: check_counts =="
python3 check_counts.py
echo "== qa: check_dupe_ids =="
python3 check_dupe_ids.py
echo "== qa: check_missing_ids =="
python3 check_missing_ids.py
echo "== qa: check_sitemap =="
python3 check_sitemap.py
echo "QA: ALL PASS"
