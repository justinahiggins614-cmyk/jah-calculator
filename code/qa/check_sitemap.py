#!/usr/bin/env python3
"""Sitemap integrity: every sitemap must be valid XML, every record URL's
JAH-EQ id must exist in the live index, no duplicate URLs, and the total
record-URL count must equal the archive count. Exits 0 when clean, 1 otherwise."""
import os, sys, gzip, json, re
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

idx_ids = set()
with gzip.open(os.path.join(ROOT, "data/index/eq.idx.json.gz"), "rt", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            idx_ids.add(json.loads(line)["id"])

fails = []
seen = set()
rec_urls = 0
for fn in sorted(os.listdir(ROOT)):
    if not (fn.startswith("sitemap") and fn.endswith(".xml")):
        continue
    p = os.path.join(ROOT, fn)
    try:
        tree = ET.parse(p)
    except Exception as e:
        fails.append("%s: invalid XML (%s)" % (fn, e))
        continue
    for loc in tree.getroot().iter():
        if not loc.tag.endswith("loc") or not loc.text:
            continue
        u = loc.text.strip()
        if u in seen:
            fails.append("duplicate URL %s (in %s)" % (u, fn))
        seen.add(u)
        m = re.search(r"eq=(JAH-EQ-\d+)", u)
        if m:
            rec_urls += 1
            if m.group(1) not in idx_ids:
                fails.append("%s: URL references unknown record %s" % (fn, m.group(1)))

if rec_urls != len(idx_ids):
    fails.append("sitemap record URLs %d != archive count %d" % (rec_urls, len(idx_ids)))

print("sitemap files checked, record URLs: %d, archive: %d" % (rec_urls, len(idx_ids)))
for f in fails:
    print("FAIL: " + f)
if fails:
    print("RESULT: FAIL")
    sys.exit(1)
print("RESULT: PASS")
