#!/usr/bin/env python3
"""Deployment readiness check: env variables used vs documented vs configured for deploy, health check, rollback, CI, secrets in configs.
Usage: deploy_check.py [project]"""
import os, re, sys, json
root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
SKIP = {".git", "node_modules", ".next", "dist", "build", "venv", ".venv", "__pycache__", "vendor", ".audit"}
used = {}; deploy_text = ""; flags = []
for d, dirs, fs in os.walk(root):
    dirs[:] = [x for x in dirs if x not in SKIP]
    for f in fs:
        p = os.path.join(d, f); rel = os.path.relpath(p, root)
        if f in ("vercel.json", "netlify.toml", "fly.toml", "render.yaml", "railway.json", "Procfile", "docker-compose.yml", "docker-compose.yaml", "Dockerfile", "app.yaml", "serverless.yml") or ".github/workflows" in rel.replace("\\", "/"):
            deploy_text += open(p, encoding="utf-8", errors="ignore").read() + "\n"
        if f.endswith((".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rb", ".php")):
            try: t = open(p, encoding="utf-8", errors="ignore").read() if os.path.getsize(p) < 600000 else ""
            except OSError: continue
            for m in re.finditer(r"process\.env\.([A-Z][A-Z0-9_]+)|os\.environ(?:\.get)?\(?\[?['\"]([A-Z][A-Z0-9_]+)|os\.Getenv\(\"([A-Z0-9_]+)|getenv\(['\"]([A-Z0-9_]+)", t):
                n = next(g for g in m.groups() if g); used.setdefault(n, rel)
doc = set()
for n in (".env.example", ".env.sample", ".env.template", "README.md"):
    p = os.path.join(root, n)
    if os.path.exists(p): doc |= set(re.findall(r"\b([A-Z][A-Z0-9_]{2,})\b", open(p, encoding="utf-8", errors="ignore").read()))
SYS = {"NODE_ENV", "PORT", "HOME", "PATH", "CI", "PWD", "USER", "HOSTNAME", "TZ", "PYTHONPATH", "VERCEL", "VERCEL_URL", "NEXT_PUBLIC_VERCEL_URL"}
undoc = sorted(n for n in used if n not in doc and n not in SYS)
print(f"# Deployment check of {root}\nenv variables used in code: {len(used)}")
if undoc: flags.append(f"{len(undoc)} env variables not documented in .env.example/README: " + ", ".join(undoc[:12]))
if not any(os.path.exists(os.path.join(root, n)) for n in (".env.example", ".env.sample", ".env.template")): flags.append("no .env.example")
unset = [n for n in used if deploy_text and n not in deploy_text and n not in SYS and n in doc]
if deploy_text and unset: print("   note: not referenced in deploy configs (may be set in the host dashboard, verify there):", ", ".join(sorted(unset)[:10]))
tx = "".join(open(os.path.join(d, f), encoding="utf-8", errors="ignore").read() for d, ds, fs in os.walk(root) if not set(d.split(os.sep)) & SKIP for f in fs if f.endswith((".py", ".js", ".ts")) and os.path.getsize(os.path.join(d, f)) < 400000)
if not re.search(r"/health|/healthz|/ping|/status|readiness|liveness", tx + deploy_text, re.I): flags.append("no health check endpoint found")
if not os.path.exists(os.path.join(root, ".github", "workflows")) and not os.path.exists(os.path.join(root, ".gitlab-ci.yml")): flags.append("no CI pipeline found")
if not any(re.search(r"rollback|previous release|revert", open(os.path.join(root, n), encoding="utf-8", errors="ignore").read(), re.I) for n in os.listdir(root) if n.lower().endswith(".md") and os.path.isfile(os.path.join(root, n))): flags.append("no rollback plan found in docs")
if re.search(r"NODE_ENV\s*[:=]\s*['\"]?development", deploy_text): flags.append("deploy config sets NODE_ENV=development")
if re.search(r"(?i)(secret|password|token|api_key)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}", deploy_text): flags.append("possible literal secret inside a deploy config")
if re.search(r"(?i)debug\s*[:=]\s*['\"]?(true|1)", deploy_text): flags.append("DEBUG enabled in a deploy config")
if os.path.exists(os.path.join(root, "Dockerfile")) and not re.search(r"^USER\s+(?!root)", open(os.path.join(root, "Dockerfile")).read(), re.M): flags.append("Dockerfile runs as root (no non-root USER)")
if not deploy_text: print("   no deploy config files found: production setup is not visible here; ask where it runs (cannot check staging vs production differences without access)")
for f in flags: print("FLAG", f)
print(f"FLAGS: {len(flags)}"); sys.exit(1 if flags else 0)
