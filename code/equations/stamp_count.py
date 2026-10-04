#!/usr/bin/env python3
"""Stamp the current equation count + date into the static HTML.

Rewrites the <span id="eq-count-num"> / <span id="eq-count-date"> values in
index.html and data.html from data/index/eq.idx.json.gz (the same source the
live JS counter reads). Run after every drip.
"""
import datetime, gzip, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
IDX = os.path.join(ROOT, "data", "index", "eq.idx.json.gz")
STATE = os.path.join(HERE, "state.json")

def main():
    with gzip.open(IDX, "rt", encoding="utf-8") as f:
        n = sum(1 for line in f if line.strip())
    # Task rule: the stamped count is next_index-1 from state.json; the live
    # index row count must agree, or the stamp would be one run behind / off.
    next_index = json.load(open(STATE, encoding="utf-8"))["next_index"]
    if next_index - 1 != n:
        raise SystemExit(
            "stamp_count: state.json next_index-1 (%d) != index rows (%d) — "
            "run the generator / index rebuild first" % (next_index - 1, n))
    num = f"{n:,}"
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    for fn in ("index.html", "data.html"):
        p = os.path.join(ROOT, fn)
        t = open(p, encoding="utf-8").read()
        t2 = re.sub(r'(<span id="eq-count-num(-f)?">)[^<]*(</span>)',
                    lambda m: m.group(1) + num + m.group(3), t)
        t2 = re.sub(r'(<span id="eq-count-date(-f)?">)[^<]*(</span>)',
                    lambda m: m.group(1) + today + m.group(3), t2)
        # data.html A-Z archive section header (stamped AFTER the index and
        # the az letter chunks flush, so it is never one run behind)
        t2 = re.sub(r'(<span id="eq-arch-num">)[^<]*(</span>)',
                    lambda m: m.group(1) + num + m.group(2), t2)
        t2 = re.sub(r'(<span id="eq-arch-date">)[^<]*(</span>)',
                    lambda m: m.group(1) + today + m.group(2), t2)
        if t2 != t:
            open(p, "w", encoding="utf-8").write(t2)
        print(f"stamp: {fn} -> {num} as of {today}")

if __name__ == "__main__":
    main()
