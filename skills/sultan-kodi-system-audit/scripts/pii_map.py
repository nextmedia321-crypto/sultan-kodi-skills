#!/usr/bin/env python3
"""Map where personal data lives and flows. Flags only, not legal advice.
Usage: pii_map.py [project]
Finds PII-like fields in schemas/models/forms, where they are logged or sent to third parties, missing deletion/export code,
missing retention hints, and missing privacy/consent pages."""
import os, re, sys, collections
root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
SKIP = {".git", "node_modules", ".next", "dist", "build", "venv", ".venv", "__pycache__", "vendor", ".audit"}
FIELD = re.compile(r"\b(email|e_mail|phone|mobile|tel|first_?name|last_?name|full_?name|address|street|zip|postal|birth|dob|passport|national_?id|id_?number|ssn|tax_?id|credit_?card|card_?number|iban|ip_?address|location|lat|lng|salary|gender)\b", re.I)
LOGCALL = re.compile(r"(console\.(?:log|error)|logger\.\w+|logging\.\w+|print|log\.\w+)\(([^)]*)", re.I)
SENDS = re.compile(r"(fetch|axios\.\w+|requests\.\w+|analytics\.\w+|track|posthog|mixpanel|segment|gtag|sentry|capture)\(", re.I)
fields = collections.defaultdict(set); logs = []; sends = []; has = {"delete": 0, "export": 0, "consent": 0, "retention": 0}
for d, dirs, fs in os.walk(root):
    dirs[:] = [x for x in dirs if x not in SKIP]
    for f in fs:
        if not f.endswith((".py", ".js", ".ts", ".tsx", ".jsx", ".sql", ".prisma", ".html", ".vue", ".php", ".rb", ".go", ".md", ".yml")): continue
        p = os.path.join(d, f); rel = os.path.relpath(p, root)
        try: t = open(p, encoding="utf-8", errors="ignore").read() if os.path.getsize(p) < 600000 else ""
        except OSError: continue
        schema = re.search(r"model|schema|migration|\.sql|\.prisma|models|entity", rel, re.I)
        for i, line in enumerate(t.split("\n"), 1):
            m = FIELD.findall(line)
            if m and (schema or re.search(r"<input|name=|type=|Column\(|field", line, re.I)):
                for x in m: fields[x.lower()].add(f"{rel}:{i}")
            lc = LOGCALL.search(line)
            if lc and FIELD.search(lc.group(2)): logs.append(f"{rel}:{i}")
            if SENDS.search(line) and FIELD.search(line): sends.append(f"{rel}:{i}")
        if re.search(r"delete.?(user|account)|erase|anonymi[sz]e|gdpr|forget", t, re.I): has["delete"] += 1
        if re.search(r"export.?(user|data|my)|data.?portability|download.?my", t, re.I): has["export"] += 1
        if re.search(r"consent|cookie.?banner|privacy.?policy|accept.?terms", t, re.I): has["consent"] += 1
        if re.search(r"retention|expire[sd]?_at|purge|ttl|delete.?after|cleanup.?job", t, re.I): has["retention"] += 1
print(f"# Personal-data map of {root}\n(flags for review, not legal advice)\n\n== PII-like fields: {len(fields)} kinds")
for k, v in sorted(fields.items()): print(f"   {k}: {len(v)} places, e.g. {sorted(v)[0]}")
print(f"\n== PII near log calls: {len(logs)}"); [print("  ", x) for x in logs[:8]]
print(f"\n== PII near outbound or analytics calls: {len(sends)}"); [print("  ", x) for x in sends[:8]]
print("\n== Handling code present (files mentioning it)")
for k, v in has.items(): print(f"   {k}: {'found in ' + str(v) + ' files' if v else 'NOT FOUND'}")
issues = []
if fields and not has["delete"]: issues.append("personal data is stored but no deletion/erasure path was found")
if fields and not has["consent"]: issues.append("personal data is collected but no consent or privacy text was found")
if fields and not has["retention"]: issues.append("no retention or cleanup logic found")
if logs: issues.append("personal data may be written to logs")
print("\nFLAGS:", "; ".join(issues) or "none"); sys.exit(1 if issues else 0)
