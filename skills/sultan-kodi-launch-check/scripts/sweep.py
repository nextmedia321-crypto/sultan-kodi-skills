#!/usr/bin/env python3
"""Read-only pre-launch sweep. Usage: sweep.py https://example.com [max_links]"""
import re, sys, ssl, urllib.request, urllib.parse
from html.parser import HTMLParser

UA = {"User-Agent": "launch-check/1.0 (read-only audit)"}

def get(url, method="GET", timeout=15):
    req = urllib.request.Request(url, headers=UA, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as r:
            return r.status, dict(r.headers), r.read(400000) if method == "GET" else b""
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), b""
    except Exception as e:
        return 0, {}, str(e).encode()

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.title = ""; s.in_t = False; s.meta = {}; s.links = []; s.h1 = 0
        s.imgs_no_alt = 0; s.lang = ""; s.canon = ""
    def handle_starttag(s, t, a):
        a = dict(a)
        if t == "html": s.lang = a.get("lang", "")
        if t == "title": s.in_t = True
        if t == "h1": s.h1 += 1
        if t == "meta" and a.get("name"): s.meta[a["name"].lower()] = a.get("content", "")
        if t == "link" and a.get("rel") == "canonical": s.canon = a.get("href", "")
        if t == "a" and a.get("href"): s.links.append(a["href"])
        if t == "img" and "alt" not in a: s.imgs_no_alt += 1
    def handle_endtag(s, t):
        if t == "title": s.in_t = False
    def handle_data(s, d):
        if s.in_t: s.title += d

def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    url = sys.argv[1]; maxl = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    out = []
    def add(sev, msg): out.append((sev, msg))
    st, h, body = get(url)
    if st == 0: sys.exit(f"UNREACHABLE: {body.decode(errors='ignore')}")
    h = {k.lower(): v for k, v in h.items()}
    if not url.startswith("https"): add("High", "Site is not served over HTTPS")
    else:
        import http.client
        try:
            c = http.client.HTTPConnection(urllib.parse.urlparse(url).netloc, timeout=15)
            c.request("HEAD", "/", headers=UA); r = c.getresponse()
            loc = r.getheader("Location") or ""
            if not (300 <= r.status < 400 and loc.startswith("https")): add("Medium", "HTTP does not redirect to HTTPS")
        except Exception:
            pass  # port 80 closed: nothing to redirect
    for k, sev in [("strict-transport-security", "Medium"), ("content-security-policy", "Medium"),
                   ("x-content-type-options", "Low"), ("referrer-policy", "Low")]:
        if k not in h: add(sev, f"Missing header: {k}")
    if "x-frame-options" not in h and "frame-ancestors" not in h.get("content-security-policy", ""):
        add("Low", "No clickjacking protection (x-frame-options or frame-ancestors)")
    p = P(); p.feed(body.decode(errors="ignore"))
    if not p.title.strip(): add("Medium", "Missing <title>")
    if "description" not in p.meta: add("Medium", "Missing meta description")
    if "viewport" not in p.meta: add("High", "Missing viewport meta (mobile layout)")
    if not p.lang: add("Low", "<html> has no lang attribute (accessibility, SEO)")
    if p.h1 != 1: add("Low", f"Expected one <h1>, found {p.h1}")
    if p.imgs_no_alt: add("Medium", f"{p.imgs_no_alt} image(s) without alt attribute")
    base = f"{urllib.parse.urlparse(url).scheme}://{urllib.parse.urlparse(url).netloc}"
    for path in ("/robots.txt", "/sitemap.xml"):
        if get(base + path, "HEAD")[0] != 200: add("Low", f"{path} not found")
    seen, bad = set(), []
    for l in p.links:
        full = urllib.parse.urljoin(url, l.split("#")[0])
        if not full.startswith("http") or full in seen: continue
        seen.add(full)
        if len(seen) > maxl: break
        c = get(full, "HEAD")[0]
        if c in (0, 404, 410) or c >= 500: bad.append(f"{full} -> {c}")
    for b in bad: add("High", f"Broken link: {b}")
    add("Info", f"Checked {min(len(seen), maxl)} links; status of page: {st}")
    order = {"High": 0, "Medium": 1, "Low": 2, "Info": 3}
    for sev, msg in sorted(out, key=lambda x: order[x[0]]): print(f"[{sev}] {msg}")

main()
