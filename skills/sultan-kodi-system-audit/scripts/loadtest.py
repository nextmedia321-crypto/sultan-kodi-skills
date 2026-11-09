#!/usr/bin/env python3
"""Light load test with the standard library. Local or staging only.
Usage: loadtest.py URL [--users 20] [--seconds 10] [--force]
Reports requests, errors, requests per second, p50/p95/max latency, and the first point where errors begin."""
import sys, time, threading, urllib.request, urllib.error, statistics
a = sys.argv[1:]
if not a: sys.exit(__doc__)
url = a[0]; opt = lambda n, d: type(d)(a[a.index(n) + 1]) if n in a else d
users, secs = opt("--users", 20), opt("--seconds", 10)
host = url.split("//")[-1].split("/")[0].split(":")[0]
if host not in ("localhost", "127.0.0.1", "[::1]") and not any(k in host for k in ("staging", "dev", "test", "qa", "sandbox")) and "--force" not in a: sys.exit(f"Refusing: {host} is not local or staging; confirm with the user then pass --force.")
if users > 200: sys.exit("Refusing more than 200 users from this light tool.")
lat, errs, first_err = [], [], [None]; lock = threading.Lock(); t0 = time.time(); stop = t0 + secs
def worker():
    while time.time() < stop:
        s = time.time()
        try:
            with urllib.request.urlopen(url, timeout=15) as r: r.read(1000); ok = r.status < 500
        except urllib.error.HTTPError as e: ok = e.code < 500
        except Exception: ok = False
        d = time.time() - s
        with lock:
            lat.append(d)
            if not ok:
                errs.append(d)
                if first_err[0] is None: first_err[0] = round(time.time() - t0, 1)
ts = [threading.Thread(target=worker) for _ in range(users)]; [t.start() for t in ts]; [t.join() for t in ts]
n = len(lat); el = time.time() - t0; ls = sorted(lat)
print(f"# Load test {url}: {users} users for {secs}s\nrequests {n}, errors {len(errs)} ({100 * len(errs) / max(n, 1):.1f}%), {n / el:.0f} req/s")
if n: print(f"latency p50 {statistics.median(ls) * 1000:.0f}ms  p95 {ls[int(n * .95) - 1] * 1000:.0f}ms  max {ls[-1] * 1000:.0f}ms")
if first_err[0] is not None: print(f"first error at {first_err[0]}s")
bad = len(errs) / max(n, 1) > 0.01 or (n and ls[int(n * .95) - 1] > 2)
print("RESULT:", "PROBLEM (errors over 1% or p95 over 2s)" if bad else "ok at this load"); sys.exit(1 if bad else 0)
