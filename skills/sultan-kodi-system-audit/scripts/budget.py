#!/usr/bin/env python3
"""Usage budget for an audit session. Real usage cannot be read from inside a session, so this is a self-reported
estimate: the worker logs rough units as it works, and the budget stops the work cleanly with a handoff.
Usage: budget.py set --percent-of-week 20 | --units N      (units: 1 unit is about 1k tokens of work; stored in .audit/budget.json)
       budget.py log N [note]                              add N units after a heavy step (a file read of 500 lines is about 2, a scan about 3, a fix cycle about 10)
       budget.py check                                     exit 0 under 80%, 3 at 80% (wrap up soon), 4 at 100% (stop and write the handoff)
       budget.py status"""
import json, os, sys, time
D = os.environ.get("AUDIT_DIR", os.path.join(os.getcwd(), ".audit")); F = os.path.join(D, "budget.json")
a = sys.argv[1:]
if not a: sys.exit(__doc__)
def load(): return json.load(open(F)) if os.path.exists(F) else {"limit": 0, "used": 0, "log": []}
b = load()
if a[0] == "set":
    if "--units" in a: b["limit"] = int(a[a.index("--units") + 1])
    elif "--percent-of-week" in a:
        pct = float(a[a.index("--percent-of-week") + 1]); b["limit"] = int(pct * 10)  # assumption: a weekly allowance of about 1000 units on this plan; calibrate with the user
        b["note"] = f"{pct}% of an assumed 1000-unit week; calibrate this assumption with the user"
    os.makedirs(D, exist_ok=True); json.dump(b, open(F, "w"), indent=1); print("budget limit:", b["limit"], "units", b.get("note", ""))
elif a[0] == "log":
    b["used"] += float(a[1]); b["log"].append({"t": time.strftime("%H:%M"), "n": float(a[1]), "note": " ".join(a[2:])}); os.makedirs(D, exist_ok=True); json.dump(b, open(F, "w"), indent=1); print(f"used {b['used']:.0f} of {b['limit']}")
elif a[0] in ("check", "status"):
    if not b["limit"]: print("no budget set"); sys.exit(0)
    p = 100 * b["used"] / b["limit"]; print(f"budget used {p:.0f}% ({b['used']:.0f}/{b['limit']} units, estimate)")
    if a[0] == "check":
        if p >= 100: print("STOP: budget reached. Save the ledger, write .audit/HANDOFF.md with the next three steps, and tell the user."); sys.exit(4)
        if p >= 80: print("WRAP UP: finish the current finding, then write .audit/HANDOFF.md."); sys.exit(3)
else: sys.exit(__doc__)
