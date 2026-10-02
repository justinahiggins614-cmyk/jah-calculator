#!/usr/bin/env python3
"""Build the public CSV export of the full equation catalog.

Reads every data/equations/eq-c*.jsonl.gz chunk and writes
data/exports/equations.csv (id,n,type,title,equation,steps,solution,
check,solver_version,canonical_hash). Safe to rerun; fully rewritten each time.
"""
import csv, glob, gzip, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "data", "exports", "equations.csv")

FIELDS = ["id", "n", "type", "title", "equation", "steps",
          "solution", "check", "solver_version", "canonical_hash"]

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    n = 0
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        for path in sorted(glob.glob(os.path.join(ROOT, "data", "equations", "eq-c*.jsonl.gz"))):
            with gzip.open(path, "rt", encoding="utf-8") as g:
                for line in g:
                    line = line.strip()
                    if not line:
                        continue
                    d = json.loads(line)
                    steps = d.get("steps") or []
                    w.writerow([
                        d.get("id", ""), d.get("n", ""), d.get("type", ""),
                        d.get("title", ""), d.get("equation", ""),
                        "\n".join(steps),
                        d.get("solution", ""), d.get("check", ""),
                        d.get("solver_version", ""), d.get("canonical_hash", ""),
                    ])
                    n += 1
    print(f"csv: {n} records -> {OUT} ({os.path.getsize(OUT)} bytes)")

if __name__ == "__main__":
    main()
