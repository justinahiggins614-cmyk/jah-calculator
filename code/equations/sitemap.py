#!/usr/bin/env python3
"""Per-record sitemap for the equation archive. Batches of 50k; writes index."""
import gzip, json, math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = "https://justinahiggins614-cmyk.github.io/jah-calculator/index.html"
BATCH = 50000

def load_ids():
    ids = []
    with gzip.open(os.path.join(ROOT, "data", "index", "eq.idx.json.gz"), "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                ids.append(json.loads(line)["id"])
    return ids

def main():
    ids = load_ids()
    n = len(ids)
    files = []
    for b in range(math.ceil(n / BATCH) or 1):
        part = ids[b * BATCH:(b + 1) * BATCH]
        fn = f"sitemap-eq-{b + 1}.xml"
        with open(os.path.join(ROOT, fn), "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
            for eid in part:
                f.write(f'  <url><loc>{BASE}?tab=eq&amp;eq={eid}</loc><changefreq>monthly</changefreq></url>\n')
            f.write('</urlset>\n')
        files.append(fn)
    # sitemap index
    with open(os.path.join(ROOT, "sitemap-index.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        f.write('  <sitemap><loc>https://justinahiggins614-cmyk.github.io/jah-calculator/sitemap.xml</loc></sitemap>\n')
        for fn in files:
            f.write(f'  <sitemap><loc>https://justinahiggins614-cmyk.github.io/jah-calculator/{fn}</loc></sitemap>\n')
        f.write('</sitemapindex>\n')
    # robots -> index
    rp = os.path.join(ROOT, "robots.txt")
    txt = open(rp, encoding="utf-8").read()
    txt = re.sub(r'Sitemap: .*', 'Sitemap: https://justinahiggins614-cmyk.github.io/jah-calculator/sitemap-index.xml', txt)
    open(rp, "w", encoding="utf-8").write(txt)
    print(f"sitemap: {n} equation URLs in {len(files)} file(s)")

if __name__ == "__main__":
    main()
