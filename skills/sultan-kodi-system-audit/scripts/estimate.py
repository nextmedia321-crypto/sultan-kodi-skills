#!/usr/bin/env python3
"""Rough size and usage estimate BEFORE an audit, so the user can choose a mode. It is an estimate, not a measurement.
Usage: estimate.py [project]"""
import os, sys
root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
SKIP = {".git", "node_modules", ".next", "dist", "build", "venv", ".venv", "__pycache__", "vendor", ".audit"}
CODE = (".js", ".jsx", ".ts", ".tsx", ".py", ".rb", ".go", ".php", ".java", ".kt", ".swift", ".vue", ".svelte", ".html", ".css", ".sql", ".prisma", ".yml", ".yaml", ".md")
files = 0; chars = 0
for d, dirs, fs in os.walk(root):
    dirs[:] = [x for x in dirs if x not in SKIP]
    for f in fs:
        if f.endswith(CODE):
            try: chars += os.path.getsize(os.path.join(d, f)); files += 1
            except OSError: pass
tok = chars // 4
print(f"# Estimate for {root}\ncode and text files: {files}, about {tok:,} tokens if everything were read once")
for name, mult, note in [("quick (critical only, read-only)", 0.6, "entry points, auth, data, scripts"), ("check only (full coverage, no fixes)", 2.0, "every row examined, scripts run"), ("check and fix", 6.0, "adds fix loop, re-audit twice"), ("full (fix, browser sweep, verifier, report)", 9.0, "everything")]:
    lo = int(tok * mult * 0.6); hi = int(tok * mult * 1.6)
    print(f"  {name}: roughly {lo:,} to {hi:,} tokens  ({note})")
print("\nHonest caveat: real usage depends on how many defects are found and how many fix attempts fail. Large systems are audited module by module with one ledger; say which modules to do first.")
