#!/usr/bin/env python3
"""Find likely cost hot spots: paid API or AI calls inside loops or request handlers, missing caching, unbounded queries, polling.
Usage: cost_scan.py [project] [--calls-per-month N]
The money figure is a rough range from public list prices that you must verify; the structural findings are the real value."""
import os, re, sys, collections
a = sys.argv[1:]; root = os.path.abspath(a[0] if a and not a[0].startswith("--") else "."); cpm = int(a[a.index("--calls-per-month") + 1]) if "--calls-per-month" in a else 10000
SKIP = {".git", "node_modules", ".next", "dist", "build", "venv", ".venv", "__pycache__", "vendor", ".audit"}
PAID = re.compile(r"(openai|anthropic|claude|gpt|gemini|messages\.create|chat\.completions|completions\.create|embeddings|twilio|sendgrid|mailgun|stripe\.|googleapis|maps\.googleapis|textract|rekognition|elevenlabs)", re.I)
LOOP = re.compile(r"\b(for|while|forEach|map|Promise\.all|asyncio\.gather)\b")
rows = collections.defaultdict(list)
for d, dirs, fs in os.walk(root):
    dirs[:] = [x for x in dirs if x not in SKIP]
    for f in fs:
        if not f.endswith((".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rb", ".php")): continue
        p = os.path.join(d, f); rel = os.path.relpath(p, root)
        try: lines = open(p, encoding="utf-8", errors="ignore").read().split("\n")
        except OSError: continue
        txt = "\n".join(lines); cached = bool(re.search(r"cache|lru_cache|memo|redis|etag|revalidate|stale", txt, re.I))
        for i, l in enumerate(lines):
            if PAID.search(l) and re.search(r"\(", l) and not l.strip().startswith(("import", "from", "//", "#", "const .* = require")):
                ctx = "\n".join(lines[max(0, i - 6):i + 1])
                kind = "paid call inside a loop" if LOOP.search(ctx) else "paid call"
                rows[kind].append(f"{rel}:{i + 1}")
                if not cached: rows["paid call in a file with no caching"].append(f"{rel}:{i + 1}")
                if re.search(r"max_tokens|maxTokens|max_output", "\n".join(lines[i:i + 8])) is None and re.search(r"openai|anthropic|claude|gpt|gemini|messages\.create|completions", l, re.I): rows["AI call without a max token limit"].append(f"{rel}:{i + 1}")
            if re.search(r"setInterval\(|while\s*\(?\s*(true|1)\b|sleep\(\s*[0-5]\s*\)", l) and re.search(r"fetch|request|query|select", "\n".join(lines[i:i + 8]), re.I): rows["polling loop"].append(f"{rel}:{i + 1}")
            if re.search(r"select\s+\*\s+from|\.find\(\s*\{?\s*\}?\s*\)|findMany\(\s*\)|\.all\(\)", l, re.I) and not re.search(r"limit|take|paginate|where", l, re.I): rows["unbounded query"].append(f"{rel}:{i + 1}")
print(f"# Cost hot spots in {root}")
for k, v in rows.items():
    print(f"\n[{k}] {len(v)}"); [print("   ", x) for x in sorted(set(v))[:6]]
ai = len(rows.get("AI call without a max token limit", []))
loops = len(rows.get("paid call inside a loop", []))
print(f"\nRough exposure at {cpm:,} requests per month (assumption, verify with the provider's current price list):")
print(f"  a typical small AI call (about 1k input and 500 output tokens) costs on the order of cents per 100 calls; a loop multiplies it by its length.")
print(f"  structural risks: {loops} paid calls in loops, {ai} AI calls with no output cap, {len(rows.get('polling loop', []))} polling loops")
sys.exit(1 if loops or ai else 0)
