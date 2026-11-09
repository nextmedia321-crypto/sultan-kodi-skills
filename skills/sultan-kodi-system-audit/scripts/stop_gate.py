#!/usr/bin/env python3
"""Claude Code Stop hook. While repair mode is on (.audit/active exists) it blocks the session from
ending until `ledger.py gate` passes. Inert in every other project or when repair mode is off.
Loop guard: after MAX_BLOCKS consecutive blocks with no change in the ledger it lets the session end
and says why, so a stuck job cannot loop forever."""
import json, os, subprocess, sys, hashlib

MAX_BLOCKS = 12
try: data = json.load(sys.stdin)
except Exception: data = {}
root = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
audit = os.path.join(root, ".audit")
if not os.path.exists(os.path.join(audit, "active")) or not os.path.exists(os.path.join(audit, "findings.json")): sys.exit(0)
here = os.path.dirname(os.path.abspath(__file__))
env = dict(os.environ, AUDIT_DIR=audit)
r = subprocess.run([sys.executable, os.path.join(here, "ledger.py"), "gate"], capture_output=True, text=True, cwd=root, env=env)
if r.returncode == 0: sys.exit(0)
state = os.path.join(audit, "stopstate.json")
h = hashlib.sha1(open(os.path.join(audit, "findings.json"), "rb").read()).hexdigest()
try: st = json.load(open(state))
except Exception: st = {"hash": "", "n": 0}
st["n"] = st["n"] + 1 if st["hash"] == h else 1; st["hash"] = h
json.dump(st, open(state, "w"))
if st["n"] > MAX_BLOCKS:
    print("Stop gate released after %d blocks with no ledger progress. Report exactly what is blocked and what you need from the user." % MAX_BLOCKS, file=sys.stderr); sys.exit(0)
print("Repair mode is on and the completion gate has not passed. Do not stop or summarize as finished. Continue the repair loop.\n" + r.stdout.strip()[-1500:], file=sys.stderr)
sys.exit(2)
