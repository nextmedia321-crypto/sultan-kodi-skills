#!/usr/bin/env python3
"""Static scan of a skill or plugin folder. Reads only; never executes anything.
Usage: scan.py path/to/skill"""
import os, re, sys
RULES = [
 ("High", r"curl[^\n|]*\|\s*(ba|z)?sh|wget[^\n|]*\|\s*(ba|z)?sh", "downloads and runs remote code"),
 ("High", r"\beval\s*\(|\bexec\s*\(|base64\s+(-d|--decode)|atob\(|FromBase64String", "dynamic or encoded code execution"),
 ("High", r"(~|\$HOME|%USERPROFILE%)/?\.(ssh|aws|gnupg|config/gcloud)|id_rsa|\.npmrc|\.netrc|keychain|Login Data|wallet\.dat", "touches credentials or key stores"),
 ("High", r"\brm\s+-rf?\s+(/|~|\$HOME)(\s|$|/\*)|mkfs\.|dd\s+if=.*of=/dev/", "destructive filesystem command"),
 ("High", r"(curl|wget|nc|requests\.post|fetch)\b[^\n]*(\$\{?[A-Z_]*(KEY|TOKEN|SECRET|PASSWORD)|\.env)", "may send secrets to a remote host"),
 ("Medium", r"sudo\s|chmod\s+(\+s|777)|launchctl|crontab|systemctl\s+enable|LaunchAgents|\.bashrc|\.zshrc|\.profile", "persistence or privilege change"),
 ("Medium", r"ignore (all |any )?(previous|prior) instructions|disregard (the )?(above|system)|do not (tell|inform) the user|without (asking|telling) the user", "prompt-injection style wording"),
 ("Medium", r"pip install|npm (i|install)\s|gem install|go install", "installs packages at runtime"),
 ("Low", r"https?://[^\s'\")]+", "external URL (check what it is used for)"),
 ("Low", r"[A-Za-z0-9+/]{120,}={0,2}", "long encoded-looking blob"),
]
if len(sys.argv) < 2: sys.exit(__doc__)
root = sys.argv[1]; found = []; n = 0; skipped = []
for d, dirs, fs in os.walk(root):
    dirs[:] = [x for x in dirs if x != ".git"]
    for f in fs:
        p = os.path.join(d, f)
        try:
            if os.path.getsize(p) > 1_500_000: skipped.append(p); continue
            raw = open(p, "rb").read()
            if b"\0" in raw[:2000]: skipped.append(p + " (binary)"); continue
            txt = raw.decode("utf-8", "ignore")
        except OSError: skipped.append(p); continue
        n += 1
        for i, line in enumerate(txt.splitlines(), 1):
            for sev, rx, why in RULES:
                if re.search(rx, line, re.I): found.append((sev, os.path.relpath(p, root), i, why, line.strip()[:110]))
order = {"High": 0, "Medium": 1, "Low": 2}
for sev, f, i, why, snip in sorted(found, key=lambda x: (order[x[0]], x[1], x[2])): print(f"[{sev}] {f}:{i}  {why}\n        {snip}")
hi = sum(1 for x in found if x[0] == "High"); me = sum(1 for x in found if x[0] == "Medium")
print(f"\nscanned {n} files, skipped {len(skipped)}; High {hi}, Medium {me}, Low {len(found) - hi - me}")
for s in skipped: print("not reviewed:", s)
print("verdict:", "DO NOT INSTALL before review" if hi else "REVIEW NEEDED" if me else "no obvious red flags (still read the instructions)")
