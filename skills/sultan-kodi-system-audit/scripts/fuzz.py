#!/usr/bin/env python3
"""Send hostile input to endpoints of a RUNNING local or staging app and look for crashes and leaks.
Usage: fuzz.py config.json
{"base":"http://localhost:3000","token_env":"TOKEN_ENV_NAME (optional)",
 "targets":[{"method":"POST","path":"/api/items","fields":{"name":"x","qty":1}},{"method":"GET","path":"/api/search","query":{"q":"x"}}]}
Reports: 5xx responses, stack traces or SQL errors in the body, reflected payloads, and slow responses. Local/staging only."""
import json, os, sys, time, urllib.request, urllib.error, urllib.parse
if len(sys.argv) < 2: sys.exit(__doc__)
cfg = json.load(open(sys.argv[1])); base = cfg["base"].rstrip("/"); host = base.split("//")[-1].split("/")[0].split(":")[0]
if host not in ("localhost", "127.0.0.1", "[::1]") and not any(k in host for k in ("staging", "dev", "test", "qa", "sandbox")) and "--force" not in sys.argv: sys.exit(f"Refusing: {host} is not local or staging.")
tok = os.environ.get(cfg.get("token_env", "")) if cfg.get("token_env") else None
PAY = ["", " ", "A" * 20000, "-1", "0", "99999999999999999999", "null", "undefined", "[]", "{}", "' OR '1'='1", "\"; DROP TABLE x;--", "<script>alert(1)</script>", "../../../etc/passwd", "%00", "${7*7}", "{{7*7}}", "אבגד‮", "😀" * 50, "\\u0000"]
LEAK = ["Traceback (most recent call last)", "at Object.", "SQLSTATE", "syntax error at or near", "SequelizeDatabaseError", "node_modules", "/home/", "/usr/lib/", "ECONNREFUSED", "stack trace"]
finds = []
def send(m, path, q, body):
    url = base + path + (("?" + urllib.parse.urlencode(q)) if q else "")
    h = {"Content-Type": "application/json"}
    if tok: h["Authorization"] = "Bearer " + tok
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, method=m, headers=h); t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=15) as r: return r.status, r.read(4000).decode("utf-8", "ignore"), time.time() - t
    except urllib.error.HTTPError as e: return e.code, e.read(4000).decode("utf-8", "ignore"), time.time() - t
    except Exception as e: return "ERR", str(e), time.time() - t
n = 0
for t in cfg["targets"]:
    m = t.get("method", "GET").upper(); data = t.get("fields") or t.get("query") or {}
    if m not in ("GET", "HEAD") and not t.get("allow_write", True): continue
    for k in data:
        for p in PAY:
            d = dict(data); d[k] = p; n += 1
            code, body, dt = send(m, t["path"], d if m == "GET" else None, d if m != "GET" else None)
            tag = f'{m} {t["path"]} field={k} payload={p[:25]!r}'
            if code == "ERR": finds.append(("connection failure", tag, body[:80]))
            elif isinstance(code, int) and code >= 500: finds.append(("5xx", tag, f"status {code}"))
            if any(x in body for x in LEAK): finds.append(("internal detail leaked", tag, next(x for x in LEAK if x in body)))
            if p.startswith("<script") and p in body: finds.append(("payload reflected unescaped", tag, "XSS candidate"))
            if p == "{{7*7}}" and "49" in body and "{{7*7}}" not in body: finds.append(("template injection?", tag, "7*7 evaluated"))
            if dt > 5: finds.append(("slow response", tag, f"{dt:.1f}s"))
print(f"# Fuzz run: {n} requests"); seen = set()
for kind, tag, d in finds:
    if (kind, tag) in seen: continue
    seen.add((kind, tag)); print(f"[{kind}] {tag}  {d}")
print(f"FINDINGS: {len(seen)}"); sys.exit(1 if seen else 0)
