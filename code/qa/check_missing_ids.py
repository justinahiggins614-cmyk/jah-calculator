#!/usr/bin/env python3
"""Missing-ID check: JAH-EQ-######## ids must form the contiguous range 1..N.
Exits 0 when contiguous, 1 with gaps listed."""
import os, sys, gzip, json, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IDX = os.path.join(ROOT, "data/index/eq.idx.json.gz")

nums = []
with gzip.open(IDX, "rt", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        m = re.fullmatch(r"JAH-EQ-(\d+)", json.loads(line)["id"])
        if not m:
            print("FAIL: malformed id: %s" % json.loads(line)["id"])
            sys.exit(1)
        nums.append(int(m.group(1)))

nums.sort()
expect = set(range(1, len(nums) + 1))
have = set(nums)
gaps = sorted(expect - have)
extras = sorted(have - expect)
print("ids in index: %d, expected range 1..%d" % (len(nums), len(nums)))
if gaps:
    print("FAIL: %d gaps (e.g. %s)" % (len(gaps), gaps[:10]))
if extras:
    print("FAIL: %d out-of-range ids (e.g. %s)" % (len(extras), extras[:10]))
if gaps or extras:
    print("RESULT: FAIL")
    sys.exit(1)
print("RESULT: PASS (contiguous)")
