#!/usr/bin/env python3
"""Findings ledger with a completion gate. Stores state in <project>/.audit/findings.json so
progress survives long sessions and context resets. Nothing counts as fixed until its
acceptance check has actually run and passed.

Usage (run from the project root, or set AUDIT_DIR):
  ledger.py init
  ledger.py add --sev High --area auth --title "DELETE has no auth" --evidence "app/api/route.ts:2" --check "npm test -- auth" [--fix "add session check"]
  ledger.py list [--open]
  ledger.py start ID [--check CMD]        mark in progress and record that the check FAILS before the fix
  ledger.py verify ID                     re-run the check after the fix; fixed only if exit code 0
  ledger.py block ID --reason "needs decision: ..."   needs the user; excluded from auto-fix
  ledger.py wontfix ID --reason "..."     only with the user's approval
  ledger.py pass --new N                  record a full re-audit that found N new defects
  ledger.py gate                          exit 0 only when the work is truly finished
  ledger.py regress                       re-run every fixed check; reopen anything that broke
  ledger.py export-tests                  write .audit/regression.sh from all fixed checks
  ledger.py active on|off                 turn repair mode (Stop hook blocking) on or off
  ledger.py report                        markdown summary
"""
import json, os, subprocess, sys, time, argparse

D = os.environ.get("AUDIT_DIR", os.path.join(os.getcwd(), ".audit"))
F = os.path.join(D, "findings.json")
SEVS = ["Critical", "High", "Medium", "Low"]

def load():
    if not os.path.exists(F): sys.exit("No ledger. Run: ledger.py init")
    return json.load(open(F))

def save(s):
    os.makedirs(D, exist_ok=True); json.dump(s, open(F, "w"), indent=1, ensure_ascii=False)

def find(s, i):
    for x in s["findings"]:
        if x["id"] == i: return x
    sys.exit(f"No finding {i}")

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=900)
    return r.returncode, (r.stdout + r.stderr).strip()[-400:]

