#!/usr/bin/env python3
"""Role and permission matrix plus IDOR test against a RUNNING test/staging instance.
Usage: authz_matrix.py config.json
Config:
{ "base": "http://localhost:3000",
  "roles": {"anon": null, "user_a": "TOKEN_A_ENV", "user_b": "TOKEN_B_ENV", "admin": "ADMIN_ENV"},   # value = NAME of an env var holding the bearer token
  "tests": [ {"name":"list users","method":"GET","path":"/api/users","expect":{"anon":401,"user_a":403,"admin":200}},
             {"name":"read own order","method":"GET","path":"/api/orders/1","owner":"user_a","expect":{"user_a":200,"user_b":403,"anon":401}} ] }
Tokens are read from env vars, never from the file. Only run against local, staging or test data. GET/HEAD by default;
other methods run only when the test sets "allow_write": true."""
import json, os, sys, urllib.request, urllib.error
if len(sys.argv) < 2: sys.exit(__doc__)
cfg = json.load(open(sys.argv[1])); base = cfg["base"].rstrip("/")
host = base.split("//")[-1].split("/")[0].split(":")[0]
if host not in ("localhost", "127.0.0.1", "[::1]") and not any(k in host for k in ("staging", "dev", "test", "qa", "sandbox")) and "--force" not in sys.argv:
    sys.exit(f"Refusing: {host} does not look like local or staging. Confirm with the user, then pass --force.")
def call(method, path, token):
    h = {"Accept": "application/json"}
    if token: h["Authorization"] = "Bearer " + token
    req = urllib.request.Request(base + path, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=15) as r: return r.status
    except urllib.error.HTTPError as e: return e.code
    except Exception as e: return "ERR " + str(e)[:40]
roles = {}
for r, env in cfg["roles"].items():
    if env and not os.environ.get(env): print(f"note: env {env} for role {r} is empty; that role is skipped"); continue
    roles[r] = os.environ.get(env) if env else None
bad = 0; rows = []
for t in cfg["tests"]:
    m = t.get("method", "GET").upper()
    if m not in ("GET", "HEAD") and not t.get("allow_write"): rows.append((t["name"], "SKIPPED (write method, no allow_write)")); continue
    res = []
    for role, exp in t["expect"].items():
        if role not in roles: continue
        got = call(m, t["path"], roles[role]); ok = (got == exp) if isinstance(exp, int) else (got in exp)
        res.append(f"{role}={got}" + ("" if ok else f" (EXPECTED {exp})")); bad += 0 if ok else 1
    rows.append((t["name"], " | ".join(res)))
print("# Authorization matrix\n")
for n, r in rows: print(f"- {n}: {r}")
print(f"\nMISMATCHES: {bad}" + ("  <- each is a finding (a 200 where 401/403 was expected is an access-control hole; for owner tests it is an IDOR)" if bad else ""))
sys.exit(1 if bad else 0)
