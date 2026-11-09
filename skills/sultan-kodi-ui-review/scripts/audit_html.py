#!/usr/bin/env python3
"""Static accessibility audit of an HTML file, plus WCAG contrast.
Usage: audit_html.py page.html        |  audit_html.py --contrast "#777777" "#ffffff" """
import re, sys
from html.parser import HTMLParser

def lum(hexc):
    h = hexc.lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

class A(HTMLParser):
    def __init__(s):
        super().__init__(); s.issues = []; s.labels_for = set(); s.inputs = []; s.cur = None; s.text = ""; s.heads = []
    def handle_starttag(s, t, a):
        a = dict(a); line = s.getpos()[0]
        if t == "img" and "alt" not in a: s.issues.append(("High", line, "img without alt"))
        if t == "label" and a.get("for"): s.labels_for.add(a["for"])
        if t in ("input", "select", "textarea") and a.get("type") not in ("hidden", "submit", "button"):
            s.inputs.append((line, a))
        if t in ("button", "a"): s.cur = (t, line, a); s.text = ""
        if t == "a" and a.get("href", "").startswith("javascript:"): s.issues.append(("Medium", line, "javascript: link"))
        if t in ("h1", "h2", "h3", "h4", "h5", "h6"): s.heads.append((int(t[1]), line))
        if "tabindex" in a and a["tabindex"].lstrip("-").isdigit() and int(a["tabindex"]) > 0:
            s.issues.append(("Low", line, "positive tabindex disrupts focus order"))
        if t == "div" and "onclick" in a and "role" not in a: s.issues.append(("Medium", line, "clickable div without role/keyboard support"))
    def handle_data(s, d):
        if s.cur: s.text += d
    def handle_endtag(s, t):
        if s.cur and t == s.cur[0]:
            _, line, a = s.cur
            if not (s.text.strip() or a.get("aria-label") or a.get("title")):
                s.issues.append(("High", line, f"<{t}> has no accessible name"))
            s.cur = None

if len(sys.argv) >= 4 and sys.argv[1] == "--contrast":
    r = ratio(sys.argv[2], sys.argv[3])
    print(f"ratio {r:.2f}:1  normal text AA {'PASS' if r >= 4.5 else 'FAIL'}  large text AA {'PASS' if r >= 3 else 'FAIL'}  AAA {'PASS' if r >= 7 else 'FAIL'}")
    sys.exit()
if len(sys.argv) < 2: sys.exit(__doc__)
a = A(); a.feed(open(sys.argv[1], encoding="utf-8", errors="ignore").read())
for line, at in a.inputs:
    if at.get("id") not in a.labels_for and not at.get("aria-label") and not at.get("aria-labelledby"):
        a.issues.append(("High", line, f"form field without label ({at.get('name') or at.get('type') or 'input'})"))
prev = 0
for lvl, line in a.heads:
    if prev and lvl > prev + 1: a.issues.append(("Low", line, f"heading level jumps h{prev} -> h{lvl}"))
    prev = lvl
order = {"High": 0, "Medium": 1, "Low": 2}
for sev, line, msg in sorted(a.issues, key=lambda x: (order[x[0]], x[1])): print(f"[{sev}] line {line}: {msg}")
print(f"{len(a.issues)} issue(s)")
