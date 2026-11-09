#!/usr/bin/env python3
"""Install or remove the Stop hook in a project's .claude/settings.json (needs the user's approval first).
Usage: install_hook.py <project> [--remove] [--print]"""
import json, os, sys
args = [a for a in sys.argv[1:] if not a.startswith("--")]
if not args: sys.exit(__doc__)
proj = os.path.abspath(args[0]); path = os.path.join(proj, ".claude", "settings.json")
cmd = f'python3 "{os.path.join(os.path.dirname(os.path.abspath(__file__)), "stop_gate.py")}"'
entry = {"hooks": [{"type": "command", "command": cmd}]}
if "--print" in sys.argv: print(json.dumps({"hooks": {"Stop": [entry]}}, indent=2)); sys.exit()
cfg = json.load(open(path)) if os.path.exists(path) else {}
stops = cfg.setdefault("hooks", {}).setdefault("Stop", [])
stops[:] = [e for e in stops if "stop_gate.py" not in json.dumps(e)]
if "--remove" not in sys.argv: stops.append(entry)
if not stops: cfg["hooks"].pop("Stop")
os.makedirs(os.path.dirname(path), exist_ok=True); json.dump(cfg, open(path, "w"), indent=2)
print(("removed from " if "--remove" in sys.argv else "installed in ") + path)
