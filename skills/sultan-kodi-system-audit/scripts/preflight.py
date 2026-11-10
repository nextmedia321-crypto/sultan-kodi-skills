#!/usr/bin/env python3
"""Cheap pre-flight BEFORE spending tokens on an audit/repair run: can this project be built and tested at all?
Usage: preflight.py [project]   (exit 0 = ready to start, 1 = fix these blockers first)
Most wasted runs start on a project that cannot install, build or run tests. This finds that in seconds."""
import os, sys, subprocess, shutil, json
root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "."); blockers = []; notes = []
def has(n): return os.path.exists(os.path.join(root, n))
def run(cmd, t=240):
    try: r = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=t, shell=isinstance(cmd, str)); return r.returncode, (r.stdout + r.stderr)[-250:]
    except Exception as e: return 1, str(e)[:120]
print(f"# Pre-flight for {root}")
if has(".git"):
    c, o = run(["git", "status", "--porcelain"]); n = len([l for l in o.split("\n") if l.strip()]) if c == 0 else 0
    notes.append(f"git: {'clean' if not n else str(n) + ' uncommitted changes (commit or branch first)'}")
else: notes.append("not a git repo: work on a copy")
if has("package.json"):
    j = json.load(open(os.path.join(root, "package.json"))); sc = j.get("scripts", {})
    if not shutil.which("node"): blockers.append("node is not installed")
    elif not has("node_modules"): blockers.append("node_modules missing: run the install command first (npm ci / pnpm i)")
    for k in ("build", "test", "lint", "typecheck"):
        if k in sc:
            c, o = run(["npm", "run", k, "--silent"], 480) if k != "test" else run("npm test --silent -- --passWithNoTests 2>&1", 480)
            notes.append(f"npm run {k}: {'ok' if c == 0 else 'FAILS'}")
            if c and k in ("build", "test"): blockers.append(f"`npm run {k}` fails before any change: {o.strip()[-120:]} (record as baseline, or fix first)")
        elif k in ("build", "test"): notes.append(f"no {k} script (a check will have to be created)")
elif has("requirements.txt") or has("pyproject.toml"):
    if has("tests") or has("test"): 
        c, o = run([sys.executable, "-m", "pytest", "-x", "-q"], 480); notes.append(f"pytest: {'ok' if c == 0 else 'FAILS or missing'}")
        if c: blockers.append("python tests fail or pytest is missing: " + o.strip()[-120:])
    else: notes.append("no tests folder")
elif has("go.mod"):
    c, o = run(["go", "build", "./..."]); notes.append(f"go build: {'ok' if c == 0 else 'FAILS'}")
    if c: blockers.append("go build fails: " + o.strip()[-120:])
else: notes.append("stack not recognized: ask how to build and run it")
if has(".env.example") and not has(".env") and not has(".env.local"): notes.append("no .env: the app may need local test values (never production values)")
for t in ("npm", "node", "python3", "git"):
    if not shutil.which(t): notes.append(f"missing tool: {t}")
for n in notes: print("  -", n)
for b in blockers: print("  BLOCKER:", b)
print("READY" if not blockers else "NOT READY: fix the blockers first, otherwise tokens are spent on a broken base"); sys.exit(1 if blockers else 0)
