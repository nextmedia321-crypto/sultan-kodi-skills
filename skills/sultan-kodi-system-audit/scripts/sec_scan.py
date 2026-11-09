#!/usr/bin/env python3
"""Run the real security scanners that are installed, for the project types found. Never installs anything.
Usage: sec_scan.py [project] [--json out.json]
Each tool is reported as ran, not installed (with the install hint) or failed. Findings are summarized
with counts and the top items so they can be added to the ledger."""
import json, os, re, shutil, subprocess, sys, time

args = [a for a in sys.argv[1:] if not a.startswith("--")]
root = os.path.abspath(args[0] if args else ".")
out_json = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
has = lambda *names: any(os.path.exists(os.path.join(root, n)) for n in names)
results = []

def run(name, cmd, parse, hint, applies=True):
    if not applies: return
    exe = cmd[0]
    if not shutil.which(exe):
        results.append({"tool": name, "status": "not installed", "hint": hint}); return
    t = time.time()
    try:
        r = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=600)
    except Exception as e:
        results.append({"tool": name, "status": "failed", "detail": str(e)[:200]}); return
    try: summary = parse(r)
    except Exception as e: summary = {"note": f"could not parse output: {str(e)[:100]}", "tail": (r.stdout + r.stderr)[-300:]}
    results.append({"tool": name, "status": "ran", "seconds": round(time.time() - t, 1), **summary})

def npm_audit(r):
    j = json.loads(r.stdout or "{}"); v = j.get("metadata", {}).get("vulnerabilities", {})
    if not v and "error" in j: return {"note": "npm audit error: " + str(j["error"].get("summary", ""))[:150]}
    items = [f'{k} ({x.get("severity")})' for k, x in list(j.get("vulnerabilities", {}).items())[:8]]
    return {"counts": v, "top": items}
def pip_audit(r):
    j = json.loads(r.stdout or "{}"); deps = j.get("dependencies", j if isinstance(j, list) else [])
    bad = [f'{d["name"]} {d.get("version")}: ' + ", ".join(x["id"] for x in d.get("vulns", [])) for d in deps if d.get("vulns")]
    return {"vulnerable_packages": len(bad), "top": bad[:8]}
def bandit(r):
    j = json.loads(r.stdout or "{}"); res = j.get("results", [])
    c = {}; [c.__setitem__(x["issue_severity"], c.get(x["issue_severity"], 0) + 1) for x in res]
    return {"counts": c, "top": [f'{x["filename"]}:{x["line_number"]} {x["test_id"]} {x["issue_text"][:70]}' for x in res[:8]]}
def gitleaks(r):
    return {"exit": r.returncode, "leaks_found": r.returncode == 1, "tail": (r.stdout + r.stderr)[-300:]}
def semgrep(r):
    j = json.loads(r.stdout or "{}"); res = j.get("results", [])
    return {"count": len(res), "top": [f'{x["path"]}:{x["start"]["line"]} {x["check_id"].split(".")[-1]}' for x in res[:8]]}
def trivy(r):
    j = json.loads(r.stdout or "{}"); n = 0; top = []
    for res in j.get("Results", []):
        for v in res.get("Vulnerabilities", []) or []: n += 1; top.append(f'{v["VulnerabilityID"]} {v["PkgName"]} ({v["Severity"]})')
    return {"vulnerabilities": n, "top": top[:8]}
def osv(r):
    j = json.loads(r.stdout or "{}"); n = sum(len(p.get("vulnerabilities", [])) for res in j.get("results", []) for p in res.get("packages", []))
    return {"vulnerabilities": n}
def plain(r): return {"exit": r.returncode, "tail": (r.stdout + r.stderr)[-400:]}

run("npm audit", ["npm", "audit", "--json"], npm_audit, "install Node.js/npm", has("package-lock.json", "package.json"))
run("pip-audit", ["pip-audit", "-f", "json"], pip_audit, "python3 -m pip install --user pip-audit", has("requirements.txt", "pyproject.toml", "Pipfile"))
run("bandit", ["bandit", "-r", ".", "-f", "json", "-q"], bandit, "python3 -m pip install --user bandit", any(f.endswith(".py") for _, _, fs in os.walk(root) for f in fs))
run("gitleaks", ["gitleaks", "detect", "--no-banner", "--redact", "-s", "."], gitleaks, "brew install gitleaks")
run("semgrep", ["semgrep", "--config", "auto", "--json", "--quiet", "."], semgrep, "python3 -m pip install --user semgrep (needs network for rules)")
run("trivy", ["trivy", "fs", "--quiet", "--format", "json", "."], trivy, "brew install trivy")
run("osv-scanner", ["osv-scanner", "--format", "json", "-r", "."], osv, "brew install osv-scanner")
run("govulncheck", ["govulncheck", "./..."], plain, "go install golang.org/x/vuln/cmd/govulncheck@latest", has("go.mod"))
run("cargo audit", ["cargo", "audit"], plain, "cargo install cargo-audit", has("Cargo.toml"))
run("bundler-audit", ["bundle-audit", "check"], plain, "gem install bundler-audit", has("Gemfile.lock"))

# built-in fallback so a secret scan always happens
if not any(r["tool"] == "gitleaks" and r["status"] == "ran" for r in results):
    rx = re.compile(r"(AKIA[0-9A-Z]{16}|sk_live_[0-9a-zA-Z]{10,}|-----BEGIN (?:RSA |EC )?PRIVATE KEY-----|(?i:api[_-]?key|secret|token|passw(?:or)?d)\s*[:=]\s*['\"][A-Za-z0-9_\-/+=]{12,}['\"])")
    hits = []
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in {".git", "node_modules", ".next", "dist", "build", "venv", ".venv", "__pycache__", ".audit"}]
        for f in fs:
            p = os.path.join(d, f)
            try:
                if os.path.getsize(p) > 500000: continue
                for i, line in enumerate(open(p, encoding="utf-8", errors="ignore"), 1):
                    if rx.search(line): hits.append(f"{os.path.relpath(p, root)}:{i}")
            except OSError: pass
    results.append({"tool": "built-in secret patterns", "status": "ran", "possible_secrets": len(hits), "top": hits[:10]})

print(f"# Security scan of {root}")
for r in results:
    print(f"\n[{r['status'].upper()}] {r['tool']}" + (f"  ({r['seconds']}s)" if "seconds" in r else ""))
    for k, v in r.items():
        if k in ("tool", "status", "seconds"): continue
        if isinstance(v, list):
            for item in v: print("   -", item)
        else: print(f"   {k}: {v}")
missing = [r["tool"] for r in results if r["status"] == "not installed"]
if missing: print("\nNot installed (coverage gap, record in the ledger as not checkable until installed):", ", ".join(missing))
if out_json: json.dump(results, open(out_json, "w"), indent=1); print("saved", out_json)