def regress(s, exclude=None):
    """Re-run the acceptance check of every finding already marked fixed. Anything that fails again is reopened."""
    bad = []
    for x in s["findings"]:
        if x["status"] == "fixed" and x["check"] and x["id"] != exclude:
            code, tail = run(x["check"])
            if code != 0:
                x["status"] = "open"; x["history"].append({"t": time.strftime("%H:%M:%S"), "exit": code, "tail": "REGRESSION: " + tail}); bad.append(x["id"])
    return bad

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("id", nargs="?")
    for a in ("sev", "area", "title", "evidence", "check", "fix", "reason", "new"): ap.add_argument("--" + a)
    ap.add_argument("--open", action="store_true"); a = ap.parse_args(); c = a.cmd

    if c == "init":
        if os.path.exists(F): sys.exit("Ledger already exists (kept).")
        save({"created": time.strftime("%Y-%m-%d %H:%M"), "findings": [], "passes": []}); print("ledger created at", F); return
    s = load()
    if c == "add":
        if not (a.sev in SEVS and a.title and a.evidence): sys.exit("add needs --sev (Critical|High|Medium|Low) --title --evidence")
        i = "F%d" % (len(s["findings"]) + 1)
        s["findings"].append({"id": i, "sev": a.sev, "area": a.area or "", "title": a.title, "evidence": a.evidence, "check": a.check or "", "fix": a.fix or "", "status": "open", "proof": "", "reason": "", "history": []})
        save(s); print("added", i)
        if not a.check: print("WARNING: no acceptance check; it will need manual proof via 'verify --check' before closing")
    elif c == "list":
        for x in sorted(s["findings"], key=lambda x: (SEVS.index(x["sev"]), x["id"])):
            if a.open and x["status"] in ("fixed", "wontfix"): continue
            print(f'{x["id"]:5} {x["sev"]:8} {x["status"]:11} {x["area"]:12} {x["title"]}')
    elif c == "start":
        x = find(s, a.id); cmd = a.check or x["check"]
        if a.check: x["check"] = a.check
        x["status"] = "in_progress"
        if cmd:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=900)
            x["baseline_failed"] = r.returncode != 0
            print(a.id, "in progress; baseline check", "FAILS as expected (defect reproduced)" if r.returncode else "PASSES BEFORE ANY FIX: the check does not prove the defect, rewrite it with start --check")
        else: print(a.id, "in progress (no automated check: you must add one with --check before verify)")
        save(s)
    elif c == "verify":
        x = find(s, a.id); cmd = a.check or x["check"]
        if not cmd: sys.exit("No acceptance check recorded; pass --check '<command that fails before the fix and passes after>'")
        if a.check and a.check != x["check"]: sys.exit("Change the check with 'start --check ...' so a failing baseline is recorded first")
        if not x.get("baseline_failed"): sys.exit("Run 'start' first: the check must fail before the fix, otherwise it proves nothing")
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=900)
        out = (r.stdout + r.stderr).strip()[-600:]
        x["history"].append({"t": time.strftime("%H:%M:%S"), "exit": r.returncode, "tail": out})
        if r.returncode == 0: x["status"] = "fixed"; x["proof"] = f"check passed at {time.strftime('%Y-%m-%d %H:%M')}: {cmd}"
        else: x["status"] = "in_progress"
        bad = regress(s, exclude=a.id) if r.returncode == 0 else []
        save(s); print(a.id, "VERIFIED FIXED" if r.returncode == 0 else f"STILL FAILING (exit {r.returncode})"); print(out[-400:])
        if bad: print("REGRESSION: this change broke earlier fixes, reopened:", ", ".join(bad), "- fix them before continuing")
        sys.exit(0 if r.returncode == 0 and not bad else 1)
    elif c in ("block", "wontfix"):
        if not a.reason: sys.exit("--reason required")
        x = find(s, a.id); x["status"] = "blocked" if c == "block" else "wontfix"; x["reason"] = a.reason; save(s); print(a.id, x["status"])
    elif c == "pass":
        s["passes"].append({"t": time.strftime("%Y-%m-%d %H:%M"), "new": int(a.new or 0)}); save(s); print("pass recorded, new defects:", a.new or 0)
    elif c == "gate":
        bad = regress(s)
        if bad: save(s); print("REGRESSION: earlier fixes failing again and reopened:", ", ".join(bad))
        open_ = [x for x in s["findings"] if x["status"] in ("open", "in_progress")]
        blocked = [x for x in s["findings"] if x["status"] == "blocked"]
        passes = s["passes"]; clean = len(passes) >= 2 and all(p["new"] == 0 for p in passes[-2:])
        print(f'findings {len(s["findings"])}: fixed {sum(x["status"]=="fixed" for x in s["findings"])}, blocked {len(blocked)}, wontfix {sum(x["status"]=="wontfix" for x in s["findings"])}, open {len(open_)}')
        for x in open_: print("  NOT DONE:", x["id"], x["sev"], x["title"])
        if not clean: print("  NOT DONE: need two consecutive full re-audit passes with 0 new defects (recorded:", len(passes), ")")
        ok = not open_ and clean
        for x in blocked: print("  needs user:", x["id"], x["reason"])
        print("GATE:", "PASSED, you may report completion" if ok else "FAILED, do not claim completion"); sys.exit(0 if ok else 1)
    elif c == "regress":
        bad = regress(s); save(s)
        print("regression check:", "ALL EARLIER FIXES STILL HOLD" if not bad else "FAILING AGAIN: " + ", ".join(bad)); sys.exit(1 if bad else 0)
    elif c == "export-tests":
        out = os.path.join(D, "regression.sh"); lines = ["#!/bin/sh", "# Regression checks exported from the audit ledger. Run from the project root.", "fail=0"]
        for x in s["findings"]:
            if x["status"] == "fixed" and x["check"]:
                title = x["title"].replace("'", "")
                lines.append(f"echo '{x['id']} {title}'; ( {x['check']} ) >/dev/null 2>&1 || {{ echo 'FAILED {x['id']}'; fail=1; }}")
        lines.append("exit $fail"); open(out, "w").write("\n".join(lines) + "\n"); os.chmod(out, 0o755); print("wrote", out, "- commit it with the project so fixes stay fixed")
    elif c == "active":
        m = os.path.join(D, "active")
        if a.id == "on": os.makedirs(D, exist_ok=True); open(m, "w").write(time.strftime("%Y-%m-%d %H:%M")); print("repair mode ON: the Stop hook now blocks finishing until the gate passes")
        else:
            if os.path.exists(m): os.remove(m)
            print("repair mode OFF")
    elif c == "report":
        print("| id | severity | status | title | proof or reason |\n|---|---|---|---|---|")
        for x in sorted(s["findings"], key=lambda x: (SEVS.index(x["sev"]), x["id"])):
            print(f'| {x["id"]} | {x["sev"]} | {x["status"]} | {x["title"]} | {(x["proof"] or x["reason"] or "-")[:90]} |')
    else: sys.exit(__doc__)

main()
