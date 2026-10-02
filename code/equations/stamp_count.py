#!/usr/bin/env python3
"""Stamp the current equation count + date into the static HTML.

Rewrites the <span id="eq-count-num"> / <span id="eq-count-date"> values in
index.html and data.html from data/index/eq.idx.json.gz (the same source the
live JS counter reads). Run after every drip.
"""
import datetime, gzip, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
IDX = os.path.join(ROOT, "data", "index", "eq.idx.json.gz")

def main():
    with gzip.open(IDX, "rt", encoding="utf-8") as f:
        n = sum(1 for line in f if line.strip())
    num = f"{n:,}"
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    for fn in ("index.html", "data.html"):
        p = os.path.join(ROOT, fn)
        t = open(p, encoding="utf-8").read()
        t2 = re.sub(r'(<span id="eq-count-num">)[^<]*(</span>)',
                    lambda m: m.group(1) + num + m.group(2), t, count=1)
        t2 = re.sub(r'(<span id="eq-count-date">)[^<]*(</span>)',
                    lambda m: m.group(1) + today + m.group(2), t2, count=1)
        if t2 != t:
            open(p, "w", encoding="utf-8").write(t2)
        print(f"stamp: {fn} -> {num} as of {today}")

if __name__ == "__main__":
    main()
