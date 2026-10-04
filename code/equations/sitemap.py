#!/usr/bin/env python3
"""Per-record sitemap for the equation archive. Batches of 50k; writes index."""
import gzip, json, math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = "https://justinahiggins614-cmyk.github.io/jah-calculator/index.html"
DATABASE = "https://justinahiggins614-cmyk.github.io/jah-calculator/data.html"
BATCH = 50000
CATEGORIES = ["linear", "quadratic", "system2", "trig", "power", "log", "exp",
              "evaluate", "percent", "derivative", "integral", "geometry"]

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
    # category landing URLs (static fallbacks for non-JS crawlers)
    with open(os.path.join(ROOT, "sitemap-eq-cats.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for cat in CATEGORIES:
            f.write(f'  <url><loc>{BASE}?tab=eq&amp;type={cat}</loc><changefreq>weekly</changefreq></url>\n')
        f.write('</urlset>\n')
    files.append("sitemap-eq-cats.xml")
    # A-Z archive letter deep links (data.html?letter=X auto-opens that letter)
    az_letters = []
    az_manifest = os.path.join(ROOT, "data", "index", "az", "manifest.json")
    if os.path.exists(az_manifest):
        az_letters = [e["l"] for e in json.load(open(az_manifest, encoding="utf-8"))["letters"]]
    with open(os.path.join(ROOT, "sitemap-eq-az.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for L in az_letters:
            f.write(f'  <url><loc>{DATABASE}?letter={L}</loc><changefreq>weekly</changefreq></url>\n')
        f.write('</urlset>\n')
    files.append("sitemap-eq-az.xml")
    print(f"sitemap: {len(az_letters)} A-Z letter URLs")
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
