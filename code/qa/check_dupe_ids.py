#!/usr/bin/env python3
"""Dupe-ID check: no equation ID may appear twice in the index or chunks.
Exits 0 when clean, 1 with duplicates listed."""
import os, sys, gzip, json, glob
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IDX = os.path.join(ROOT, "data/index/eq.idx.json.gz")

seen_idx, seen_chunk = Counter(), Counter()
with gzip.open(IDX, "rt", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            seen_idx[json.loads(line)["id"]] += 1
for path in sorted(glob.glob(os.path.join(ROOT, "data/equations/eq-c*.jsonl.gz"))):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                seen_chunk[json.loads(line)["id"]] += 1

dupes_idx = sorted([k for k, v in seen_idx.items() if v > 1])
dupes_chunk = sorted([k for k, v in seen_chunk.items() if v > 1])
print("index rows: %d, chunk records: %d" % (sum(seen_idx.values()), sum(seen_chunk.values())))
fails = 0
if dupes_idx:
    print("FAIL: %d duplicated ids in index: %s" % (len(dupes_idx), dupes_idx[:10])); fails += 1
if dupes_chunk:
    print("FAIL: %d duplicated ids in chunks: %s" % (len(dupes_chunk), dupes_chunk[:10])); fails += 1
if fails:
    print("RESULT: FAIL"); sys.exit(1)
print("RESULT: PASS (no duplicate ids)")
