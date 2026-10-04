#!/usr/bin/env python3
"""Build the A-Z browse index for the equation archive (data.html archive section).

Reads data/index/eq.idx.json.gz (JSONL: id, title, type, chunk), groups rows by
the first letter of the title (A-Z, non-letters under '#'), and writes one gz
chunk per letter:

    data/index/az/eq-az-<L>.json.gz   -- compact rows [id, title, type]
    data/index/az/manifest.json       -- {total, updated, letters: [{l, n}]}

data.html fetches only the letter chunk the user opens (lazy), never the whole
archive at once. Run AFTER the drip generator flushes the index (drip.sh order:
generator -> build_az_index -> sitemap -> stamp_count), never before.
"""
import datetime, gzip, json, os, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
IDX = os.path.join(ROOT, "data", "index", "eq.idx.json.gz")
OUTDIR = os.path.join(ROOT, "data", "index", "az")

def letter_of(title):
    t = (title or "").strip()
    if not t:
        return "#"
    c = t[0].upper()
    return c if "A" <= c <= "Z" else "#"

def atomic_write_gz(path, payload):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    os.close(fd)
    try:
        with gzip.open(tmp, "wt", encoding="utf-8") as f:
            f.write(payload)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

def main():
    if not os.path.exists(IDX):
        raise SystemExit("build_az_index: missing %s (run generator.py first)" % IDX)
    buckets = {}
    n = 0
    with gzip.open(IDX, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            L = letter_of(d.get("t"))
            buckets.setdefault(L, []).append([d["id"], d.get("t", ""), d.get("y", "")])
            n += 1
    if n == 0:
        raise SystemExit("build_az_index: index is empty, refusing to write")
    os.makedirs(OUTDIR, exist_ok=True)
    order = sorted(buckets.keys(), key=lambda L: ("#" if L == "#" else "", L))
    letters = []
    for L in order:
        rows = buckets[L]
        path = os.path.join(OUTDIR, "eq-az-%s.json.gz" % L)
        atomic_write_gz(path, "\n".join(json.dumps(r, separators=(",", ":")) for r in rows))
        letters.append({"l": L, "n": len(rows)})
    manifest = {
        "total": n,
        "updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "letters": letters,
    }
    fd, tmp = tempfile.mkstemp(dir=OUTDIR, suffix=".tmp")
    os.close(fd)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(manifest, f, separators=(",", ":"))
    os.replace(tmp, os.path.join(OUTDIR, "manifest.json"))
    print("az-index: %d records across %d letters (%s)" % (n, len(letters), ",".join(order)))

if __name__ == "__main__":
    main()
