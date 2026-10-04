#!/usr/bin/env python3
"""Link audit for the calculator site: every href/src in index.html must resolve.
External https links are fetched (GET, small timeout); local data paths must exist.
Exits 0 when clean, 1 with the dead list otherwise."""
import os, re, sys, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAGE = os.path.join(ROOT, "index.html")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) jah-qa-linkcheck"}

html = open(PAGE, encoding="utf-8").read()
urls = sorted(set(re.findall(r'(?:href|src)\s*=\s*"([^"]+)"', html)))
# only real destinations: drop anchors, mailto, javascript:, templated/relative-up paths
urls = [u for u in urls if u and not u.startswith(("#", "mailto:", "javascript:"))]

dead, ok = [], []
for u in urls:
    if u.startswith("http"):
        try:
            req = urllib.request.Request(u, headers=UA)
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status in (200, 301, 302, 303, 307, 308):
                    ok.append((u, r.status))
                else:
                    dead.append((u, r.status))
        except urllib.error.HTTPError as e:
            dead.append((u, "HTTPError %s" % e.code))
        except Exception as e:
            dead.append((u, "%s: %s" % (type(e).__name__, e)))
    else:
        # strip fragment/query: data.html#archive and ?tab=eq both resolve locally
        local = u.split("#", 1)[0]
        if local == "" or local.startswith("?"):
            local = "index.html"
        p = os.path.join(ROOT, local.lstrip("/"))
        if os.path.exists(p):
            ok.append((u, "local"))
        else:
            dead.append((u, "missing local file"))

print("checked %d links" % len(urls))
for u, s in ok:
    print("  OK   %s [%s]" % (u, s))
for u, s in dead:
    print("  DEAD %s [%s]" % (u, s))
if dead:
    print("RESULT: FAIL (%d dead)" % len(dead))
    sys.exit(1)
print("RESULT: PASS")
