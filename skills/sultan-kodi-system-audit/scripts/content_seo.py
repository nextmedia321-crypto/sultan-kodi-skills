#!/usr/bin/env python3
"""Content, SEO and language check for HTML pages: a folder of built/static HTML, or a URL (same-origin crawl).
Usage: content_seo.py <folder|url> [--max-pages 30]
Checks per page: title and length, meta description, h1 count, lang and dir attributes, Hebrew/Arabic text without dir=rtl,
images without alt, canonical, Open Graph, viewport, broken internal links (URL mode and folder mode), duplicate titles."""
import os, re, sys, urllib.request, urllib.error, urllib.parse, collections
a = sys.argv[1:]
if not a: sys.exit(__doc__)
tgt = a[0]; mx = int(a[a.index("--max-pages") + 1]) if "--max-pages" in a else 30
pages = {}
def fetch(u):
    try:
        with urllib.request.urlopen(u, timeout=15) as r: return r.status, r.read(1500000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e: return e.code, ""
    except Exception: return 0, ""
if tgt.startswith("http"):
    origin = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(tgt)); q = [tgt]; seen = set()
    while q and len(pages) < mx:
        u = q.pop(0).split("#")[0]
        if u in seen: continue
        seen.add(u); c, h = fetch(u)
        if c != 200: pages[u] = (c, None); continue
        pages[u] = (c, h)
        for l in re.findall(r'href=["\']([^"\']+)', h):
            full = urllib.parse.urljoin(u, l).split("#")[0]
            if full.startswith(origin) and full not in seen and not re.search(r"\.(png|jpg|jpeg|svg|pdf|css|js|ico|webp|zip)(\?|$)", full): q.append(full)
else:
    for d, _, fs in os.walk(tgt):
        if "node_modules" in d: continue
        for f in fs:
            if f.endswith(".html") and len(pages) < mx:
                pages[os.path.join(d, f)] = (200, open(os.path.join(d, f), encoding="utf-8", errors="ignore").read())
issues = collections.defaultdict(list); titles = collections.defaultdict(list)
for u, (c, h) in pages.items():
    if h is None: issues["broken page or link"].append(f"{u} status {c}"); continue
    t = re.search(r"<title[^>]*>(.*?)</title>", h, re.S | re.I); t = re.sub(r"\s+", " ", t.group(1)).strip() if t else ""
    if not t: issues["missing title"].append(u)
    elif not 15 <= len(t) <= 65: issues["title length outside 15-65"].append(f"{u} ({len(t)})")
    titles[t].append(u)
    if not re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'][^"\']{50,}', h, re.I): issues["meta description missing or too short"].append(u)
    n1 = len(re.findall(r"<h1[\s>]", h, re.I))
    if n1 != 1: issues["h1 count not 1"].append(f"{u} ({n1})")
    if not re.search(r"<html[^>]+lang=", h, re.I): issues["html lang missing"].append(u)
    if re.search(r"[֐-׿؀-ۿ]{3,}", h) and not re.search(r'dir=["\']rtl|direction\s*:\s*rtl', h, re.I): issues["right-to-left text without dir=rtl"].append(u)
    noalt = len(re.findall(r"<img(?![^>]*\balt=)[^>]*>", h, re.I))
    if noalt: issues["images without alt"].append(f"{u} ({noalt})")
    if not re.search(r'<meta[^>]+name=["\']viewport', h, re.I): issues["viewport meta missing"].append(u)
    if not re.search(r'rel=["\']canonical', h, re.I): issues["canonical missing"].append(u)
    if not re.search(r'property=["\']og:title', h, re.I): issues["Open Graph tags missing"].append(u)
    if not tgt.startswith("http"):
        for l in re.findall(r'href=["\']([^"\'#]+)', h):
            if re.match(r"(https?:|mailto:|tel:|javascript:|//)", l): continue
            p = os.path.normpath(os.path.join(os.path.dirname(u), l.split("?")[0]))
            if not (os.path.exists(p) or os.path.exists(os.path.join(p, "index.html")) or os.path.exists(p + ".html")): issues["broken internal link"].append(f"{u} -> {l}")
for t, us in titles.items():
    if t and len(us) > 1: issues["duplicate title"].append(f"{t[:40]} on {len(us)} pages")
print(f"# Content and SEO check: {len(pages)} pages")
for k, v in issues.items():
    print(f"\n[{k}] {len(v)}"); [print("   ", x) for x in v[:5]]
print(f"\nISSUES: {sum(len(v) for v in issues.values())}"); sys.exit(1 if issues else 0)
