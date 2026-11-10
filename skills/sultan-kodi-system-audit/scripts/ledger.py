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
  ledger.py priority                      today / this week / this month, by business impact and effort
  ledger.py cover ROWID run|read|not-checkable|n/a [--reason "evidence"]   close a coverage row in .audit/ledger-seed.tsv
  ledger.py coverage                      coverage summary and the next unchecked rows
  ledger.py release-set --build CMD --test CMD --smoke CMD   record the commands that prove the system is ready to go live
  ledger.py release                       GO / NO-GO: gate passed, no open High/Critical, blocked items listed, build, tests and smoke run now
  ledger.py report                        markdown summary
  (add also takes --impact revenue|retention|risk|none --effort S|M|L --plain "one plain sentence for a business owner")
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

SEED = os.path.join(D, "ledger-seed.tsv")
def cov_load():
    if not os.path.exists(SEED): return []
    return [(l.rstrip("\n").split("\t") + [""] * 7)[:7] for l in open(SEED, encoding="utf-8") if l.strip()]
def cov_save(rows): open(SEED, "w", encoding="utf-8").write("\n".join("\t".join(r) for r in rows) + "\n")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("id", nargs="?"); ap.add_argument("status", nargs="?")
    for a in ("sev", "area", "title", "evidence", "check", "fix", "reason", "new", "impact", "effort", "plain", "status", "build", "test", "smoke"): ap.add_argument("--" + a)
    ap.add_argument("--open", action="store_true"); a = ap.parse_args(); c = a.cmd

    if c == "init":
        if os.path.exists(F): sys.exit("Ledger already exists (kept).")
        save({"created": time.strftime("%Y-%m-%d %H:%M"), "findings": [], "passes": []}); print("ledger created at", F); return
    s = load()
    if c == "add":
        if not (a.sev in SEVS and a.title and a.evidence): sys.exit("add needs --sev (Critical|High|Medium|Low) --title --evidence")
        i = "F%d" % (len(s["findings"]) + 1)
        s["findings"].append({"id": i, "sev": a.sev, "area": a.area or "", "title": a.title, "evidence": a.evidence, "check": a.check or "", "fix": a.fix or "", "impact": a.impact or "", "effort": a.effort or "", "plain": a.plain or "", "status": "open", "proof": "", "reason": "", "history": []})
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
        cv = cov_load(); unchecked = [r for r in cv[1:] if r[4] == "unchecked"]
        if cv: print(f"  coverage: {len(cv) - 1 - len(unchecked)}/{len(cv) - 1} rows closed")
        for r in unchecked[:8]: print("  NOT DONE: coverage row", r[0], r[2], r[1][:60])
        ok = not open_ and clean and not unchecked
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
    elif c == "priority":
        W = {"revenue": 3, "risk": 3, "retention": 2, "none": 0, "": 1}; E = {"S": 1, "M": 2, "L": 4, "": 2}; SV = {"Critical": 8, "High": 4, "Medium": 2, "Low": 1}
        todo = [x for x in s["findings"] if x["status"] in ("open", "in_progress", "blocked")]
        sc = lambda x: (SV[x["sev"]] + W.get(x.get("impact", ""), 1) * 2) / E.get(x.get("effort", ""), 2)
        todo.sort(key=sc, reverse=True)
        buckets = {"Today": [x for x in todo if x["sev"] == "Critical" or sc(x) >= 6], "This week": [], "This month": []}
        for x in todo:
            if x in buckets["Today"]: continue
            (buckets["This week"] if sc(x) >= 2.5 or x["sev"] == "High" else buckets["This month"]).append(x)
        for k, v in buckets.items():
            print(f"\n## {k} ({len(v)})")
            for x in v: print(f'- {x["id"]} [{x["sev"]}] {x["title"]}  impact={x.get("impact") or "?"} effort={x.get("effort") or "?"}' + (" (needs you)" if x["status"] == "blocked" else ""))
    elif c == "cover":
        if not (a.id and a.status in ("run", "read", "not-checkable", "n/a") and a.reason): sys.exit("use: cover ROWID run|read|not-checkable|n/a --reason EVIDENCE")
        rows = cov_load(); hit = [r for r in rows[1:] if r[0] == a.id]
        if not hit: sys.exit("no such row " + a.id)
        hit[0][4] = {"run": "run", "read": "read", "not-checkable": "not checkable", "n/a": "not applicable"}[a.status]; hit[0][5] = a.reason; cov_save(rows)
        print(a.id, "closed as", hit[0][4])
    elif c == "release-set":
        rel = {k: getattr(a, k) for k in ("build", "test", "smoke") if getattr(a, k)}
        if not rel: sys.exit("give at least one of --build --test --smoke")
        old = json.load(open(os.path.join(D, "release.json"))) if os.path.exists(os.path.join(D, "release.json")) else {}
        old.update(rel); json.dump(old, open(os.path.join(D, "release.json"), "w"), indent=1); print("saved", old)
    elif c == "release":
        rp = os.path.join(D, "release.json"); rel = json.load(open(rp)) if os.path.exists(rp) else {}
        problems = []
        bad = regress(s); save(s)
        if bad: problems.append("earlier fixes failing again: " + ", ".join(bad))
        op = [x for x in s["findings"] if x["status"] in ("open", "in_progress")]
        for x in op: problems.append(f'not fixed: {x["id"]} {x["sev"]} {x["title"]}')
        for x in s["findings"]:
            if x["status"] == "blocked": problems.append(f'blocked on you: {x["id"]} {x["sev"]} {x["title"]} ({x["reason"][:80]})')
            if x["status"] == "wontfix" and x["sev"] in ("Critical", "High"): problems.append(f'wontfix on a {x["sev"]}: {x["id"]} {x["title"]} (needs explicit sign-off)')
        cv = cov_load(); un = [r for r in cv[1:] if r[4] == "unchecked"]
        if un: problems.append(f"{len(un)} coverage rows unchecked")
        ps = s["passes"]
        if not (len(ps) >= 2 and all(p["new"] == 0 for p in ps[-2:])): problems.append("need two consecutive clean re-audit passes")
        for k in ("build", "test", "smoke"):
            if k not in rel: problems.append(f"no {k} command recorded (release-set --{k} ...)"); continue
            code, tail = run(rel[k])
            print(f"{k}: {'ok' if code == 0 else 'FAILED'}  ({rel[k]})")
            if code: problems.append(f"{k} failed: {tail[-150:]}")
        for p in problems: print("  NO-GO:", p)
        print("RELEASE:", "GO (all checks passed; deploying is a separate step that needs the user's yes)" if not problems else "NO-GO"); sys.exit(1 if problems else 0)
    elif c == "coverage":
        rows = cov_load(); un = [r for r in rows[1:] if r[4] == "unchecked"]; tot = len(rows) - 1
        print(f"coverage: {tot - len(un)}/{tot} rows closed, {len(un)} unchecked")
        for r in un[:15]: print("  next:", r[0], r[2], r[1][:70])
        sys.exit(1 if un else 0)
    elif c == "report":
        print("| id | severity | status | title | proof or reason |\n|---|---|---|---|---|")
        for x in sorted(s["findings"], key=lambda x: (SEVS.index(x["sev"]), x["id"])):
            print(f'| {x["id"]} | {x["sev"]} | {x["status"]} | {x["title"]} | {(x["proof"] or x["reason"] or "-")[:90]} |')
    else: sys.exit(__doc__)

main()
