#!/usr/bin/env python3
"""Email deliverability and template check.
Usage: email_check.py --domain example.com [--dkim-selector google,default,selector1]   DNS records via dig/nslookup if available
       email_check.py --templates <folder>                                               static check of email templates
DNS needs network access; if it is blocked the result says so and nothing is claimed."""
import subprocess, shutil, sys, re, os
a = sys.argv[1:]; opt = lambda n: a[a.index(n) + 1] if n in a and a.index(n) + 1 < len(a) else None
def udp_txt(name, server="1.1.1.1"):
    import socket, struct, random
    q = struct.pack(">HHHHHH", random.randint(0, 65535), 0x0100, 1, 0, 0, 0) + b"".join(bytes([len(p)]) + p.encode() for p in name.split(".")) + b"\x00" + struct.pack(">HH", 16, 1)
    so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); so.settimeout(4)
    try: so.sendto(q, (server, 53)); d = so.recvfrom(4096)[0]
    except Exception: return None
    if d[3] & 15: return None  # NXDOMAIN/SERVFAIL: do not treat as "record missing"
    an = struct.unpack(">H", d[6:8])[0]; i = 12
    while d[i]: i += d[i] + 1
    i += 5; out = []
    for _ in range(an):
        while d[i] and d[i] < 192: i += d[i] + 1
        i += 2 if d[i] >= 192 else 1
        t, _, _, ln = struct.unpack(">HHIH", d[i:i + 10]); i += 10; rd = d[i:i + ln]; i += ln
        if t == 16:
            j = 0; s = b""
            while j < len(rd): n = rd[j]; s += rd[j + 1:j + 1 + n]; j += 1 + n
            out.append(s.decode("utf-8", "ignore"))
    return "\n".join(out)
def txt(name):
    if not shutil.which("dig") and not shutil.which("nslookup"):
        r = udp_txt(name)
        return (r, "") if r is not None else (None, "no dig/nslookup and direct DNS query failed (network blocked?)")
    if shutil.which("dig"): cmd = ["dig", "+short", "TXT", name]
    elif shutil.which("nslookup"): cmd = ["nslookup", "-type=TXT", name]
    else: return None, "no dig or nslookup installed"
    try: r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    except Exception as e: return None, str(e)
    if r.returncode or "timed out" in r.stdout + r.stderr or "no servers" in (r.stdout + r.stderr).lower(): return None, "DNS lookup blocked or failed here"
    return r.stdout, ""
bad = 0; unchecked = 0
if opt("--domain"):
    d = opt("--domain"); print(f"# Email DNS check for {d}")
    for label, name, must in (("SPF", d, "v=spf1"), ("DMARC", "_dmarc." + d, "v=DMARC1")):
        out, err = txt(name)
        if out is None: print(f"{label}: NOT CHECKED ({err})"); unchecked += 1; continue
        rec = [l for l in out.split("\n") if must in l]
        if not rec: print(f"{label}: MISSING"); bad += 1; continue
        print(f"{label}: found")
        r = rec[0]
        if label == "SPF" and ("+all" in r or "?all" in r or "~all" not in r and "-all" not in r): print("  weak SPF ending (use ~all or -all)"); bad += 1
        if label == "SPF" and r.count("include:") > 9: print("  too many include lookups (limit is 10)"); bad += 1
        if label == "DMARC" and "p=none" in r: print("  DMARC policy is p=none (monitoring only)"); bad += 1
    for s in (opt("--dkim-selector") or "google,default,selector1,selector2,k1,mail").split(","):
        out, err = txt(f"{s}._domainkey.{d}")
        if out and "v=DKIM1" in out: print(f"DKIM selector {s}: found")
        elif out is not None and s == (opt("--dkim-selector") or "").split(",")[0]: print(f"DKIM selector {s}: missing"); bad += 1
elif opt("--templates"):
    print("# Email template check")
    for dd, _, fs in os.walk(opt("--templates")):
        for f in fs:
            if not f.endswith((".html", ".mjml", ".hbs", ".ejs", ".liquid", ".txt")): continue
            t = open(os.path.join(dd, f), encoding="utf-8", errors="ignore").read(); p = []
            if not re.search(r"unsubscribe|הסרה|ביטול הרשמה", t, re.I): p.append("no unsubscribe text")
            if f.endswith(".html") and "alt=" not in t and "<img" in t: p.append("images without alt")
            if re.search(r"[֐-׿]{3,}", t) and not re.search(r"dir=[\"']rtl|direction\s*:\s*rtl", t, re.I): p.append("Hebrew without rtl")
            if re.search(r"<script|onclick=", t, re.I): p.append("script or inline handlers (stripped by mail clients)")
            if re.search(r"https?://localhost|127\.0\.0\.1", t): p.append("localhost link")
            if f.endswith(".html") and not re.search(r"@media|max-width", t): p.append("no responsive rules")
            if p: bad += len(p); print(f"  {f}: " + "; ".join(p))
else: sys.exit(__doc__)
print(f"ISSUES: {bad}")
if unchecked: print("RESULT: NOT CHECKED, record as not checkable"); sys.exit(2)
sys.exit(1 if bad else 0)
