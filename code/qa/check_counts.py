#!/usr/bin/env python3
"""Count-vs-data: equation counts must derive from data, never hardcode.
Compares the live index, the chunk files, and api.json claims.
Exits 0 when consistent, 1 otherwise."""
import os, sys, gzip, json, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IDX = os.path.join(ROOT, "data/index/eq.idx.json.gz")

idx_ids = []
with gzip.open(IDX, "rt", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            idx_ids.append(json.loads(line)["id"])

chunk_n = 0
chunk_ids = set()
for path in sorted(glob.glob(os.path.join(ROOT, "data/equations/eq-c*.jsonl.gz"))):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunk_n += 1
                chunk_ids.add(json.loads(line)["id"])

api_n = None
api_path = os.path.join(ROOT, "api.json")
if os.path.exists(api_path):
    api_n = json.load(open(api_path)).get("equations")

print("index rows        : %d" % len(idx_ids))
print("chunk records     : %d" % chunk_n)
print("api.json equations: %s" % api_n)

fails = []
if chunk_n != len(idx_ids):
    fails.append("chunk total %d != index total %d" % (chunk_n, len(idx_ids)))
if api_n is not None and api_n != len(idx_ids):
    fails.append("api.json says %s but index has %d" % (api_n, len(idx_ids)))

# every index id must exist in some chunk
missing = [i for i in idx_ids if i not in chunk_ids]
if missing:
    fails.append("%d index ids missing from chunks (e.g. %s)" % (len(missing), missing[:3]))

for f in fails:
    print("FAIL: " + f)
if fails:
    print("RESULT: FAIL")
    sys.exit(1)
print("RESULT: PASS")
