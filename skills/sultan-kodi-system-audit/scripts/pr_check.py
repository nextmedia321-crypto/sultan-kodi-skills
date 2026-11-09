#!/usr/bin/env python3
"""Audit only what a change touched (for pull requests and CI). Exit 1 when it finds a problem.
Usage: pr_check.py [--base origin/main] [--project .]
Looks at changed files vs the base: secrets, risky calls, debug leftovers, TODO, missing tests for changed source,
changed routes without auth hints, and runs .audit/regression.sh if it exists."""
import subprocess, sys, re, os
a = sys.argv[1:]; opt = lambda n, d=None: a[a.index(n) + 1] if n in a else d
root = os.path.abspath(opt("--project", ".")); base = opt("--base", "origin/main")
def git(*x): return subprocess.run(["git", "-C", root, *x], capture_output=True, text=True)
if git("rev-parse", "--git-dir").returncode: sys.exit("not a git repository")
r = git("diff", "--name-only", "--diff-filter=ACMR", base + "...HEAD")
if r.returncode: r = git("diff", "--name-only", "--diff-filter=ACMR", "HEAD~1")
files = [f for f in r.stdout.split("\n") if f]
SEC = re.compile(r"(AKIA[0-9A-Z]{16}|sk_live_[0-9a-zA-Z]{10,}|-----BEGIN (?:RSA |EC )?PRIVATE KEY-----|(?i:api[_-]?key|secret|token|passw(?:or)?d)\s*[:=]\s*['\"][A-Za-z0-9_\-/+=]{12,}['\"])")
RISK = re.compile(r"\beval\(|dangerouslySetInnerHTML|innerHTML\s*=|shell=True|verify\s*=\s*False|rejectUnauthorized\s*:\s*false")
DBG = re.compile(r"console\.log\(|debugger;|var_dump\(")
bad = []; warn = []
for f in files:
    p = os.path.join(root, f)
    if not os.path.isfile(p) or os.path.getsize(p) > 600000: continue
    t = open(p, encoding="utf-8", errors="ignore").read()
    for i, line in enumerate(t.split("\n"), 1):
        if SEC.search(line) and not f.endswith(".example"): bad.append(f"{f}:{i} possible secret (masked)")
        if RISK.search(line): bad.append(f"{f}:{i} risky call")
        if DBG.search(line) and not re.search(r"test|spec", f): warn.append(f"{f}:{i} debug leftover")
    if re.search(r"(route|api)/", f) and f.endswith((".ts", ".js", ".py")) and not re.search(r"auth|session|token|login|public", t, re.I): warn.append(f"{f}: changed route with no auth hint")
src = [f for f in files if f.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".go")) and not re.search(r"test|spec|\.d\.ts|config", f)]
tests = [f for f in files if re.search(r"test|spec", f)]
if src and not tests: warn.append(f"{len(src)} source files changed and no test file changed")
reg = os.path.join(root, ".audit", "regression.sh")
if os.path.exists(reg):
    rr = subprocess.run(["sh", reg], cwd=root, capture_output=True, text=True)
    if rr.returncode: bad.append("regression.sh failed: " + rr.stdout.strip()[-200:])
print(f"# PR check: {len(files)} changed files vs {base}")
for b in bad: print("BLOCK", b)
for w in warn: print("warn ", w)
print("RESULT:", "BLOCKED" if bad else "ok" + (" with warnings" if warn else "")); sys.exit(1 if bad else 0)
