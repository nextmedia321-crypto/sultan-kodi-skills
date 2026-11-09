#!/usr/bin/env python3
"""Compare two audit snapshots and show the trend.
Usage: trend.py snapshot [label]       save .audit/history/<timestamp>.json from findings.json
       trend.py compare [A.json B.json]  compare the last two (or two given) snapshots: new, closed, still open, regressions, by severity"""
import json, os, sys, time, shutil, glob
D = os.environ.get("AUDIT_DIR", os.path.join(os.getcwd(), ".audit")); H = os.path.join(D, "history"); F = os.path.join(D, "findings.json")
a = sys.argv[1:]
if not a: sys.exit(__doc__)
if a[0] == "snapshot":
    os.makedirs(H, exist_ok=True); s = json.load(open(F)); n = os.path.join(H, time.strftime("%Y%m%d-%H%M%S") + "-%03d" % (int(time.time() * 1000) % 1000) + ".json")
    json.dump({"label": a[1] if len(a) > 1 else "", "t": time.strftime("%Y-%m-%d %H:%M"), "findings": [{k: x[k] for k in ("id", "sev", "title", "status", "area")} for x in s["findings"]]}, open(n, "w"), ensure_ascii=False, indent=1); print("saved", n)
elif a[0] == "compare":
    fs = a[1:3] if len(a) >= 3 else sorted(glob.glob(os.path.join(H, "*.json")))[-2:]
    if len(fs) < 2: sys.exit("need two snapshots")
    A, B = (json.load(open(f)) for f in fs); key = lambda x: x["title"]
    ia = {key(x): x for x in A["findings"]}; ib = {key(x): x for x in B["findings"]}
    def isopen(x): return x["status"] in ("open", "in_progress", "blocked")
    new = [x for k, x in ib.items() if k not in ia]; closed = [x for k, x in ib.items() if k in ia and isopen(ia[k]) and not isopen(x)]
    reopened = [x for k, x in ib.items() if k in ia and not isopen(ia[k]) and isopen(x)]; still = [x for k, x in ib.items() if k in ia and isopen(ia[k]) and isopen(x)]
    print(f"# Trend: {A['t']} -> {B['t']}\nnew {len(new)}, closed {len(closed)}, REOPENED {len(reopened)}, still open {len(still)}")
    for t, l in (("NEW", new), ("CLOSED", closed), ("REOPENED (regression)", reopened)):
        for x in l[:10]: print(f"  {t}: [{x['sev']}] {x['title']}")
    for s in ("Critical", "High", "Medium", "Low"): print(f"  open {s}: {sum(isopen(x) and x['sev'] == s for x in A['findings'])} -> {sum(isopen(x) and x['sev'] == s for x in B['findings'])}")
    sys.exit(1 if reopened else 0)
else: sys.exit(__doc__)
