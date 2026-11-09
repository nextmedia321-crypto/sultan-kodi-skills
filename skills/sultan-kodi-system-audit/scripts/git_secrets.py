#!/usr/bin/env python3
"""Find secrets that were removed from the code but still live in git history. Masks every value.
Usage: git_secrets.py [project] [--max-commits 2000]
Reports commit, file and pattern kind only. Any hit means rotate the secret first, then consider history rewriting (ask the user)."""
import subprocess, sys, re, os
a = sys.argv[1:]; root = os.path.abspath(a[0] if a and not a[0].startswith("--") else "."); mc = a[a.index("--max-commits") + 1] if "--max-commits" in a else "2000"
if subprocess.run(["git", "-C", root, "rev-parse"], capture_output=True).returncode: sys.exit("not a git repository")
P = {"AWS key": r"AKIA[0-9A-Z]{16}", "Stripe live key": r"sk_live_[0-9a-zA-Z]{10,}", "private key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", "GitHub token": r"gh[pousr]_[A-Za-z0-9]{30,}", "Slack token": r"xox[baprs]-[A-Za-z0-9-]{10,}", "Google API key": r"AIza[0-9A-Za-z_\-]{35}", "JWT": r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "generic secret assignment": r"(?i)(?:api[_-]?key|secret|token|passw(?:or)?d)\s*[:=]\s*['\"][A-Za-z0-9_\-/+=]{16,}['\"]"}
RX = {k: re.compile(v) for k, v in P.items()}
p = subprocess.Popen(["git", "-C", root, "log", "--all", "-p", "-U0", f"--max-count={mc}", "--format=@@@%h %ad", "--date=short"], stdout=subprocess.PIPE, text=True, errors="ignore")
commit = ""; fil = ""; hits = {}; env_files = set()
for line in p.stdout:
    if line.startswith("@@@"): commit = line[3:].strip(); continue
    if line.startswith("+++ b/"): fil = line[6:].strip(); continue
    if re.search(r"(^|/)\.env(\.|$)", fil) and not fil.endswith((".example", ".sample")): env_files.add((commit, fil))
    if not line.startswith("+") or line.startswith("+++"): continue
    for k, rx in RX.items():
        if rx.search(line) and not re.search(r"example|placeholder|your[_-]|xxxx|test|dummy", line, re.I): hits.setdefault((k, fil), commit)
print(f"# Secrets in git history of {root} (values never printed)")
for (k, f), c in sorted(hits.items()): print(f"  {k}  in {f}  first seen at commit {c}")
for c, f in sorted(env_files)[:10]: print(f"  .env file committed: {f} (commit {c})")
n = len(hits) + len(env_files)
print(f"HITS: {n}" + ("\nNext: rotate each secret NOW (history rewriting does not make a leaked secret safe), then ask the user before rewriting history." if n else "")); sys.exit(1 if n else 0)
