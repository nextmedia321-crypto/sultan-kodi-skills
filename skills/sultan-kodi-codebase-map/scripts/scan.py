#!/usr/bin/env python3
"""Fast project scan. Usage: scan.py [path] [depth]"""
import os, re, sys, json, collections
root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "."); depth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
SKIP = {".git", "node_modules", ".next", "dist", "build", "__pycache__", ".venv", "venv", "vendor", ".turbo", "coverage", ".cache"}
exts = collections.Counter(); sizes = []; files = []
for d, dirs, fs in os.walk(root):
    dirs[:] = [x for x in dirs if x not in SKIP]
    for f in fs:
        p = os.path.join(d, f); files.append(p)
        exts[os.path.splitext(f)[1] or f] += 1
        try: sizes.append((os.path.getsize(p), os.path.relpath(p, root)))
        except OSError: pass
print(f"== {root}\nfiles: {len(files)}")
print("== top file types:", ", ".join(f"{k or 'none'} {v}" for k, v in exts.most_common(8)))
print("== tree (depth %d)" % depth)
for d, dirs, fs in os.walk(root):
    dirs[:] = sorted(x for x in dirs if x not in SKIP)
    lvl = os.path.relpath(d, root).count(os.sep) if d != root else 0
    if lvl >= depth: dirs[:] = []; continue
    n = sum(len(f) for _, _, f in os.walk(d))
    if d != root: print("  " * lvl + os.path.basename(d) + f"/  ({n} files)")
print("== entry points & manifests")
for name in ("package.json", "pyproject.toml", "requirements.txt", "go.mod", "Cargo.toml", "pom.xml", "Dockerfile", "docker-compose.yml", "next.config.js", "vite.config.ts", "main.py", "app.py", "index.js", "server.js", "README.md"):
    if os.path.exists(os.path.join(root, name)): print(" -", name)
pj = os.path.join(root, "package.json")
if os.path.exists(pj):
    try:
        j = json.load(open(pj)); print("   scripts:", ", ".join(j.get("scripts", {}))); print("   deps:", ", ".join(list(j.get("dependencies", {}))[:15]))
    except Exception: pass
fan = collections.Counter()
for p in files:
    if p.endswith((".js", ".jsx", ".ts", ".tsx", ".mjs", ".py")):
        try: txt = open(p, encoding="utf-8", errors="ignore").read()
        except OSError: continue
        for m in re.findall(r"""(?:from|require\(|import)\s*['"](\.{1,2}/[^'"]+)['"]""", txt) + re.findall(r"^from\s+(\.[\w\.]*)\s+import", txt, re.M):
            fan[os.path.normpath(os.path.join(os.path.dirname(p), m))] += 1
print("== most imported local modules (danger zones)")
for k, v in fan.most_common(8): print(f"  {v:3d}  {os.path.relpath(k, root)}")
print("== largest files")
for s, r in sorted(sizes, reverse=True)[:6]: print(f"  {s // 1024:5d} KB  {r}")
