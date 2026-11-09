#!/usr/bin/env python3
"""Map the services in a repo or folder of repos: service roots, routes they expose, outbound calls to other
services, shared databases, and mismatches between what is called and what exists.
Usage: map_services.py [dir]  (a monorepo, or a parent folder holding several repos)"""
import os, re, sys, collections, json
root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
SKIP = {".git", "node_modules", ".next", "dist", "build", "venv", ".venv", "__pycache__", "vendor"}
MAN = ("package.json", "pyproject.toml", "requirements.txt", "go.mod", "Cargo.toml", "pom.xml", "composer.json", "Gemfile")
svcs = {}
for d, dirs, fs in os.walk(root):
    dirs[:] = [x for x in dirs if x not in SKIP]
    if any(m in fs for m in MAN) or "Dockerfile" in fs:
        if not any(d != s and d.startswith(s + os.sep) and os.path.exists(os.path.join(s, "package.json")) and False for s in svcs): svcs[d] = {}
# keep only top-most service roots unless nested ones have their own Dockerfile
roots = [d for d in svcs if not any(d != o and d.startswith(o + os.sep) and "Dockerfile" not in os.listdir(d) for o in svcs)]
ROUTE = [re.compile(r"\b(?:app|router|api)\.(get|post|put|patch|delete)\(\s*['\"`](/[^'\"`]*)"), re.compile(r"@(?:app|router|bp)\.(get|post|put|patch|delete|route)\(\s*['\"](/[^'\"]*)"), re.compile(r"\.(?:GET|POST|PUT|DELETE|PATCH)\(\s*\"(/[^\"]*)")]
CALL = [re.compile(r"(?:fetch|axios\.\w+|requests\.\w+|httpx\.\w+|http\.(?:Get|Post)|got\.\w+)\(\s*[`'\"]([^`'\"]+)"), re.compile(r"(?:BASE_URL|API_URL|SERVICE_URL|_HOST)\s*[:=]\s*['\"]([^'\"]+)")]
DB = re.compile(r"(postgres(?:ql)?://[^\s'\"`]+|mongodb(?:\+srv)?://[^\s'\"`]+|mysql://[^\s'\"`]+|redis://[^\s'\"`]+|DATABASE_URL|MONGO_URI|REDIS_URL|sqlite:///[^\s'\"`]+)")
info = {}
for r in roots:
    name = os.path.relpath(r, root) if r != root else os.path.basename(root)
    routes, calls, dbs, envs = set(), collections.Counter(), set(), set()
    for d, dirs, fs in os.walk(r):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for f in fs:
            if not f.endswith((".js", ".ts", ".tsx", ".jsx", ".py", ".go", ".rb", ".php", ".yml", ".yaml", ".env", ".example", ".json")): continue
            try: t = open(os.path.join(d, f), encoding="utf-8", errors="ignore").read() if os.path.getsize(os.path.join(d, f)) < 600000 else ""
            except OSError: continue
            for rx in ROUTE:
                for m in rx.finditer(t): routes.add(m.group(m.lastindex))
            for rx in CALL:
                for m in rx.finditer(t): calls[m.group(1)[:90]] += 1
            for m in DB.finditer(t):
                v = m.group(1); v = re.sub(r"//[^@/]*@", "//***@", v); dbs.add(v[:60])
            envs.update(re.findall(r"process\.env\.([A-Z0-9_]+)|os\.environ(?:\.get)?\(?\[?['\"]([A-Z0-9_]+)", t) and [x for tup in re.findall(r"process\.env\.([A-Z0-9_]+)|os\.environ(?:\.get)?\(?\[?['\"]([A-Z0-9_]+)", t) for x in tup if x])
    info[name] = {"routes": sorted(routes), "calls": calls, "dbs": sorted(dbs), "envs": sorted(envs)}
print(f"# Service map of {root}\nservices found: {len(info)}")
for n, i in info.items():
    print(f"\n## {n}\n   routes exposed: {len(i['routes'])}  " + ", ".join(i["routes"][:8]) + ("..." if len(i["routes"]) > 8 else ""))
    ext = [(u, c) for u, c in i["calls"].most_common(12)]
    print("   outbound calls:"); [print(f"     - {u}  x{c}") for u, c in ext] if ext else print("     none")
    print("   data stores referenced:", ", ".join(i["dbs"]) or "none")
shared = collections.defaultdict(list)
for n, i in info.items():
    for d in i["dbs"]: shared[d].append(n)
print("\n## Shared data stores")
hit = False
for d, ns in shared.items():
    if len(ns) > 1: hit = True; print(f"   {d} used by {', '.join(ns)}  (shared database: check ownership of the schema and migrations)")
if not hit: print("   none detected")
print("\n## Possible contract mismatches (calls to a path no service exposes)")
allr = {r for i in info.values() for r in i["routes"]}; mism = 0
for n, i in info.items():
    for u in i["calls"]:
        m = re.match(r"^(?:https?://[^/]+)?(/[A-Za-z0-9_\-/\.]*)", u)
        if m and m.group(1).startswith("/api") and m.group(1) not in allr and not any(re.sub(r":\w+|\[\w+\]|\{\w+\}", "", r) and m.group(1).startswith(re.sub(r"/(:\w+|\[\w+\]|\{\w+\}).*", "", r)) for r in allr):
            mism += 1; print(f"   {n} calls {u} but no scanned service exposes it")
if not mism: print("   none detected (static match only; dynamic URLs and external APIs are not resolved)")
