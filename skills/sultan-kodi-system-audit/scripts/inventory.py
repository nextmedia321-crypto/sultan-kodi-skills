#!/usr/bin/env python3
"""Inventory of a project's surfaces, to seed an audit coverage ledger. Read-only.
Usage: inventory.py [path] [--ledger out.tsv]
Prints counts and file:line samples for routes, API endpoints, UI interactive elements,
env variables, data models, dependencies, tests and risk markers. Static only: it cannot
see generated code, external services or runtime behavior."""
import os, re, sys, json, collections

args = [a for a in sys.argv[1:] if not a.startswith("--")]
ledger_out = sys.argv[sys.argv.index("--ledger") + 1] if "--ledger" in sys.argv else None
if ledger_out and ledger_out in args: args.remove(ledger_out)
root = os.path.abspath(args[0] if args else ".")
SKIP = {".git", "node_modules", ".next", "dist", "build", "__pycache__", ".venv", "venv", "vendor", ".turbo", "coverage", ".cache", ".idea", ".vscode"}
CODE = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".rb", ".go", ".php", ".java", ".kt", ".swift", ".vue", ".svelte", ".html", ".sql", ".prisma", ".graphql", ".yml", ".yaml", ".json", ".toml", ".env", ".sh")

P = {
 "api_endpoint": [r"\b(?:app|router|api)\.(get|post|put|patch|delete|all|use)\(\s*['\"`]([^'\"`]+)", r"@(?:app|router|bp|api)\.(get|post|put|patch|delete|route)\(\s*['\"]([^'\"]+)",
                  r"export\s+(?:async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE)\b", r"\.(?:HandleFunc|Handle)\(\s*\"([^\"]+)", r"\b(?:Route::|get|post)\s+['\"]/([^'\"]*)"],
 "ui_button": [r"<button\b", r"<Button\b", r"role=[\"']button", r"type=[\"']submit"],
 "ui_link": [r"<a\s[^>]*href", r"<Link\b", r"router\.push\(", r"navigate\("],
 "ui_form_field": [r"<form\b", r"<input\b", r"<select\b", r"<textarea\b", r"<Input\b", r"<TextField\b"],
 "ui_handler": [r"\bon(?:Click|Submit|Change|Press|KeyDown|Drop|Toggle)\s*=", r"addEventListener\(\s*['\"](?:click|submit|keydown|change)", r"\(click\)=|@click|v-on:click"],
 "env_var": [r"process\.env\.([A-Z0-9_]+)", r"os\.environ(?:\.get)?\(?\[?['\"]([A-Z0-9_]+)", r"import\.meta\.env\.([A-Z0-9_]+)", r"getenv\(['\"]([A-Z0-9_]+)"],
 "data_model": [r"CREATE\s+TABLE\s+(?:IF NOT EXISTS\s+)?[\"`]?([\w\.]+)", r"^model\s+(\w+)\s*\{", r"class\s+(\w+)\((?:models\.Model|db\.Model|Base)\)", r"\b(?:mongoose\.)?model\(\s*['\"](\w+)", r"pgTable\(\s*['\"](\w+)"],
 "background_job": [r"\bcron\b|setInterval\(|schedule\.|@scheduled|celery|bullmq|queue\.add\(|node-cron"],
 "webhook_or_integration": [r"webhook", r"stripe|twilio|sendgrid|mailgun|openai|anthropic|supabase|firebase|aws-sdk|s3\.|paypal|slack"],
 "auth": [r"jwt|jsonwebtoken|passport|next-auth|bcrypt|argon2|session|oauth|login|signup|resetPassword|isAdmin|role\s*[=!]=="],
 "todo_marker": [r"\b(TODO|FIXME|HACK|XXX)\b"],
 "debug_leftover": [r"console\.log\(|debugger;|print\(\s*['\"]DEBUG|var_dump\("],
 "risky_call": [r"\beval\(|dangerouslySetInnerHTML|innerHTML\s*=|exec\(|child_process|shell=True|verify\s*=\s*False|rejectUnauthorized\s*:\s*false|Access-Control-Allow-Origin['\"]?\s*[:,]\s*['\"]\*"],
 "possible_secret": [r"(?i)(api[_-]?key|secret|token|passw(?:or)?d)\s*[:=]\s*['\"][A-Za-z0-9_\-/+=]{12,}['\"]", r"AKIA[0-9A-Z]{16}", r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----", r"sk_live_[0-9a-zA-Z]+"],
 "test_case": [r"\b(?:it|test)\(\s*['\"`]", r"\bdef\s+test_\w+", r"func\s+Test\w+"],
}
RX = {k: [re.compile(p, re.M) for p in v] for k, v in P.items()}
found = collections.defaultdict(list)
files = []; route_files = []
for d, dirs, fs in os.walk(root):
    dirs[:] = [x for x in dirs if x not in SKIP]
    for f in fs:
        p = os.path.join(d, f); rel = os.path.relpath(p, root); files.append(rel)
        low = rel.lower().replace("\\", "/")
        if re.search(r"(^|/)(app|pages)/.*(page|route|layout)?\.(tsx|jsx|ts|js|vue|svelte)$", low) and re.search(r"(page|route|index|\[)", os.path.basename(low)):
            route_files.append(rel)
        if not f.endswith(CODE) and f not in (".env.example", "Dockerfile", "Makefile"): continue
        if os.path.getsize(p) > 800_000: continue
        try: txt = open(p, encoding="utf-8", errors="ignore").read()
        except OSError: continue
        is_test = bool(re.search(r"(test|spec)\.|__tests__|/tests?/", low))
        for kind, rxs in RX.items():
            if kind in ("ui_button", "ui_link", "ui_form_field", "ui_handler") and not f.endswith((".tsx", ".jsx", ".html", ".vue", ".svelte", ".js", ".ts", ".php")): continue
            if kind == "test_case" and not is_test: continue
            if kind in ("todo_marker", "debug_leftover", "risky_call", "possible_secret") and is_test and kind != "possible_secret": continue
            for rx in rxs:
                for m in rx.finditer(txt):
                    line = txt.count("\n", 0, m.start()) + 1
                    label = next((g for g in reversed(m.groups()) if g), m.group(0)[:40]) if m.groups() else m.group(0)[:40]
                    label = label.strip()
                    if label in ("GET", "POST", "PUT", "PATCH", "DELETE"): label = f"{label} {rel}"
                    found[kind].append((rel, line, label))

def show(kind, title, n=8, unique=False):
    items = found.get(kind, [])
    print(f"\n== {title}: {len(items)}")
    seen = set(); c = 0
    for rel, line, label in items:
        key = label if unique else (rel, line)
        if key in seen: continue
        seen.add(key); c += 1
        if c <= n: print(f"   {rel}:{line}  {label}")
    if unique and len(seen) > n: print(f"   ... {len(seen)} unique")

print(f"# Inventory of {root}\nfiles: {len(files)}")
ext = collections.Counter(os.path.splitext(f)[1] or f for f in files)
print("types:", ", ".join(f"{k} {v}" for k, v in ext.most_common(8)))
print("\n== hygiene")
for name, why in [("README.md", "how to run"), (".gitignore", "keeps secrets out"), (".env.example", "documents env vars"), ("LICENSE", "license"), ("Dockerfile", "container build"), (".github/workflows", "CI"), ("CHANGELOG.md", "history")]:
    print(f"   {'present' if os.path.exists(os.path.join(root, name)) else 'MISSING'}  {name}  ({why})")
if os.path.exists(os.path.join(root, ".env")): print("   NOTE  .env exists: make sure it is ignored by git and never printed")
pj = os.path.join(root, "package.json")
if os.path.exists(pj):
    try:
        j = json.load(open(pj)); print("\n== package.json\n   scripts:", ", ".join(j.get("scripts", {})) or "none"); print("   dependencies:", len(j.get("dependencies", {})), " dev:", len(j.get("devDependencies", {})))
        if "test" not in j.get("scripts", {}): print("   NOTE  no test script")
    except Exception: print("   package.json unreadable")
print(f"\n== page and route files: {len(route_files)}")
for r in route_files[:12]: print("  ", r)
show("api_endpoint", "API endpoints", 14)
for k, t in [("ui_button", "buttons"), ("ui_link", "links"), ("ui_form_field", "forms and fields"), ("ui_handler", "event handlers")]: show(k, t, 5)
show("env_var", "environment variables used", 20, unique=True)
show("data_model", "data models / tables", 15, unique=True)
show("background_job", "background jobs / schedulers", 6); show("webhook_or_integration", "webhooks and third-party integrations", 6, unique=True); show("auth", "auth-related code", 5)
tests = len(found.get("test_case", [])); print(f"\n== test cases found: {tests}")
show("possible_secret", "POSSIBLE SECRETS (mask values in reports)", 10); show("risky_call", "risky calls", 10); show("todo_marker", "TODO/FIXME markers", 6); show("debug_leftover", "debug leftovers", 5)

if ledger_out:
    rows = [("id", "surface", "type", "where", "status", "evidence_or_reason", "findings")]; i = 1
    for r in route_files: rows.append((f"R{i}", r, "route/page", r, "unchecked", "", "")); i += 1
    for kind in ("api_endpoint", "data_model", "env_var", "background_job", "webhook_or_integration"):
        seen = set()
        for rel, line, label in found.get(kind, []):
            if (kind, label) in seen: continue
            seen.add((kind, label)); rows.append((f"R{i}", label, kind, f"{rel}:{line}", "unchecked", "", "")); i += 1
    byfile = collections.Counter(rel for rel, _, _ in found.get("ui_button", []) + found.get("ui_form_field", []) + found.get("ui_handler", []))
    for rel, n in byfile.most_common(): rows.append((f"R{i}", f"{n} interactive elements in {rel}", "ui", rel, "unchecked", "", "")); i += 1
    for area in ("build and deploy pipeline", "authentication flows", "error and empty states", "accessibility", "responsiveness", "performance", "security headers", "dependencies", "backups and recovery", "logging and monitoring", "tests", "documentation", "legal and privacy pages"):
        rows.append((f"R{i}", area, "cross-cutting", "-", "unchecked", "", "")); i += 1
    os.makedirs(os.path.dirname(os.path.abspath(ledger_out)), exist_ok=True)
    with open(ledger_out, "w", encoding="utf-8") as fh:
        fh.write("\n".join("\t".join(r) for r in rows) + "\n")
    print(f"\nledger seed written: {ledger_out} ({len(rows) - 1} rows). Add what this static scan cannot see.")
