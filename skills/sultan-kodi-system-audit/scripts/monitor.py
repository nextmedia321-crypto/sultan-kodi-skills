#!/usr/bin/env python3
"""Nightly monitor: a lightweight re-check that reports only what CHANGED since last run. Read-only on the project.
Usage: monitor.py [project] [--url http://staging...]      (cron/scheduled-task friendly; exit 1 when something got worse)
Runs: sec_scan.py (installed scanners + secret patterns), regression.sh if present, git_secrets.py, pii flags count, optional URL status.
Stores .audit/monitor/<date>.json and writes .audit/monitor/latest.md with new / resolved items."""
import json, os, subprocess, sys, time, re, urllib.request
a = sys.argv[1:]; root = os.path.abspath(a[0] if a and not a[0].startswith("--") else "."); url = a[a.index("--url") + 1] if "--url" in a else None
H = os.path.dirname(os.path.abspath(__file__)); M = os.path.join(root, ".audit", "monitor"); os.makedirs(M, exist_ok=True)
def run(cmd, **k): return subprocess.run(cmd, capture_output=True, text=True, timeout=900, cwd=root, **k)
state = {"t": time.strftime("%Y-%m-%d %H:%M"), "items": {}}
r = run([sys.executable, os.path.join(H, "sec_scan.py"), root, "--json", os.path.join(M, "_sec.json")])
try:
    for t in json.load(open(os.path.join(M, "_sec.json"))):
        if t["status"] == "ran":
            for k in ("top", "counts", "count", "vulnerabilities", "possible_secrets", "vulnerable_packages", "leaks_found"):
                if t.get(k): state["items"][f"scan:{t['tool']}:{k}"] = json.dumps(t[k], sort_keys=True)[:300]
except Exception: state["items"]["scan:error"] = "sec_scan output unreadable"
if os.path.isdir(os.path.join(root, ".git")):
    g = run([sys.executable, os.path.join(H, "git_secrets.py"), root])
    for l in g.stdout.split("\n"):
        if l.startswith("  ") and "first seen" in l or ".env file committed" in l: state["items"]["history:" + l.strip()[:120]] = "present"
reg = os.path.join(root, ".audit", "regression.sh")
if os.path.exists(reg):
    out = run(["sh", reg]).stdout
    for l in out.split("\n"):
        if l.startswith("FAILED"): state["items"]["regression:" + l] = "failing"
p = run([sys.executable, os.path.join(H, "pii_map.py"), root]).stdout
m = re.search(r"FLAGS: (.*)", p)
if m and m.group(1) != "none": state["items"]["pii:" + m.group(1)[:160]] = "flagged"
if url:
    try:
        with urllib.request.urlopen(url, timeout=15) as x: code = x.status
    except urllib.error.HTTPError as e: code = e.code
    except Exception as e: code = "unreachable"
    if code != 200: state["items"]["uptime:" + url] = f"status {code}"
files = sorted(f for f in os.listdir(M) if re.match(r"\d{8}-\d{4}\.json", f))
prev = json.load(open(os.path.join(M, files[-1]))) if files else None
json.dump(state, open(os.path.join(M, time.strftime("%Y%m%d-%H%M") + ".json"), "w"), indent=1)
for f in files[:-30]: os.remove(os.path.join(M, f))
if os.path.exists(os.path.join(M, "_sec.json")): os.remove(os.path.join(M, "_sec.json"))
new = [k for k in state["items"] if not prev or k not in prev["items"] or prev["items"][k] != state["items"][k]]
gone = [k for k in (prev["items"] if prev else {}) if k not in state["items"]]
lines = [f"# Monitor {state['t']} for {root}", f"previous run: {prev['t'] if prev else 'none (this is the baseline)'}", f"open items now: {len(state['items'])}", "", f"## NEW or changed ({len(new)})"] + [f"- {k}: {state['items'][k]}" for k in new] + [f"\n## RESOLVED ({len(gone)})"] + [f"- {k}" for k in gone]
open(os.path.join(M, "latest.md"), "w").write("\n".join(lines) + "\n"); print("\n".join(lines))
sys.exit(1 if new and prev else 0)
