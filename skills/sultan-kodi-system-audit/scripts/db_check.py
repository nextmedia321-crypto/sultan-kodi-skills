#!/usr/bin/env python3
"""Read-only database health check. SQLite fully (stdlib). Postgres through psql if installed.
Usage: db_check.py --sqlite path.db
       db_check.py --postgres "$DATABASE_URL" --i-confirm-not-production
Postgres is only touched with the confirm flag, and only with SELECT queries. Use a copy or staging."""
import sqlite3, sys, os, shutil, subprocess
a = sys.argv[1:]
def opt(n): return a[a.index(n) + 1] if n in a and a.index(n) + 1 < len(a) else None
out = []
def p(*x): print(*x)

if opt("--sqlite"):
    path = opt("--sqlite")
    if not os.path.exists(path): sys.exit("no such file: " + path)
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True); c = con.cursor()
    p(f"# SQLite check: {path}")
    r = c.execute("PRAGMA integrity_check").fetchall(); p("integrity_check: " + ", ".join(x[0] for x in r))
    fk = c.execute("PRAGMA foreign_key_check").fetchall(); p(f"foreign_key violations: {len(fk)}")
    for x in fk[:10]: p("   ", x)
    tables = [t[0] for t in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    p(f"tables: {len(tables)}")
    for t in tables:
        cols = c.execute(f'PRAGMA table_info("{t}")').fetchall()
        n = c.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        pk = any(x[5] for x in cols); idx = c.execute(f'PRAGMA index_list("{t}")').fetchall()
        fks = c.execute(f'PRAGMA foreign_key_list("{t}")').fetchall()
        flags = []
        if not pk: flags.append("NO PRIMARY KEY")
        if n > 1000 and not idx: flags.append("large table without any index")
        for f in fks:
            covered = any(c.execute(f'PRAGMA index_info("{i[1]}")').fetchall()[0][2] == f[3] for i in idx if c.execute(f'PRAGMA index_info("{i[1]}")').fetchall()) if idx else False
            if not covered and n > 1000: flags.append(f"foreign key {f[3]} not indexed")
        for x in cols:
            if x[1].lower() in ("email", "user_id", "created_at") and False: pass
        nulls = [x[1] for x in cols if not x[3] and not x[5]]
        p(f"  {t}: {n} rows, {len(cols)} cols" + (("  <- " + "; ".join(flags)) if flags else ""))
    c.execute("PRAGMA page_count"); pc = c.fetchone()[0]; fl = c.execute("PRAGMA freelist_count").fetchone()[0]
    p(f"pages {pc}, free {fl}")
    p("\nNot checked by this script: application-level orphans without declared foreign keys, data meaning, backups. Inspect those by reading the models.")
elif opt("--postgres"):
    if "--i-confirm-not-production" not in a: sys.exit("Refusing: pass --i-confirm-not-production only after the user confirmed this is a copy or staging database.")
    if not shutil.which("psql"): sys.exit("psql is not installed, so the Postgres check could not run. Record this as not checkable.")
    q = {"tables without primary key": "select n.nspname||'.'||c.relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where c.relkind='r' and n.nspname not in ('pg_catalog','information_schema') and not exists (select 1 from pg_index i where i.indrelid=c.oid and i.indisprimary)",
         "foreign keys without index": "select conrelid::regclass||'.'||conname from pg_constraint c where contype='f' and not exists (select 1 from pg_index i where i.indrelid=c.conrelid and (i.indkey::int2[])[0:0] is not null and i.indkey[0]=c.conkey[1])",
         "tables without RLS (Supabase style)": "select schemaname||'.'||tablename from pg_tables where schemaname='public' and not rowsecurity",
         "largest tables": "select relname||' '||pg_size_pretty(pg_total_relation_size(oid)) from pg_class where relkind='r' and relnamespace='public'::regnamespace order by pg_total_relation_size(oid) desc limit 5"}
    for name, sql in q.items():
        r = subprocess.run(["psql", opt("--postgres"), "-At", "-c", sql], capture_output=True, text=True, timeout=120, env={**os.environ, "PGOPTIONS": "-c default_transaction_read_only=on"})
        p(f"\n== {name}"); p((r.stdout.strip() or "none")[:1500] if r.returncode == 0 else "error: " + r.stderr.strip()[:200])
else: sys.exit(__doc__)
