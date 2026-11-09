#!/usr/bin/env python3
"""Build a self-contained HTML report from .audit/findings.json (and .audit/sweep/sweep.json if present).
Usage: report_html.py [--lang en|he] [--out .audit/report.html] [--title "..."]"""
import json, os, sys, html, time
a = sys.argv[1:]; opt = lambda n, d=None: a[a.index(n) + 1] if n in a else d
D = os.environ.get("AUDIT_DIR", os.path.join(os.getcwd(), ".audit")); F = os.path.join(D, "findings.json")
if not os.path.exists(F): sys.exit("No ledger at " + F)
s = json.load(open(F)); lang = opt("--lang", "en"); out = opt("--out", os.path.join(D, "report.html"))
T = {"en": dict(t="System audit report", sev="By severity", st="By status", f="Findings", id="ID", s="Severity", stt="Status", ti="Title", pr="Proof / reason", ev="Evidence", gate="Completion gate", passes="Re-audit passes", dirn="ltr", sw="Browser sweep", pg="Pages visited", iss="Issues found", g="Gate passed", ng="Gate not passed"),
     "he": dict(t="דוח בדיקת מערכת", sev="לפי חומרה", st="לפי סטטוס", f="ממצאים", id="מזהה", s="חומרה", stt="סטטוס", ti="כותרת", pr="הוכחה / סיבה", ev="ראיה", gate="שער סיום", passes="סבבי בדיקה חוזרת", dirn="rtl", sw="סריקת דפדפן", pg="דפים שנסרקו", iss="בעיות שנמצאו", g="השער עבר", ng="השער לא עבר")}[lang]
title = opt("--title", T["t"]); F_ = s["findings"]; e = html.escape
sev = ["Critical", "High", "Medium", "Low"]; col = {"Critical": "#b3261e", "High": "#d9622b", "Medium": "#c99a06", "Low": "#5b7f95"}
stc = {"fixed": "#2e7d32", "open": "#b3261e", "in_progress": "#c99a06", "blocked": "#6a5acd", "wontfix": "#777"}
def bars(counts, colors):
    m = max(counts.values() or [1]) or 1
    return "".join(f'<div class="row"><span class="lab">{e(k)}</span><span class="bar"><i style="width:{100 * v / m:.0f}%;background:{colors.get(k, "#888")}"></i></span><b>{v}</b></div>' for k, v in counts.items())
cs = {k: sum(x["sev"] == k for x in F_) for k in sev}; ct = {}
for x in F_: ct[x["status"]] = ct.get(x["status"], 0) + 1
open_ = [x for x in F_ if x["status"] in ("open", "in_progress")]; passes = s["passes"]
ok = not open_ and len(passes) >= 2 and all(p["new"] == 0 for p in passes[-2:])
rows = "".join(f'<tr><td>{e(x["id"])}</td><td><span class="pill" style="background:{col[x["sev"]]}">{e(x["sev"])}</span></td><td><span class="pill" style="background:{stc.get(x["status"], "#888")}">{e(x["status"])}</span></td><td>{e(x["title"])}<div class="ev">{e(T["ev"])}: {e(x["evidence"])}</div></td><td>{e((x["proof"] or x["reason"] or "-")[:160])}</td></tr>' for x in sorted(F_, key=lambda x: (sev.index(x["sev"]), x["id"])))
sw = ""; sp = os.path.join(D, "sweep", "sweep.json")
if os.path.exists(sp):
    j = json.load(open(sp)); sw = f'<h2>{e(T["sw"])}</h2><p>{e(T["pg"])}: {len(j["pages"])} · {e(T["iss"])}: {len(j["issues"])}</p><ul>' + "".join(f'<li><b>{e(i["type"])}</b> {e(i["where"])} — {e(i["detail"][:120])}</li>' for i in j["issues"][:25]) + "</ul>"
doc = f'''<!doctype html><html lang="{lang}" dir="{T["dirn"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title>
<style>:root{{--bg:#fafaf7;--fg:#1d1d1b;--card:#fff;--line:#e4e2da}}@media(prefers-color-scheme:dark){{:root{{--bg:#16161a;--fg:#ececec;--card:#202026;--line:#34343c}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,Arial,sans-serif;padding:16px}}main{{max-width:980px;margin:auto}}h1{{font-size:24px}}h2{{margin-top:28px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin:12px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}}
.row{{display:flex;align-items:center;gap:8px;margin:5px 0}}.lab{{width:90px}}.bar{{flex:1;background:var(--line);border-radius:5px;height:12px;overflow:hidden}}.bar i{{display:block;height:100%}}
table{{width:100%;border-collapse:collapse;background:var(--card)}}td,th{{border-bottom:1px solid var(--line);padding:8px;text-align:start;vertical-align:top}}.pill{{color:#fff;border-radius:99px;padding:1px 9px;font-size:12px}}.ev{{font-size:12px;opacity:.7}}
.gate{{padding:10px 14px;border-radius:8px;color:#fff;background:{"#2e7d32" if ok else "#b3261e"}}}@media(max-width:640px){{td,th{{font-size:13px;padding:6px}}}}</style></head><body><main>
<h1>{e(title)}</h1><p>{time.strftime("%Y-%m-%d %H:%M")}</p><div class="gate">{e(T["gate"])}: {e(T["g"] if ok else T["ng"])} · {e(T["passes"])}: {len(passes)}</div>
<div class="grid"><div class="card"><h3>{e(T["sev"])}</h3>{bars(cs, col)}</div><div class="card"><h3>{e(T["st"])}</h3>{bars(ct, stc)}</div></div>
<h2>{e(T["f"])} ({len(F_)})</h2><div style="overflow-x:auto"><table><tr><th>{e(T["id"])}</th><th>{e(T["s"])}</th><th>{e(T["stt"])}</th><th>{e(T["ti"])}</th><th>{e(T["pr"])}</th></tr>{rows}</table></div>{sw}</main></body></html>'''
open(out, "w", encoding="utf-8").write(doc); print("wrote", out)
