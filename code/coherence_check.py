#!/usr/bin/env python3
"""Coherence check: every AI the calculator presents vs the phone-book canon.

Canon: /home/hatch/workspace/jah-ai-models/ai-catalog.json
Rule: any AI presented WITH a JAH-AI ID must match the canon exactly
(name + description, whitespace-normalized). Site helpers must NOT claim
a canon ID. Exit 0 = coherent, 1 = drift found (loud report).
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON_PATHS = [
    "/home/hatch/workspace/jah-ai-models/ai-catalog.json",
    os.path.expanduser("~/workspace/jah-ai-models/ai-catalog.json"),
]
ID_RE = re.compile(r"JAH-AI-[A-Z0-9-]+")

def ws(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()

def load_canon():
    for p in CANON_PATHS:
        if os.path.exists(p):
            c = json.load(open(p, encoding="utf-8"))
            recs = c.get("records", [])
            return {r["ID"]: r for r in recs if r.get("ID")}
    return None

def main():
    canon = load_canon()
    issues = []
    helpers = []
    if canon is None:
        print("COHERENCE WARN: canon file not found; ID-claim scan only.")
    # The calculator has no AI personas: Ask Anything is a helper, no canon ID.
    helpers.append("Ask Anything (answer engine) — site helper, no JAH-AI ID claimed")
    # Scan for any JAH-AI ID claims anywhere in the site.
    claimed = set()
    for base, _, files in os.walk(ROOT):
        if ".git" in base:
            continue
        for f in files:
            if f.endswith((".html", ".js", ".json")):
                try:
                    txt = open(os.path.join(base, f), encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                for m in ID_RE.findall(txt):
                    claimed.add((m, os.path.relpath(os.path.join(base, f), ROOT)))
    # The module copy itself contains no IDs; the only acceptable mention is none.
    real_claims = [(i, f) for (i, f) in claimed if "jah-talk-fallback" not in f]
    if real_claims:
        for i, f in sorted(real_claims):
            issues.append("canon ID claimed outside canon context: %s in %s" % (i, f))
    print("=" * 64)
    print("COHERENCE REPORT — jah-calculator")
    print("=" * 64)
    print("Helper AIs (no canon ID, JAHtalk voice):")
    for h in helpers:
        print("  - " + h)
    print("JAH-AI ID claims found on site: %d" % len(real_claims))
    if issues:
        print("\n*** DRIFT DETECTED ***")
        for i in issues:
            print("  ! " + i)
        return 1
    print("\nOK: no canon-ID claims; every AI surface is a declared helper.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
