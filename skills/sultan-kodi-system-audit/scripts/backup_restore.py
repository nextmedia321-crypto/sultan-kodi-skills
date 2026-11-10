#!/usr/bin/env python3
"""Prove a backup can be restored. SQLite and archive/dump files. Never touches the original.
Usage: backup_restore.py --sqlite live.db [--backup backup.db]   (if no backup given: makes one with the SQLite backup API, restores to a temp copy, compares)
       backup_restore.py --archive backup.tar.gz|backup.zip     (lists, extracts to temp, checks it opens and is not empty)
       backup_restore.py --pgdump dump.sql|dump.custom           (only parses; a real restore needs a scratch Postgres, reported as not checked)"""
import sqlite3, sys, os, tempfile, shutil, tarfile, zipfile
a = sys.argv[1:]; opt = lambda n: a[a.index(n) + 1] if n in a and a.index(n) + 1 < len(a) else None
def counts(path):
    c = sqlite3.connect(f"file:{path}?mode=ro", uri=True); r = {}
    for (t,) in c.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'"): r[t] = c.execute(f'select count(*) from "{t}"').fetchone()[0]
    ok = c.execute("pragma integrity_check").fetchone()[0]; return r, ok
tmp = tempfile.mkdtemp(prefix="restore_")
try:
    if opt("--sqlite"):
        live = opt("--sqlite"); bk = opt("--backup"); made = False
        if not bk:
            bk = os.path.join(tmp, "backup.db"); s = sqlite3.connect(f"file:{live}?mode=ro", uri=True); d = sqlite3.connect(bk); s.backup(d); d.close(); s.close(); made = True
        rest = os.path.join(tmp, "restored.db"); shutil.copy(bk, rest)
        lc, lok = counts(live); rc, rok = counts(rest)
        print(f"# Restore test ({'backup made now by this script' if made else 'existing backup file'}: {bk})\nrestored integrity: {rok}")
        diff = {t: (lc.get(t), rc.get(t)) for t in set(lc) | set(rc) if lc.get(t) != rc.get(t)}
        for t in sorted(lc): print(f"  {t}: live {lc[t]} / restored {rc.get(t)}")
        if diff and not made: print("DIFFERENCES vs live (expected if the backup is older):", diff)
        if made: print("NOTE: this proves SQLite backup/restore works, not that the project's own scheduled backups exist. Check for a real backup job and its age.")
        sys.exit(0 if rok == "ok" and (made and not diff or not made) else 1)
    elif opt("--archive"):
        p = opt("--archive"); out = os.path.join(tmp, "x")
        if p.endswith((".tar.gz", ".tgz", ".tar")): tarfile.open(p).extractall(out, filter="data")
        elif p.endswith(".zip"): zipfile.ZipFile(p).extractall(out)
        else: sys.exit("unsupported archive type")
        n = sum(len(f) for _, _, f in os.walk(out)); sz = sum(os.path.getsize(os.path.join(d, x)) for d, _, f in os.walk(out) for x in f)
        print(f"# Archive restore test: extracted {n} files, {sz} bytes, age {(__import__('time').time() - os.path.getmtime(p)) / 86400:.1f} days")
        sys.exit(0 if n and sz else 1)
    elif opt("--pgdump"):
        p = opt("--pgdump"); head = open(p, "rb").read(200000)
        print(f"# Postgres dump parse only: {os.path.getsize(p)} bytes, {'plain SQL' if head[:5] != b'PGDMP' else 'custom format'}; CREATE TABLE statements: {head.count(b'CREATE TABLE')}")
        sc = opt("--scratch")
        if not sc:
            print("NOT CHECKED: a real restore needs a scratch Postgres database. Pass --scratch URL --i-confirm-not-production (an EMPTY throwaway database, never production)."); sys.exit(2)
        if "--i-confirm-not-production" not in a: sys.exit("Refusing: --scratch must be an empty throwaway database; pass --i-confirm-not-production")
        import subprocess
        n0 = subprocess.run(["psql", sc, "-At", "-c", "select count(*) from pg_tables where schemaname='public'"], capture_output=True, text=True)
        if n0.returncode or n0.stdout.strip() != "0": sys.exit("Refusing: scratch database is unreachable or not empty (" + (n0.stderr.strip()[:100] or n0.stdout.strip()) + ")")
        r = subprocess.run(["psql", sc, "-q", "-v", "ON_ERROR_STOP=1", "-f", p] if head[:5] != b"PGDMP" else ["pg_restore", "--no-owner", "-d", sc, p], capture_output=True, text=True)
        n1 = subprocess.run(["psql", sc, "-At", "-c", "select count(*) from pg_tables where schemaname='public'"], capture_output=True, text=True).stdout.strip()
        print(f"restore exit {r.returncode}; tables restored: {n1}" + (f"; error: {r.stderr.strip()[:200]}" if r.returncode else "")); sys.exit(0 if r.returncode == 0 and n1 != "0" else 1)
    else: sys.exit(__doc__)
finally: shutil.rmtree(tmp, ignore_errors=True)
